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

_DEBOUNCED_STATE = const(0x01)
_UNSTABLE_STATE = const(0x02)
_CHANGED_STATE = const(0x04)

_TICKS_PER_SEC = const(1000)


class Debouncer:
    """Debounce an input pin or an arbitrary predicate"""

    def __init__(self, io_or_predicate, interval=0.010):
        """Make an instance.
        :param DigitalInOut/function io_or_predicate: the DigitalIO or function to debounce
        :param int interval: bounce threshold in seconds (default is 0.010, i.e. 10 milliseconds)
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
        self._interval_ticks = interval * _TICKS_PER_SEC

    def _set_state(self, bits):
        self.state |= bits

    def _unset_state(self, bits):
        self.state &= ~bits

    def _toggle_state(self, bits):
        self.state ^= bits

    def _get_state(self, bits):
        return (self.state & bits) != 0

    def update(self):
        """Update the debouncer state. MUST be called frequently"""
        now_ticks = ticks_ms()
        self._unset_state(_CHANGED_STATE)
        current_state = self.function()
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
    def interval(self):
        """The debounce delay, in seconds"""
        return self._interval_ticks / _TICKS_PER_SEC

    @interval.setter
    def interval(self, new_interval_s):
        self._interval_ticks = new_interval_s * _TICKS_PER_SEC

    @property
    def value(self):
        """Return the current debounced value."""
        return self._get_state(_DEBOUNCED_STATE)

    @property
    def rose(self):
        """Return whether the debounced value went from low to high at the most recent update."""
        return self._get_state(_DEBOUNCED_STATE) and self._get_state(_CHANGED_STATE)

    @property
    def fell(self):
        """Return whether the debounced value went from high to low at the most recent update."""
        return (not self._get_state(_DEBOUNCED_STATE)) and self._get_state(
            _CHANGED_STATE
        )

    @property
    def last_duration(self):
        """Return the number of seconds the state was stable prior to the most recent transition."""
        return self._last_duration_ticks / _TICKS_PER_SEC

    @property
    def current_duration(self):
        """Return the number of seconds since the most recent transition."""
        return ticks_diff(ticks_ms(), self._state_changed_ticks) / _TICKS_PER_SEC


class Button(Debouncer):
    """Debounce counter"""

    def __init__(
        self,
        pin,
        short_duration_ms=200,
        long_duration_ms=500,
        active_down=True,
        **kwargs
    ):
        self.short_duration_ms = short_duration_ms
        self.long_duration_ms = long_duration_ms
        self.active_down = active_down
        self.last_change_ms = ticks_ms()
        self.short_counter = 0
        self.short_to_show = 0
        self.long_registered = False
        self.long_showed = False
        super().__init__(pin, **kwargs)

    def _pushed(self):
        return (self.active_down and super().fell) or (
            not self.active_down and super().rose
        )

    def _released(self):
        return (self.active_down and super().rose) or (
            not self.active_down and super().fell
        )

    def update(self):
        super().update()
        if self._pushed():
            self.last_change_ms = ticks_ms()
            self.short_counter = self.short_counter + 1
        elif self._released():
            self.last_change_ms = ticks_ms()
            if self.long_registered:
                self.long_registered = False
                self.long_showed = False
        else:
            duration = ticks_diff(ticks_ms(), self.last_change_ms)
            if (
                not self.long_registered
                and self.value != self.active_down
                and duration > self.long_duration_ms
            ):
                self.long_registered = True
                self.short_to_show = self.short_counter - 1
                self.short_counter = 0
            elif (
                self.short_counter > 0
                and self.value == self.active_down
                and duration > self.short_duration_ms
            ):
                self.short_to_show = self.short_counter
                self.short_counter = 0

    @property
    def short_count(self):
        """Return the number of short press"""
        ret = self.short_to_show
        self.short_to_show = 0
        return ret

    @property
    def long_press(self):
        """Return whether long press has occured"""
        if self.long_registered and not self.long_showed:
            self.long_showed = True
            return True
        return False
