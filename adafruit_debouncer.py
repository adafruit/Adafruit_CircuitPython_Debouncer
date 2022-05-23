# SPDX-FileCopyrightText: 2019 Dave Astels for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_debouncer`
====================================================

Debounces an arbitrary predicate function (typically created as a lambda) of 0
arguments.  Since a very common use is debouncing a digital input pin, the
initializer accepts a DigitalInOut object instead of a lambda.

* Author(s): Dave Astels

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
* Adafruit Ticks library:
  https://github.com/adafruit/Adafruit_CircuitPython_Ticks
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Debouncer.git"

from micropython import const
from adafruit_ticks import ticks_ms, ticks_diff

try:
    from typing import Callable, Optional, Union
    from circuitpython_typing.io import ROValueIO
except ImportError:
    pass

_DEBOUNCED_STATE: int = const(0x01)
_UNSTABLE_STATE: int = const(0x02)
_CHANGED_STATE: int = const(0x04)

_TICKS_PER_SEC: int = const(1000)


class Debouncer:
    """Debounce an input pin or an arbitrary predicate"""

    def __init__(
        self,
        io_or_predicate: Union[ROValueIO, Callable[[], bool]],
        interval: float = 0.010,
    ) -> None:
        """Make an instance.
        :param DigitalInOut/function io_or_predicate: the DigitalIO or
                                                      function that returns a boolean to debounce
        :param float interval: bounce threshold in seconds (default is 0.010, i.e. 10 milliseconds)
        """
        self.state = 0x00
        if hasattr(io_or_predicate, "value"):
            self.function = lambda: io_or_predicate.value
        else:
            self.function = io_or_predicate
        if self.function():
            self._set_state(_DEBOUNCED_STATE | _UNSTABLE_STATE)
        self._last_bounce_ticks = 0
        self._last_duration_ticks = 0
        self._state_changed_ticks = 0

        # Could use the .interval setter, but pylint prefers that we explicitly
        # set the real underlying attribute:
        self._interval_ticks = int(interval * _TICKS_PER_SEC)

    def _set_state(self, bits: int) -> None:
        self.state |= bits

    def _unset_state(self, bits: int) -> None:
        self.state &= ~bits

    def _toggle_state(self, bits: int) -> None:
        self.state ^= bits

    def _get_state(self, bits: int) -> bool:
        return (self.state & bits) != 0

    def update(self, new_state: Optional[int] = None) -> None:
        """Update the debouncer state. MUST be called frequently"""
        now_ticks = ticks_ms()
        self._unset_state(_CHANGED_STATE)
        if new_state is None:
            current_state = self.function()
        else:
            current_state = bool(new_state)
        if current_state != self._get_state(_UNSTABLE_STATE):
            self._last_bounce_ticks = now_ticks
            self._toggle_state(_UNSTABLE_STATE)
        else:
            if ticks_diff(now_ticks, self._last_bounce_ticks) >= self._interval_ticks:
                if current_state != self._get_state(_DEBOUNCED_STATE):
                    self._last_bounce_ticks = now_ticks
                    self._toggle_state(_DEBOUNCED_STATE)
                    self._set_state(_CHANGED_STATE)
                    self._last_duration_ticks = ticks_diff(
                        now_ticks, self._state_changed_ticks
                    )
                    self._state_changed_ticks = now_ticks

    @property
    def interval(self) -> float:
        """The debounce delay, in seconds"""
        return self._interval_ticks / _TICKS_PER_SEC

    @interval.setter
    def interval(self, new_interval_s: float) -> None:
        self._interval_ticks = new_interval_s * _TICKS_PER_SEC

    @property
    def value(self) -> bool:
        """Return the current debounced value."""
        return self._get_state(_DEBOUNCED_STATE)

    @property
    def rose(self) -> bool:
        """Return whether the debounced value went from low to high at the most recent update."""
        return self._get_state(_DEBOUNCED_STATE) and self._get_state(_CHANGED_STATE)

    @property
    def fell(self) -> bool:
        """Return whether the debounced value went from high to low at the most recent update."""
        return (not self._get_state(_DEBOUNCED_STATE)) and self._get_state(
            _CHANGED_STATE
        )

    @property
    def last_duration(self) -> float:
        """Return the number of seconds the state was stable prior to the most recent transition."""
        return self._last_duration_ticks / _TICKS_PER_SEC

    @property
    def current_duration(self) -> float:
        """Return the number of seconds since the most recent transition."""
        return ticks_diff(ticks_ms(), self._state_changed_ticks) / _TICKS_PER_SEC


class Button(Debouncer):
    """
    Debouncer for buttons. Reports ``pressed`` and ``released`` for the button state.
    Counts multiple short presses, allowing to detect double clicks, triple clicks, etc.
    Reports long presses separately. A long press can immediately follow multiple clicks,
    in which case the long click will be reported in the same update as the short clicks.

    :param DigitalInOut/function pin: the DigitalIO or function to debounce.
    :param int short_duration_ms: the maximum length of a short press in milliseconds.
    :param int long_duration_ms: the minimum length of a long press in milliseconds.
    :param bool value_when_pressed: the value of the predicate when the button is
                                    pressed. Defaults to False (for pull up buttons).
    """

    def __init__(
        self,
        pin: Union[ROValueIO, Callable[[], bool]],
        short_duration_ms: int = 200,
        long_duration_ms: int = 500,
        value_when_pressed: bool = False,
        **kwargs
    ) -> None:
        self.short_duration_ms = short_duration_ms
        self.long_duration_ms = long_duration_ms
        self.value_when_pressed = value_when_pressed
        self.last_change_ms = ticks_ms()
        self.short_counter = 0
        self.short_to_show = 0
        self.long_registered = False
        self.long_to_show = False
        super().__init__(pin, **kwargs)

    @property
    def pressed(self) -> bool:
        """Return whether the button was pressed or not at the last update."""
        return (self.value_when_pressed and self.rose) or (
            not self.value_when_pressed and self.fell
        )

    @property
    def released(self) -> bool:
        """Return whether the button was release or not at the last update."""
        return (self.value_when_pressed and self.fell) or (
            not self.value_when_pressed and self.rose
        )

    def update(self, new_state: Optional[int] = None) -> None:
        super().update(new_state)
        if self.pressed:
            self.last_change_ms = ticks_ms()
            self.short_counter = self.short_counter + 1
        elif self.released:
            self.last_change_ms = ticks_ms()
            if self.long_registered:
                self.long_registered = False
        else:
            duration = ticks_diff(ticks_ms(), self.last_change_ms)
            if (
                not self.long_registered
                and self.value == self.value_when_pressed
                and duration > self.long_duration_ms
            ):
                self.long_registered = True
                self.long_to_show = True
                self.short_to_show = self.short_counter - 1
                self.short_counter = 0
            elif (
                self.short_counter > 0
                and self.value != self.value_when_pressed
                and duration > self.short_duration_ms
            ):
                self.short_to_show = self.short_counter
                self.short_counter = 0
            else:
                self.long_to_show = False
                self.short_to_show = 0

    @property
    def short_count(self) -> int:
        """Return the number of short press if a series of short presses has
        ended at the last update."""
        return self.short_to_show

    @property
    def long_press(self) -> bool:
        """Return whether a long press has occured at the last update."""
        return self.long_to_show
