SPS/FUNK Emulator Scripts
=========================

.. contents:: Contents
   :local:
   :depth: 2

This guide lists the commands that run the Python emulator for the IPC/1 + SPC/1
image (:doc:`sps_funk_ipc1`) and shows what to expect. The emulator is a folder of
plain Python files, ``id7000_sps_emu``.

Requirements
------------

* Python 3.8 or later (written and tested with Python 3.12).
* Only the standard library is used, so there is nothing to install. ``terminal``
  is a file in the folder (``terminal.py``) and is not the PyPI package of that
  name: do not install anything for it.
* For the interactive front end: a terminal of at least 80 x 26 characters (120
  columns or more also show the side panel), and a UTF-8 locale for the Danish
  letters (otherwise use ``--ascii``). Python's ``curses`` module is part of the
  standard library on Linux and macOS. On Windows it is usually missing and
  ``pip install windows-curses`` supplies it; this was not tested.
* The emulator is pure Python and runs about one million 8080 instructions per
  second.

Files
-----

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Purpose
   * - ``sps_funk_image.bin``
     - The 16 KB ROM image (``SPS_1``-``5`` then ``FUNK_1``-``3``), loaded from the
       same folder
   * - ``cpu8080.py``
     - 8080 core
   * - ``machine.py``
     - ``Machine``: memory, both UARTs, timer, digital and analog I/O
   * - ``terminal.py``
     - Small ADM-style terminal (``Terminal``) that renders the console screen
   * - ``aux.py``
     - Host side of the aux link (``AuxHost``): framing, byte stuffing, CRC
   * - ``disasm.py``
     - 8080 disassembler used by the debugger
   * - ``asm8080.py``
     - 8080 assembler for your own processes
   * - ``interactive.py``
     - Curses front end
   * - ``demo_console.py``, ``demo_plc.py``, ``demo_fib.py``
     - Demo scripts
   * - ``examples/fib.asm``, ``fib.hex``, ``fib.bin``
     - The Fibonacci example process, as source and assembled

Quick start
-----------

.. code-block:: console

   cd id7000_sps_emu
   python3 interactive.py          # the interactive front end
   python3 demo_console.py         # or one of the scripts

Scripts can be started from another folder too, because the ROM is found next to
the code.

The demo scripts
----------------

demo_console.py
~~~~~~~~~~~~~~~

Boots the system, shows the menu, starts a process with ``P`` (priority 3,
address ``7000h``), presses ESC to return to the menu and enters an invalid
command.

.. code-block:: console

   python3 demo_console.py

.. code-block:: text

   === screen after boot ===
                        VELKOMMEN TIL IPC/1 OPERATIVSYSTEMET
                         VÆLG IMELLEM  FØLGENDE KOMMANDOER:
                             'C'- DIALOG  MED SPC/1
                             'D'- HOP TIL  DEBUGGER
                             'P'- OPSTART AF PROCES
   KOMMANDO :

The script then prints the screen after each step. The process it starts counts
at ``7F00h`` once per 5 timer ticks.

demo_plc.py
~~~~~~~~~~~

Talks to the system over the aux link, downloads a small PLC program, starts it,
toggles a digital input and reads an analog value.

.. code-block:: console

   python3 demo_plc.py

.. code-block:: text

   version (60h)    -> [(121, b'\x00'), (96, b'\x00\x0088.03.14\x00')]
   download         -> last block reply [(121, b'\x00'), (30, b'\x04\x00\x00')] | PLC_STATE = 1
   run (20h,1)      -> [(121, b'\x00'), (32, b'\x01\x00')] | PLC_STATE = 3
   relocated code   -> 21 55 5a 7e 21 d5 52 77 c9
   input 0 inactive -> output 0 = False   (port 20h=FF, port 10h=00)
   input 0 active   -> output 0 = True   (port 20h=FE, port 10h=01)
   analog table @77F0h (module 0, channels 0-7, ...): [128, 512, 896, 1408, ...]

The program copies input point 0 to output point 0. After the run command the
loader has rewritten the ``LXI H`` operands to the image addresses.

demo_fib.py
~~~~~~~~~~~

Assembles ``examples/fib.asm``, downloads it over the aux link, starts it with the
``P`` command and watches ``7100h``. It takes several seconds.

.. code-block:: console

   python3 demo_fib.py

.. code-block:: text

   value changes at 7100h (emulated seconds, text):
       0.01 s   '0000'
       0.17 s   '0001'
       2.17 s   '0002' (+2.00 s)
       3.17 s   '0003' (+1.00 s)
       4.17 s   '0005' (+1.00 s)
      ...
   clock-process pulses (OUT 0Ah) per second: 100 before, 100 with the Fibonacci process running

The ``0001`` appears twice in the sequence (0, 1, 1, 2), which is why 2.00 s pass
before the text changes to ``0002``. The last line shows that the process does not
disturb the OS clock.

The interactive front end
-------------------------

.. code-block:: console

   python3 interactive.py [--ascii] [--tick-hz N] [--watch ADDR]

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Option
     - Meaning
   * - ``--ascii``
     - Show the ROM's national characters as ``[ \ ] { | }`` instead of Æ Ø Å æ ø å
   * - ``--tick-hz N``
     - Timer ticks per second at speed x1 (default 500, which makes the OS clock count
       real seconds)
   * - ``--watch ADDR``
     - Show 8 bytes at this hex address in the panel, for example ``--watch 7100``
   * - ``--fixed N``
     - Run ``N`` instructions per screen update (used by the self-test)
   * - ``--selftest``
     - Run a scripted test without a terminal and exit

Everything you type goes to the operator console. Enter sends carriage return,
Backspace sends ``08h`` and Esc sends ``1Bh``. ``Ctrl-]`` is the prefix for the
emulator's own keys:

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - After ``Ctrl-]``
     - Action
   * - ``q``
     - Quit
   * - ``p`` ``s``
     - Pause or resume; change the speed (x0.25 to maximum)
   * - ``i``
     - Toggle a digital input point (prompts for 0-159)
   * - ``a``
     - Set an analog value (prompts for ``module channel value``, for example ``0 3 512``)
   * - ``l``
     - Download the demo program (output 0 follows input 0)
   * - ``L``
     - Download the code in a hex file (prompts for the path)
   * - ``r`` ``x``
     - Run or stop the PLC program
   * - ``v`` ``c``
     - Read the version string; send a raw aux command (prompts for ``code args``, in hex)
   * - ``b``
     - Break into the debugger
   * - ``R``
     - Restart the system (command ``3Ah``). This is the only way to stop an
       operator-started process
   * - ``d`` ``n`` ``h``
     - Show or hide the panel; switch Danish and raw characters; help

The panel shows step and tick counts, the PLC state, the digital input and output
ports, the analog values, a log of aux commands and, with ``--watch``, memory.

Walk-through 1: the operator menu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Start ``python3 interactive.py``. The menu appears after a moment.
2. Type ``C`` and Enter: the menu is redrawn and nothing else happens (the ``C``
   command is a stub in this image).
3. Type ``X`` and Enter: ``INDTASTNINGSFEJL !`` (input error) appears.
4. Type ``P`` and Enter, ``3`` and Enter, then a hex address and Enter to start a
   process there (see walk-through 3 for one that does something).

Walk-through 2: a PLC program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. ``Ctrl-]`` then ``l``: the demo program is downloaded over the aux link.
2. ``Ctrl-]`` then ``r``: the panel shows ``PLC RUN``.
3. ``Ctrl-]`` then ``i``, type ``0`` and Enter: digital input 0 becomes active and the
   panel shows output 0 on. Repeat to switch it off again.
4. ``Ctrl-]`` then ``a``, type ``0 1 700`` and Enter, to give module 0 channel 1 a
   value.
5. ``Ctrl-]`` then ``x`` stops the program. Stop it before downloading a new
   one: while it runs, the ROM refuses a download (status 1) and the front end
   shows ``download refused``.

Walk-through 3: the Fibonacci process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   python3 interactive.py --watch 7100

1. If a PLC program is running, stop it (``Ctrl-]`` then ``x``).
2. ``Ctrl-]`` then ``L`` and enter ``examples/fib.hex`` (relative to the folder in
   which you started the program). The code is placed at ``807Ch``.
3. At the console type ``P`` Enter, ``3`` Enter, ``807C`` Enter.
4. The panel line ``Watch 7100`` now shows the ASCII digits ``0000``, ``0001``,
   ``0001``, ``0002``, ``0003`` and so on, one per second. Press Esc to return to
   the menu; the process keeps running.

Priorities 1 to 3 work. A process at priority 4 or lower never runs, because the
PLC cycle (priority 4) never blocks.

To stop the process, restart the system with ``Ctrl-]`` then ``R``. IPC/1 has no call
that stops a single process, and a process that executes ``RET`` at its top level
does not end cleanly (see :doc:`sps_funk_ipc1`). Up to six processes can be
started this way; the seventh gets ``INGEN PROCESKONTROLBLOKKE LEDIGE``.

Walk-through 4: the debugger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ROM's ``D`` command calls a debugger ROM at ``F008h`` that is not in the image.
The front end intercepts that address (and ``F000h``) with a small monitor:

1. Type ``D`` and Enter, or press ``Ctrl-]`` then ``b`` at any time.
2. The monitor shows registers, the code at the program counter, the stack and a
   memory dump. Keys: ``s`` step, ``c`` continue (perform the ``RET`` the real
   debugger would do, so the ROM clears the screen and redraws the menu), ``g``
   go without the ``RET``, ``m`` dump memory (prompts for a hex address), ``b``
   toggle a breakpoint (prompts for a hex address), ``x`` quit the emulator.

The assembler
-------------

.. code-block:: console

   python3 asm8080.py examples/fib.asm -l -o fib.bin --hex fib.hex

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Option
     - Meaning
   * - ``-l``
     - Print a listing (address, bytes, source)
   * - ``-o FILE``
     - Write the binary
   * - ``--hex FILE``
     - Write the bytes as text, 16 per line (the format that ``Ctrl-]`` ``L`` reads)
   * - ``-D NAME=VALUE``
     - Override a constant, for example ``-D TICKS_PER_SEC=100``

The syntax is ``LABEL: MNEMONIC operands ; comment`` with the directives ``ORG``,
``EQU``, ``DB``, ``DW`` and ``DS``. Numbers can be written ``1234``, ``0x1F``,
``1FH``, ``101B`` or ``'A'``, and expressions may use ``+ - * /``, parentheses,
``$``, ``LOW()`` and ``HIGH()``.

To run your own process with the front end, assemble it at ``ORG 807CH`` (the
download puts the first code byte there), load the hex file with ``Ctrl-]`` ``L``
and start it with ``P`` at ``807C``. A process must wait on a semaphore
regularly; ``examples/fib.asm`` shows how.

Using the emulator from Python
------------------------------

Start Python in the ``id7000_sps_emu`` folder and type the examples.

The console
~~~~~~~~~~~

.. code-block:: python

   from machine import Machine
   from terminal import Terminal
   m = Machine()
   m.run(2_000_000)                     # boot
   t = Terminal(); t.feed(m.take())     # m.take() returns the console output
   print(t.render())                    # the screen, with Danish letters
   m.type('P\r')                        # type on the console

The aux link, digital and analog I/O
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from machine import Machine, attach_analog
   from aux import AuxHost
   m = Machine(); adc = attach_analog(m); m.run(2_000_000)
   h = AuxHost(m); h.connect()          # the first frame only starts the link
   print(h.command(0x60))               # version string reply
   m.set_din(3, True)                   # digital input 3 active (port 20h bit 3 low)
   m.run(200000)
   print(m.dout(0))                     # digital output 0
   adc[0].values[2] = 512               # module 0, channel 2

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Call
     - Meaning
   * - ``Machine()``
     - Builds the machine. ``m.TICK`` is the number of instructions per timer tick
       (4000 by default).
   * - ``m.run(n)``, ``m.type(text)``, ``m.take()``
     - Run ``n`` instructions, type on the console, return the console output.
   * - ``m.set_din(point, active=True)``, ``m.dout(point)``
     - Digital input and output points.
   * - ``attach_analog(m)``
     - Adds six analog modules. ``adc[i].values[ch]`` sets a 10-bit value.
   * - ``AuxHost(m)``
     - ``connect()``, ``command(code, *args)``. Commands are listed in
       :doc:`sps_funk_ipc1`.
   * - ``Terminal()``
     - ``feed(bytes)`` and ``render(national=True)``.

The self-test
-------------

.. code-block:: console

   python3 interactive.py --selftest

Runs nine scripted checks on a fake screen: boot and menu, console keyboard, aux
download and run, analog value, version string, the ``D`` debugger entry and
return, pause and help, and the Fibonacci process loaded with ``L`` and started
with ``P``. It prints one ``ok`` line per check and takes a few minutes.

Troubleshooting
---------------

``Terminal too small: need 80x26``
   Enlarge the terminal window.

Danish letters show as ``[ \ ]`` or as question marks
   Use a UTF-8 locale, or run with ``--ascii`` to see the raw characters.

``Ctrl-]`` does nothing or closes the session
   Some terminals and ssh/telnet clients take ``Ctrl-]`` for themselves. Change that
   setting, or use the Python API instead.

The Esc key feels slow
   Curses waits a moment (25 ms here) to tell Esc from an arrow-key sequence.

``ModuleNotFoundError: No module named 'terminal'``
   Run the script from the ``id7000_sps_emu`` folder or keep the files together.
   Do not ``pip install terminal``.

``download refused: the PLC program is running``
   The ROM refuses a download in state 3. Stop the program first (``Ctrl-]`` ``x``).
   Commands are also only answered after the first frame (``connect()``).

The Fibonacci numbers change every five seconds
   The ticks per second are not 500. Run with ``--tick-hz 500`` or change
   ``TICKS_PER_SEC`` in ``examples/fib.asm`` and reassemble.

Command ``0Eh`` never answers
   Known: no reply in any test, and the command interpreter stays blocked afterwards.

A process at priority 4 or lower does nothing
   Use priority 1 to 3.

Limits
------

* The tick rate, the analog scaling and the RAM size are inferred or assumed.
* The interrupt enable register ``FEh`` is not modelled: interrupts are raised
  whenever a device has work.
* The debugger is a built-in monitor, not the original ROM.
