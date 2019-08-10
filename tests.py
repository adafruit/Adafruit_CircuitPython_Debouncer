import sys
import time
import adafruit_debouncer


def _true():
    return True
def _false():
    return False


def assertEqual(a, b):
    assert a == b, "Want %r, got %r" % (a, b)


def test_simple():
    db = adafruit_debouncer.Debouncer(_false)
    assertEqual(db.value, False)

    db.function = _true
    db.update()
    assertEqual(db.value, False)
    time.sleep(0.02)
    db.update()
    assertEqual(db.value, True)
    assertEqual(db.rose, True)
    assertEqual(db.fell, False)

    db.function = _false
    db.update()
    assertEqual(db.value, True)
    assertEqual(db.fell, False)
    assertEqual(db.rose, False)
    time.sleep(0.02)
    db.update()
    assertEqual(db.value, False)
    assertEqual(db.rose, False)
    assertEqual(db.fell, True)


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
    db = adafruit_debouncer.Debouncer(_false, interval=0.01)
    db.update()

    # set the interval to a longer time, sleep for a time between
    # the two interval settings, and assert that the value hasn't changed.

    db.function = _true
    db.interval = 0.2
    db.update()
    time.sleep(0.11)
    db.update()

    assertEqual(db.value, False)
    assertEqual(db.rose, False)
    assertEqual(db.fell, False)

    time.sleep(0.11)
    db.update()
    assertEqual(db.value, True)
    assertEqual(db.rose, True)
    assertEqual(db.fell, False)


def run():
    passes = 0
    fails = 0
    for name, test in locals().items():
        if name.startswith('test_') and callable(test):
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
        print(r"""
 ________
< YATTA! >
 --------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||""")


if __name__ == '__main__':
    run()
