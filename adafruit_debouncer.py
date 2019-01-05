# The MIT License (MIT)
#
# Copyright (c) 2019 Dave Astels for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_debouncer`
====================================================

Debounces an arbitrary predicate function (typically created as a lambda) of 0 arguments.
Since a very common use is debouncing a digital input pin, the initializer accepts a pin number
instead of a lambda.

* Author(s): Dave Astels

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Debouncer.git"

import time
import digitalio
import microcontroller

class Debouncer(object):
    """Debounce an input pin or an arbitrary predicate"""

    DEBOUNCED_STATE = 0x01
    UNSTABLE_STATE = 0x02
    CHANGED_STATE = 0x04


    def __init__(self, pin_or_predicate, mode=None, interval=0.010):
        """Make am instance.
           :param int/function pin_or_predicate: the pin (from board) to debounce
           :param int mode: digitalio.Pull.UP or .DOWN (default is no pull up/down)
           :param int interval: bounce threshold in seconds (default is 0.010, i.e. 10 milliseconds)
        """
        self.state = 0x00
        if isinstance(pin_or_predicate, microcontroller.Pin):
            pin = digitalio.DigitalInOut(pin_or_predicate)
            pin.direction = digitalio.Direction.INPUT
            if mode is not None:
                pin.pull = mode
            self.function = lambda: pin.value
        else:
            self.function = pin_or_predicate
        if self.function():
            self.__set_state(Debouncer.DEBOUNCED_STATE | Debouncer.UNSTABLE_STATE)
        self.previous_time = 0
        if interval is None:
            self.interval = 0.010
        else:
            self.interval = interval


    def __set_state(self, bits):
        self.state |= bits


    def __unset_state(self, bits):
        self.state &= ~bits


    def __toggle_state(self, bits):
        self.state ^= bits


    def __get_state(self, bits):
        return (self.state & bits) != 0


    def update(self):
        """Update the debouncer state. MUST be called frequently"""
        now = time.monotonic()
        self.__unset_state(Debouncer.CHANGED_STATE)
        current_state = self.function()
        if current_state != self.__get_state(Debouncer.UNSTABLE_STATE):
            self.previous_time = now
            self.__toggle_state(Debouncer.UNSTABLE_STATE)
        else:
            if now - self.previous_time >= self.interval:
                if current_state != self.__get_state(Debouncer.DEBOUNCED_STATE):
                    self.previous_time = now
                    self.__toggle_state(Debouncer.DEBOUNCED_STATE)
                    self.__set_state(Debouncer.CHANGED_STATE)


    @property
    def value(self):
        """Return the current debounced value."""
        return self.__get_state(Debouncer.DEBOUNCED_STATE)


    @property
    def rose(self):
        """Return whether the debounced value went from low to high at the most recent update."""
        return self.__get_state(self.DEBOUNCED_STATE) and self.__get_state(self.CHANGED_STATE)


    @property
    def fell(self):
        """Return whether the debounced value went from high to low at the most recent update."""
        return (not self.__get_state(self.DEBOUNCED_STATE)) and self.__get_state(self.CHANGED_STATE)
