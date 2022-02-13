# SPDX-FileCopyrightText: 2022 david gauchard
# SPDX-License-Identifier: MIT

import board
import digitalio
from adafruit_debouncer import Button

# This example shows how to count short clicks or detect a long press

pin = digitalio.DigitalInOut(board.D12)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP
switch = Button(pin)

while True:
    switch.update()
    if switch.long_press:
        print("long")
    count = switch.short_count
    if count != 0:
        print("count=", count)
