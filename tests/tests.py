# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
How to use this test file:

Copy adafruit_debouncer's dependencies to lib/ on your circuitpython device.
Copy adafruit_debouncer.py to / on the device
Copy this tests.py file to /main.py on the device
Connect to the serial terminal (e.g. sudo screen /dev/ttyACM0 115200)
Press Ctrl-D, if needed to start the tests running
"""
import sys
import time
import adafruit_debouncer


def _true():
    return True


def _false():
    return False


def assertEqual(a, b):
    assert a == b, "Want %r, got %r" % (a, b)


def test_back_and_forth():
    # Start false
    db = adafruit_debouncer.Debouncer(_false)
    assertEqual(db.value, False)

    # Set the raw state to true, update, and make sure the debounced
    # state has not changed yet:
    db.function = _true
    db.update()
    assertEqual(db.value, False)
    assert not db.last_duration, "There was no previous interval??"

    # Sleep longer than the debounce interval, so state can change:
    time.sleep(0.02)
    db.update()
    assert db.last_duration  # is actually duration between powerup and now
    assertEqual(db.value, True)
    assertEqual(db.rose, True)
    assertEqual(db.fell, False)
    # Duration since last change has only been long enough to run these
    # asserts, which should be well under 1/10 second
    assert db.current_duration < 0.1, "Unit error? %d" % db.current_duration

    # Set raw state back to false, make sure it's not instantly reflected,
    # then wait and make sure it IS reflected after the interval has passed.
    db.function = _false
    db.update()
    assertEqual(db.value, True)
    assertEqual(db.fell, False)
    assertEqual(db.rose, False)
    time.sleep(0.02)
    assert 0.019 < db.current_duration <= 1, (
        "Unit error? sleep .02 -> duration %d" % db.current_duration
    )
    db.update()
    assertEqual(db.value, False)
    assertEqual(db.rose, False)
    assertEqual(db.fell, True)

    assert 0 < db.current_duration <= 0.1, (
        "Unit error? time to run asserts %d" % db.current_duration
    )
    assert 0 < db.last_duration < 0.1, (
        "Unit error? Last dur should be ~.02, is %d" % db.last_duration
    )


def test_interval_is_the_same():
    db = adafruit_debouncer.Debouncer(_false, interval=0.25)
    assertEqual(db.value, False)
    db.update()
    db.function = _true
    db.update()

    time.sleep(0.1)  # longer than default interval
    db.update()
    assertEqual(db.value, False)

    time.sleep(0.2)  # 0.1 + 0.2 > 0.25
    db.update()
    assertEqual(db.value, True)
    assertEqual(db.rose, True)
    assertEqual(db.interval, 0.25)


def test_setting_interval():
    # Check that setting the interval does change the time the debouncer waits
    db = adafruit_debouncer.Debouncer(_false, interval=0.01)
    db.update()

    # set the interval to a longer time, sleep for a time between
    # the two interval settings, and assert that the value hasn't changed.

    db.function = _true
    db.interval = 0.2
    db.update()
    assert db.interval - 0.2 < 0.00001, "interval is not consistent"
    time.sleep(0.11)
    db.update()

    assertEqual(db.value, False)
    assertEqual(db.rose, False)
    assertEqual(db.fell, False)

    # and then once the whole time has passed make sure it did change
    time.sleep(0.11)
    db.update()
    assertEqual(db.value, True)
    assertEqual(db.rose, True)
    assertEqual(db.fell, False)


def run():
    passes = 0
    fails = 0
    for name, test in locals().items():
        if name.startswith("test_") and callable(test):
            try:
                print()
                print(name)
                test()
                print("PASS")
                passes += 1
            except Exception as e:
                sys.print_exception(e)
                print("FAIL")
                fails += 1

    print(passes, "passed,", fails, "failed")
    if passes and not fails:
        print(
            r"""
 ________
< YATTA! >
 --------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||"""
        )


if __name__ == "__main__":
    run()
