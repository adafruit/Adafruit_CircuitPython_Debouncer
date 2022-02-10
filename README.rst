Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-debouncer/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/debouncer/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_Debouncer/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_Debouncer/actions/
    :alt: Build Status

Debounces an arbitrary predicate function (typically created as a lambda) of 0 arguments.
The constructor also accepts a digital pin as a convienence.



Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Adafruit Ticks <https://github.com/adafruit/Adafruit_CircuitPython_Ticks>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

.. code-block:: python

    import board
    import digitalio
    from adafruit_debouncer import Debouncer

    pin = digitalio.DigitalInOut(board.D12)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    switch = Debouncer(pin)

    while True:
        switch.update()
        if switch.fell:
            print('Just pressed')
        if switch.rose:
            print('Just released')
        if switch.value:
            print('not pressed')
        else:
            print('pressed')


Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/debouncer/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_debouncer/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
