Board 5 Image: Running the Emulator Scripts
===========================================

.. contents:: Contents
   :local:
   :depth: 2

This guide lists the commands that run the Python emulator for the board 5 image
(:doc:`board5_terminal_concentrator`) and shows what to expect. The emulator is a
folder of plain Python files, ``id7000_emu``.

Requirements
------------

* Python 3.8 or later. The scripts were written and run with Python 3.12.
* Nothing else: only the standard library is used, so there is nothing to install.
  The ``cpu8080``, ``machine``, ``sync`` and ``printer`` modules are files in the
  folder, not packages from PyPI.
* About one to two seconds of CPU time to boot. The emulator is pure Python and
  runs about one million 8080 instructions per second.

Files
-----

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - File
     - Purpose
   * - ``board5_eproms_0_to_6.bin``
     - The ROM image, loaded from the same folder
   * - ``cpu8080.py``
     - 8080 core
   * - ``machine.py``
     - Memory map, 12 channel UARTs, timer, ``Machine`` class
   * - ``sync.py``
     - Synchronous 8251 and the stub Cyber host (``CyberHost``)
   * - ``printer.py``
     - 8255 printer stub and helpers that build print data
   * - ``demo.py``
     - Console and local commands
   * - ``demo_cyber.py``
     - Cyber link conversation
   * - ``demo_printer.py``
     - Printer tests and a rendered report

Quick start
-----------

.. code-block:: console

   cd id7000_emu
   python3 demo.py

The scripts can also be started from another folder, for example
``python3 id7000_emu/demo.py``, because the ROM is found next to the code.

The demo scripts
----------------

demo.py
~~~~~~~

Boots the ROM, types four lines on channel 0 and prints each reply.

.. code-block:: console

   python3 demo.py

.. code-block:: text

   ':STATUS'    -> |[ASCII NORMAL MODE (95 CH-SET)]|[NO CR/LF AT LINES WITH 80 CHARS]|[HP-CASSETTE MODE OFF]|[PAPER TAPE MODE OFF]|
   ':HP,ON'     -> |[HP-CASSETTE MODE ON]|
   ':FOO'       -> |[ILLEGAL COMMAND]|
   'HELLO'      -> |[CYBER LINK DOWN]|

``|`` stands for a carriage return and line feed. A line that starts with ``:`` is
a local command; any other line goes to the Cyber host and is answered with
``[CYBER LINK DOWN]`` because no host is connected.

demo_cyber.py
~~~~~~~~~~~~~

Connects the stub Cyber host to the synchronous 8251, brings the link up, sends a
typed line to the host and sends text back.

.. code-block:: console

   python3 demo_cyber.py

.. code-block:: text

   1 poll (idle)      -> {'addr': 112, 'dev': 96, 'ctl': 24, 'data': b'', 'lrc': 245}
     console: |[CYBER LINK ESTABLISHED]|
   2 user typed HELLO; console:
   3 poll             -> {'addr': 112, 'dev': 97, 'ctl': 19, 'data': b'HELLO\x1bB', 'lrc': 228}
   4 host says text   -> {'addr': 112, 'dev': 96, 'ctl': 6, 'data': b'', 'lrc': 235}
     console: HI FROM CYBER||
   5 :STATUS -> |[ASCII NORMAL MODE (95 CH-SET)]|[NO CR/LF AT LINES WITH 80 CHARS]|...

``ctl`` 24 (``18h``) is the "nothing to send" reply, 19 (``13h``) carries the typed
line, and 6 is an acknowledgement.

demo_printer.py
~~~~~~~~~~~~~~~

Starts printing from the Cyber host, checks the printer data byte for byte, prints
a rendered report and tests the busy and hold handshake.

.. code-block:: console

   python3 demo_printer.py

.. code-block:: text

   8255 mode word seen by printer: 0x82 | PC after init: 0b10010000
   PASS single space
   PASS A = form feed
   PASS J = skip a line
   PASS ESC # = 3 spaces
   PASS ESC J = 10 zeros

   busy_reads=4 : b'\n\rSLOW\r\n'
   busy+hold    : printed b'' | host ACK ctl = 0x6
   busy cleared, hold still on: b''
   hold cleared : b'\n\rHELD\r\n'

The full output also contains a two-page rendered report.

Using the emulator from Python
------------------------------

Start Python in the ``id7000_emu`` folder (``python3``) and type the examples
below. Each one builds on its own ``Machine``.

The console
~~~~~~~~~~~

.. code-block:: python

   from machine import Machine
   m = Machine()
   m.boot()                          # self-test, banner, idle loop
   m.type(':STATUS\r')               # keys on channel 0 (use ch=n for another channel)
   m.run(400000)                     # let the slow transmitter finish
   print(m.take_tx())                # bytes sent on channel 0 (NUL padding included)

The Cyber host
~~~~~~~~~~~~~~

.. code-block:: python

   from machine import Machine
   from sync import Sync8251, CyberHost, attach
   m = Machine(); s = Sync8251(); attach(m, s); m.boot()
   host = CyberHost(m, s)
   print(host.poll())                # idle poll: brings the link up
   m.type('HELLO\r'); m.run(500000)  # a line for the host
   print(host.poll()['data'])        # b'HELLO\x1bB'
   host.say(0, b'HI FROM CYBER\r\n') # text for channel 0 (ESC B trailer added)
   print(m.take_tx())

The printer
~~~~~~~~~~~

.. code-block:: python

   from machine import Machine
   from sync import Sync8251, CyberHost, attach
   from printer import Printer, attach_printer, print_via_host, tab, zeros
   m = Machine(); s = Sync8251(); attach(m, s)
   p = attach_printer(m, Printer()); m.boot()
   host = CyberHost(m, s); host.poll()
   print_via_host(host, b'TOTAL' + tab(5) + b'|' + zeros(6), cc='J')
   m.run(400000)
   print(p.raw)                      # bytes the printer received
   print(p.text())                   # CR, LF and FF applied

``cc`` is the carriage-control character: a space (and any other character) gives
a line feed and carriage return, ``A`` a form feed and ``J`` an extra line feed.

Reference
---------

.. list-table::
   :header-rows: 1
   :widths: 36 64

   * - Call
     - Meaning
   * - ``Machine(trace_io=False)``
     - Builds the machine. ``trace_io=True`` records ``IN``/``OUT`` in ``m.bus.iolog``.
   * - ``m.boot()``
     - Runs about 1.4 million steps: self-test, banner, idle loop.
   * - ``m.run(n)``
     - Runs ``n`` instructions and raises the timer tick every ``m.TICK`` steps
       (default 2500).
   * - ``m.type(text, ch=0, gap=40000)``
     - Types each character on channel ``ch`` and runs ``gap`` steps after it.
   * - ``m.take_tx(ch=0)``
     - Returns and clears the bytes sent on channel ``ch``.
   * - ``CyberHost.poll(channel=0, dev=0x60)``
     - Sends a poll and returns the reply as a dictionary, or ``None``.
   * - ``CyberHost.say(channel, text, ctl=0x11, end=b'\x1bB')``
     - Sends data to a user. ``end=b'\x1b '`` sends it to the printer instead.
   * - ``CyberHost.exchange(addr, dev, ctl, data=b'')``
     - Sends any frame (``addr`` is ``70h`` plus the channel).
   * - ``Printer(busy_reads=0, capture_on='fall')``
     - Printer model. Attributes: ``raw``, ``hold``, ``force_busy``; methods
       ``text()`` and ``pages()``.
   * - ``print_via_host(host, text, cc=' ', channel=0, eol=b'\r\n')``
     - Sends one block to the printer (``ctl`` ``12h``, ``ESC space`` trailer).

Configuration
-------------

* ``ID7000_BOARD5_ROM`` is an environment variable that points to a different ROM
  file: ``ID7000_BOARD5_ROM=/path/to/rom.bin python3 demo.py``.
* ``m.TICK`` changes the number of instructions between timer ticks.

Troubleshooting
---------------

``ModuleNotFoundError: No module named 'machine'``
   Run the script from the ``id7000_emu`` folder or keep the files together; the
   modules are local files.

``FileNotFoundError`` for the ROM
   ``board5_eproms_0_to_6.bin`` must be next to ``machine.py``, or set
   ``ID7000_BOARD5_ROM``.

``BrokenPipeError`` when piping the output into ``head``
   Harmless: the reader closed the pipe early.

Replies are cut off or empty
   The ROM transmits slowly. Run more steps (for example ``m.run(400000)``) before
   calling ``take_tx()``.

The first Cyber reply is ``[CYBER LINK DOWN]``
   Send one poll first. ``[CYBER LINK ESTABLISHED]`` appears on the console when
   the first frame arrives.

Limits
------

* There is no interactive front end for this image; use the scripts or a Python
  session.
* The 8255 and the timer period are inferred. The interrupt enable register
  ``FEh`` is not modelled, so interrupts are raised whenever a device has work.
