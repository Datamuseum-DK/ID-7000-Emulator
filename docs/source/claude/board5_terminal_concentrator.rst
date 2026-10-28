ID-7000 Board 5 ROM: Terminal Concentrator (200UT/SIM)
======================================================

.. contents:: Contents
   :local:
   :depth: 2

.. note::

   This document describes the firmware image ``board5_eproms_0_to_6.bin``
   (seven 1 KB EPROMs, ``0000h``-``1BFFh``). Everything is *inferred* from the
   firmware and from behaviour observed in a Python emulator. Nothing has been
   checked against hardware manuals or schematics. The one exception is the
   statement that ports ``FEh`` and ``FFh`` belong to an interrupt and timer
   module, which was supplied with the project. Statements are marked as
   *inferred* or *unverified* where that matters. How to run the emulator is
   described in :doc:`board5_usage`.

Overview
--------

The input was a single file, ``board5_eproms_0_to_6.bin``, containing the
contents of seven 1 KB EPROMs (numbered 0 to 6). The work proceeded in five
steps:

1. Identify the CPU and disassemble the image.
2. Write an 8080 core and a first memory/I/O map.
3. Trace the boot path.
4. Find where user input is handled and trace a full command line.
5. Trace the "Cyber link" routines and build a stub host for them.

Summary of findings
~~~~~~~~~~~~~~~~~~~

* The CPU is an **Intel 8080** (no Z80 or 8085-specific opcodes found).
* The firmware is a small **preemptive multitasking** terminal concentrator /
  terminal emulator. The banner reads
  ``ID-7000 *READY* (200UT/SIM) VERSION 01.02.83``.
* It serves **12 asynchronous user channels** (8251 USARTs at ports
  ``60h``-``77h``) and one **synchronous line** (8251 at ``A0h``/``A1h``)
  to a CDC Cyber mainframe, using a bisync-style polled protocol.
* Local commands start with a colon (``:STATUS``). Any other line is queued
  for the Cyber host.
* The self-test (ROM checksum plus RAM test) passes in the emulator, and the
  firmware boots to an idle loop and responds to typed input and to host
  frames.
* Ports ``FEh`` and ``FFh`` are the **interrupt and timer module**: ``FEh``
  is an interrupt enable register in which bit *n* enables the source of
  ``RST n``, and a read of ``FFh`` acknowledges the timer tick.
* Printing is started by the Cyber host, not from the terminal (see
  `Printing`_).

The ROM image
-------------

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - File
     - ``board5_eproms_0_to_6.bin``
   * - Size
     - 7168 bytes (7 x 1 KB EPROMs)
   * - Load address
     - ``0000h``-``1BFFh``
   * - Padding
     - ``76h`` (HLT) fills unused space; everything above about ``1900h``
       is padding
   * - Checksum
     - Byte at ``1A30h`` (``20h``) equals the 8-bit sum of
       ``0000h``-``1A2Fh``

Evidence for the 8080:

* ``F3`` (DI) / ``C3`` (JMP) at the reset vector, ``DB``/``D3`` for IN/OUT.
* No CB/ED/DD/FD prefixes and no DJNZ/JR, so not a Z80.
* No RIM/SIM, so nothing 8085-specific.

Memory map (inferred)
---------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Range
     - Contents
   * - ``0000h``-``1BFFh``
     - ROM (EPROMs 0-6)
   * - ``4000h``-``BFFFh``
     - RAM. The power-on RAM test exercises exactly this range.
   * - ``4000h``-``42xxh``
     - Task/scheduler data, timer counters, channel tables
   * - ``41F9h``
     - 44-byte block copied from ROM ``1106h`` at start-up
   * - ``A2xxh``-``A3xxh``
     - Cyber-link state, per-channel records, buffers

I/O map (inferred)
------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Ports
     - Device
   * - ``50h``-``53h``
     - 8255 PPI (port A data out, port B status in, PC7 strobe, PC4
       set/reset). Looks like a parallel printer port. *Unverified.*
   * - ``60h``-``77h``
     - 12 x 8251 USART. Data on the even port, control/status on the odd port.
   * - ``A0h``/``A1h``
     - 8251 in synchronous mode (sync character ``16h`` = SYN). The Cyber
       link.
   * - ``FEh``
     - Interrupt module: enable register, bit *n* enabling the source of
       ``RST n`` (see the next section). ``7Eh`` is written at the end of boot.
   * - ``FFh``
     - Timer module: read in the RST 3 timer handler to acknowledge the tick.

The 8251 identification comes from the initialisation sequences. For the
async channels the byte sequence ``03h, 53h, FAh, 25h`` is, on an 8251:

* ``03h`` - dummy write to flush the mode/command state
* ``53h`` - command with the internal-reset bit set
* ``FAh`` - mode byte (7 data bits, even parity, 2 stop bits, x16 clock)
* ``25h`` - command: enable transmit and receive, RTS

For the sync line the sequence ``03h, 53h, 98h, 16h, 96h`` is: reset, a
synchronous-mode byte (7 data bits, parity), the sync character ``16h`` (SYN),
and a command with enter-hunt, receive-enable and DTR.

Status bits used by the firmware: bit 0 = TxRDY, bit 1 = RxRDY.

Interrupt and timer module (``FEh``/``FFh``)
--------------------------------------------

The two ports are the board's interrupt and timer module (information supplied
with the project). The firmware accesses them in only five places:

.. list-table::
   :header-rows: 1
   :widths: 10 14 34 42

   * - Port
     - Address
     - Access
     - Effect
   * - ``FEh``
     - ``0DA3h``
     - ``OUT 00h`` at the start of boot
     - All interrupt sources off while the devices are set up.
   * - ``FEh``
     - ``107Eh``
     - ``OUT 7Eh`` at the end of initialisation
     - Bits 1-6 set: the sources for ``RST 1`` to ``RST 6``.
   * - ``FEh``
     - ``0052h``
     - ``IN``, ``ORI 04h``, ``OUT`` in the sync receive reset
     - Bit 2 set: the source for ``RST 2`` (sync receive).
   * - ``FEh``
     - ``01FFh``
     - ``IN``, ``ORI 10h``, ``OUT`` when a transmit starts
     - Bit 4 set: the source for ``RST 4`` (sync transmit).
   * - ``FFh``
     - ``0762h``
     - ``IN`` at the top of the timer ISR
     - Acknowledges the tick. The value read is not used.

What this suggests (inferred):

* ``FEh`` is an **interrupt enable (mask) register** and can be read back,
  because the code uses read-modify-write. Bit *n* belongs to ``RST n``:
  bit 2 is the sync receiver (``RST 2``), bit 3 the timer (``RST 3``), bit 4 the
  sync transmitter (``RST 4``) and bit 6 the async receivers (``RST 6``). Bit 0
  is never set.
* The firmware never clears a bit again. The 8251 transmit interrupt is stopped
  at the chip (the command byte switches the transmitter off), not in ``FEh``.
  Whether the module clears an enable bit by itself when an interrupt is taken
  is not known. The repeated ``ORI`` in the receive reset and in the transmit
  start would also fit that.
* ``FFh`` belongs to the timer. The ROM never writes it, so the tick period is
  either fixed in hardware or set outside this ROM. It is not known.

Interrupt vectors
-----------------

.. list-table::
   :header-rows: 1
   :widths: 12 15 73

   * - RST
     - Address
     - Behaviour
   * - 0 / reset
     - ``0000h``
     - ``DI; JMP 0DA0h`` (self-test and boot)
   * - 1
     - ``0008h``
     - ``EI; RET`` (unused)
   * - 2
     - ``0010h``
     - ``JMP 005Bh``: sync line **receive**
   * - 3
     - ``0018h``
     - ``JMP 0760h``: **timer tick** (also drives task time-slicing and the
       link-lost timeout)
   * - 4
     - ``0020h``
     - ``JMP 020Bh``: sync line **transmit**
   * - 5
     - ``0028h``
     - ``EI; RET`` (unused)
   * - 6
     - ``0030h``
     - ``JMP 0880h``: async **receive** (any of the 12 channels)
   * - 7
     - ``0038h``
     - ``JMP 0DA0h`` (restarts the system)

Boot sequence
-------------

1. ``0000h``: ``DI``, jump to ``0DA0h``.
2. ``0DA0h``: write ``0`` to port ``FEh`` (all interrupt sources off), send
   the 8251 reset sequence to port ``61h``.
3. **ROM checksum.** Sum ``0000h``-``1A2Fh`` into C and compare against the
   byte at ``1A30h``. The emulator confirms ``20h == 20h``.
4. **RAM test.** Fill ``4000h``-``BFFFh`` with an address-derived pattern and
   verify; repeat with the complement; verify again. On failure the code
   prints ``** ERROR IN RAM MEMORY DETECTED IN HEX AREA $x000-y000`` (or
   ``** ERROR IN PROM MEMORY DETECTED **`` for a checksum failure) through
   the 8251 on port ``60h``/``61h``.
5. **Peripheral initialisation** (from ``1000h``): sync 8251 at ``A1h``
   (``03h, 53h, 98h, 16h, 96h``), 8255 control word ``82h`` plus bit
   set/reset ``08h``, ``09h``, ``0Fh``, then the 12 async channels
   (``61h``, ``63h`` ... ``77h``).
6. **Data initialisation.** Copy 44 bytes from ROM ``1106h`` to RAM
   ``41F9h``; build the task and channel tables; set the link-down flag
   (``429Dh`` = 1).
7. Write ``7Eh`` to port ``FEh`` (enables the sources for ``RST 1``-``RST 6``),
   ``EI``, and fall into the
   idle loop at ``0869h`` (``NOP; HLT; JMP 0869h``). From then on everything
   is interrupt-driven.

.. code-block:: text

   I/O trace of the boot (emulator, ports only):

   OUT FE  00
   OUT 61  03 53 FA 25      IN 60
   ... RAM test (about 800,000 steps) ...
   OUT A1  03 53 98 16 96
   OUT 53  82 08 09 0F
   OUT 61,63,...,77  03 53 FA 25 (each followed by an IN of the data port)
   OUT FE  7E

After boot, the first timer ticks cause the banner to be queued and printed
on every channel (in the emulator, all 12 channels print it).

Multitasking
~~~~~~~~~~~~

The routines at ``07C8h``-``085Fh`` save and restore the registers and stack
pointer into a task table, giving a small preemptive scheduler:

* ``07C8h``: voluntary switch (the code loads A with a reason, e.g. ``01h``
  or ``02h``, and calls it).
* ``0760h`` (RST 3): decrements a time-slice counter at ``4000h`` and forces a
  switch when it expires; also decrements the link-timeout counters at
  ``429Bh``/``429Ch``.
* ``02E0h`` onward: the task that services Cyber polls and queued output.

Banner and message strings
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Address
     - Content
   * - near ``10D0h``
     - ``ID-7000 *READY* (200UT/SIM) VERSION 01.02.83``
   * - ``0EC5h``-``0F6Bh``
     - Self-test failure messages and the ``$2000-3000`` ... ``9000-A000``
       range strings
   * - ``1699h``-``18A0h``
     - Status and mode messages (``[CYBER LINK ...]``, ``[HP-CASSETTE ...]``)
   * - ``169Eh``
     - Length-prefixed command-name table (see below)

"200UT" is the CDC 200 User Terminal, a remote batch terminal for CDC Cyber
mainframes, so the firmware is a *200UT simulator* running on the ID-7000.

8251 and 8255 initialisation
----------------------------

The peripheral set-up is done in two places. Channel 0 is initialised first
(``0DA7h``-``0DB3h``) so that self-test errors can be printed. The rest is done
at ``0FFEh``-``1079h``: the sync 8251 (the first ``03h`` is loaded at
``0FFEh`` and written at ``1000h``), the 8255 (``OUT`` instructions at
``1014h``-``1020h``) and a loop over channels 0-11 (``1022h``-``1047h``) that
writes the async sequence through the stub table at ``0C91h`` and reads one
stale byte through ``0C04h``.

8251 initialisation
~~~~~~~~~~~~~~~~~~~



Common first step: ``03h`` then ``53h``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An 8251 accepts control-port writes in a fixed order (mode byte, sync
character(s) if any, then command bytes). After a warm restart the ROM cannot
know which step a chip is on, so every chip receives ``03h`` then ``53h``.

* Waiting for a mode byte: ``03h`` is taken as an async mode (the stop-bit
  field is invalid, which the chip tolerates), so ``53h`` is a command.
* Waiting for a command: ``03h`` is a harmless command (TxEN and DTR).
* Waiting for a single sync character: ``03h`` is that character.

In each case ``53h`` is then a command. ``53h`` is ``0101 0011``, which sets
IR, ER, DTR and TxEN. IR (internal reset, ``40h``) sends the chip back to the
wait-for-mode state; the other bits have no lasting effect.

.. note::

   One case is not covered: a chip waiting for a *second* sync character. The
   datasheet recommends three dummy writes for that situation.

Mode and command formats used
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Mode byte    D7  D6  D5  D4   D3  D2   D1  D0
   (async)      S2  S1  EP  PEN  L2  L1   B2  B1
                stop    even par  data bits   clock (01=x1, 10=x16, 11=x64)
   (sync, B=00) S2 = 1 single sync char, S1 = 0 internal sync detect

   Command byte D7  D6  D5   D4  D3    D2   D1   D0
                EH  IR  RTS  ER  SBRK  RxE  DTR  TxEN

Async channels 0-11
^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 12 25 63

   * - Byte
     - Kind
     - Meaning
   * - ``03h``
     - flush
     - See "Common first step" above.
   * - ``53h``
     - command
     - IR: internal reset.
   * - ``FAh``
     - mode
     - ``1111 1010``: async, clock divide x16, 7 data bits, parity enabled and
       even, 2 stop bits. In short, **7E2 at 16x the external clock**.
   * - ``25h``
     - command
     - ``0010 0101``: RTS, RxE, TxEN set. Transmitter and receiver enabled,
       RTS asserted. DTR is **not** asserted and the error flags are not
       cleared.

After the four writes the loop reads the channel's data port once to discard
any stale byte (stub at ``0C04h``).

.. note::

   The ROM does not set a baud rate. That is determined by the clock wired to
   the chip's TxC/RxC pins, so any speed selection must be in the hardware.

Synchronous Cyber link (``A0h``/``A1h``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The sequence is ``03h``, ``53h``, ``98h``, ``16h``, ``96h``.

.. list-table::
   :header-rows: 1
   :widths: 12 25 63

   * - Byte
     - Kind
     - Meaning
   * - ``03h``, ``53h``
     - flush, reset
     - As for the async channels.
   * - ``98h``
     - mode
     - ``1001 1000``: synchronous mode, 7 data bits, parity enabled and
       **odd**, single sync character, internal sync detect.
   * - ``16h``
     - sync character
     - SYN. In sync mode the byte after the mode word is the sync character.
   * - ``96h``
     - command
     - ``1001 0110``: EH (enter hunt), ER (clear errors), RxE, DTR. The
       receiver is enabled and searching for SYN. RTS and the transmitter
       are off.

The odd parity setting fits the sync character: SYN (``16h``) has three bits
set, so with odd parity its parity bit is 0 and it goes out as plain ``16h``.

Runtime commands (half duplex)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The line is run half-duplex. The receiver and transmitter are never enabled
together, and RTS is asserted only while transmitting.

.. list-table::
   :header-rows: 1
   :widths: 10 25 15 50

   * - Byte
     - Bits set
     - Address
     - Purpose
   * - ``96h``
     - EH, ER, RxE, DTR
     - ``0050h``, ``0280h``
     - Receive. Used after an error and after a transmit finishes.
   * - ``02h``
     - DTR
     - ``01C2h``
     - A complete frame has been received: switch the receiver off while the
       reply is prepared.
   * - ``33h``
     - TxEN, DTR, ER, RTS
     - ``01FDh``
     - Start a transmit with RTS asserted.

The routines at ``0050h`` and ``01FDh`` also set bit 2 and bit 4 of the interrupt
enable register (port ``FEh``): bit 2 enables ``RST 2`` (sync receive) and bit 4
enables ``RST 4`` (sync transmit).

Status bits used
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Bit
     - Use
   * - 0
     - TxRDY: tested before each character is written.
   * - 1
     - RxRDY: tested by the polling code and the sync receive ISR.
   * - 3-5
     - PE, OE, FE: the sync receive ISR masks with ``38h`` and resets the
       receiver on any error.

8255 initialisation
~~~~~~~~~~~~~~~~~~~

The 8255 is set up at ``1012h``-``1020h`` (``OUT`` instructions at ``1014h``-``1020h``). Port ``53h`` is the control
register, ``50h`` is port A and ``51h`` is port B.

.. list-table::
   :header-rows: 1
   :widths: 10 22 68

   * - Write
     - Kind
     - Effect
   * - ``82h``
     - mode set
     - ``1000 0010``: group A mode 0, **port A output**, port C upper output,
       group B mode 0, **port B input**, port C lower output.
   * - ``08h``
     - bit set/reset
     - Bit 7 = 0 selects bit set/reset. Bit number ``100`` = PC4, bit 0 = 0:
       **reset PC4**.
   * - ``09h``
     - bit set/reset
     - **Set PC4**.
   * - ``0Fh``
     - bit set/reset
     - Bit number ``111`` = PC7, bit 0 = 1: **set PC7**.

The mode write already clears the output latches, so the PC4 reset is
redundant. PC4 ends high; what it connects to is not known.

Printer output (``19E1h``)
^^^^^^^^^^^^^^^^^^^^^^^^^^

PC7 is the strobe. The routine:

1. Saves the character in D, disables interrupts (``DI``) and reads port B
   (``51h``). If bit 5 is set it yields to another task (``task_switch``)
   and retries.
2. Writes the character to port A (``50h``).
3. Writes ``0Eh`` (reset PC7, strobe low) then ``0Fh`` (set PC7, strobe high),
   re-enables interrupts and returns.

PC7 idles high and the strobe is active low. This is the usual Centronics-style
handshake with PB5 as a busy line, but it has not been confirmed against a
schematic. After a busy indication the code yields, then tests PB3
(``ANI 08h``): if clear it goes straight back to re-test busy, otherwise it
yields again. Its meaning is unclear. The busy path was never executed in the
emulator, because the stub reports the printer as always ready.

Where user input is handled
---------------------------

A byte arriving on any async channel raises RST 6 and runs the receive
handler.

Route of a received byte
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   RST 6 -> 0030h -> 0880h  rx_isr           save registers
              0CC0h  poll_rx          poll the 12 status ports (mask B=02h)
              0621h  chan_state_ptr   per-channel state record
              0D45h  port_stub        indirect IN via the table at 0C04h
              08B3h  main character handler / exit (POP, EI, RET)
              0A35h  buffer a printable byte for the line
              08FCh  end-of-line (CR 0Dh; 13h and 03h take related paths)

``0CC0h`` loops through channels asking ``IN 61h``, ``IN 63h`` ... until it
finds one with the requested status bit set, and returns the channel number
in C.

Indexed I/O tables
~~~~~~~~~~~~~~~~~~

``0D45h`` is a computed jump into a table of 4-byte entries. Each entry is
``IN port; RET; NOP`` or ``OUT port; RET; NOP``, so the port is selected by
channel number with the data byte still in A.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Table base
     - Meaning
   * - ``0C04h``
     - ``IN`` data port (``60h``, ``62h`` ... ``76h``)
   * - ``0C33h``
     - ``OUT`` data port
   * - ``0C62h``
     - ``IN`` status port (``61h``, ``63h`` ... ``77h``)
   * - ``0C91h``
     - ``OUT`` control port

Special characters
~~~~~~~~~~~~~~~~~~

The handler at ``08B3h`` reacts to a few control characters:

* ``0Dh`` (CR): end of line.
* ``13h``: also ends the line (path at ``08E4h``).
* ``03h`` (Ctrl-C): cancels/ends the line (path at ``092Fh``).
* ``7Fh`` (DEL) and the ``06h``/``01h`` state checks at ``08BEh``-``08C5h``
  are handled specially; their exact meaning was not pinned down.

Local commands and the Cyber path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At end of line the handler (``0917h``/``0918h``) checks whether the first
character of the line is a colon (``3Ah``).

* **Colon:** it is a *local command*. ``1500h`` matches the text against the
  length-prefixed table at ``169Eh``, ``1537h`` dispatches on the match,
  ``15ECh`` builds the reply, ``1694h`` copies each reply string, and the
  8251 stubs transmit it.
* **Anything else:** the line is queued for the Cyber host through ``0A35h``.
  While the link is down you get ``[CYBER LINK DOWN]``.

Call path observed for ``:STATUS`` plus CR:

.. code-block:: text

   0880 rx_isr -> 0CC0 poll_rx -> 0621 chan_state_ptr -> 0D45 port_stub
     -> 0621 -> 1529 tbl_get -> 1500 cmd_match -> 1537 cmd_dispatch
     -> 15EC build_reply -> 1694 copy_str (x4) -> 0D45 port_stub (transmit loop)

Local command table (``169Eh``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Names are stored with a length byte in front. Commands observed in the
emulator:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Typed
     - Reply
   * - ``:STATUS``
     - Four lines: ASCII mode, CR/LF-at-80 mode, HP-cassette mode and
       paper-tape mode (for example ``[ASCII NORMAL MODE (95 CH-SET)]``,
       ``[NO CR/LF AT LINES WITH 80 CHARS]``,
       ``[HP-CASSETTE MODE OFF]``, ``[PAPER TAPE MODE OFF]``)
   * - ``:HP,ON``
     - ``[HP-CASSETTE MODE ON]``
   * - ``:PTAPE,ON``
     - ``[PAPER TAPE MODE ON]``
   * - ``:AUTO80,ON``
     - ``[AUTO CR/LF AT LINES WITH 80 CHARS]``
   * - ``:RESET``
     - ``[USER PORT NORMAL MODE]``
   * - ``:ASC128,ON``
     - Expected ``[ASCII EXTENDED MODE (128 CH-SET)]`` from the string
       table, but the reply was **not cleanly captured** (it overlapped the
       previous command's output), so this is unconfirmed
   * - ``:FOO``
     - ``[ILLEGAL COMMAND]``
   * - ``HELLO``
     - ``[CYBER LINK DOWN]`` (before the link is up)

.. note::

   The ROM does not echo typed characters, so the connected terminal is
   presumably echoing locally.

The Cyber link
--------------



What it is
~~~~~~~~~~

The Cyber link is a **synchronous serial connection to a CDC Cyber
mainframe**. It is not a device on the board; it is the *host* the ID-7000
talks to. The evidence:

* The banner says ``(200UT/SIM)``; the CDC 200 User Terminal connected to
  Cyber mainframes over synchronous lines.
* The status strings are ``[CYBER LINK ESTABLISHED]``, ``[CYBER LINK LOST]``,
  ``[CYBER LINK DOWN]`` and
  ``[CYBER LINK: SITE ADDRESS 1 NOT ACTIVE]``.
* The ``A0h``/``A1h`` 8251 is configured in sync mode with SYN (``16h``).
* Lines that do not start with ``:`` are queued for the link.

The framing is bisync-like. The exact CDC 200UT protocol was not available, so
the details below describe what the firmware does, *not* a published spec.

Frame format
~~~~~~~~~~~~

.. code-block:: text

   SYN SYN SYN  SOH  addr  dev  ctl  [data...]  ETX  LRC

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Field
     - Meaning
   * - ``addr``
     - ``70h`` + channel number (``70h`` to ``7Bh`` for the 12 channels). The
       ROM subtracts ``70h`` (``02E8h``) and uses it as an index.
   * - ``dev``
     - ``60h``, ``61h``, ``70h`` or ``71h`` (the only values the receive code
       accepts). The meaning of each was not determined.
   * - ``ctl``
     - ``05h`` (ENQ) = poll. ``11h``, ``12h``, ``0Ch`` = data to the terminal.
       ``18h``, ``13h``, ``06h`` are used in terminal replies (see below).
   * - ``LRC``
     - The complement of the XOR of every byte from SOH to ETX. The receiver
       checks only the low 7 bits.

Receive state machine (RST 2, ``005Bh``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

State is held in ``A2F2h``; the running LRC is in ``A2F3h``
(initialised to ``FEh`` at SOH, which is the complement of SOH).

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - State
     - Action
   * - ``FFh``/``FEh``
     - Idle. SYN is ignored; ``01h`` (SOH) moves to state 0, clears the
       timeout counters, and, if the link was down, broadcasts
       ``[CYBER LINK ESTABLISHED]`` to channels 0-11.
   * - 0
     - Address byte, must be ``70h``-``7Eh``; stored at ``A2F4h``.
   * - 1
     - ``dev`` byte, must be ``60h``/``61h``/``70h``/``71h``; stored at
       ``A2F5h``.
   * - 2
     - ``ctl`` byte. ENQ goes to state 3. ``11h``/``12h``/``0Ch`` allocate a
       buffer (``0671h``), copy the header into it and go to state 4.
   * - 3
     - Expect ETX, then state 6.
   * - 4
     - Data bytes appended to the buffer until ETX, then state 5.
   * - 5
     - LRC after a data frame. On success the buffer is flagged complete (4)
       and ``A2D2h`` is set to 0.
   * - 6
     - LRC after an ENQ. On success ``A2D2h`` is set to the address, the
       receiver is turned off (``02h`` to ``A1h``), and the service task is
       woken via ``07CDh``.

A status error (parity, overrun or framing, mask ``38h``) or any invalid
byte goes to ``0087h``, which resets the state machine and writes ``96h``
to ``A1h`` (re-enter hunt).

Transmit state machine (RST 4, ``020Bh``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The transmit-start routine at ``01D6h`` writes ``33h`` to ``A1h`` and sets a
bit in port ``FEh``. State is kept in ``A2F9h``.

.. code-block:: text

   11 x SYN (16h)  ->  SOH  ->  payload bytes  ->  ETX  ->  LRC
   -> trailing SYN  ->  write 96h to A1h (back to receive)

Replies observed from the emulator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Host sent
     - Terminal replied
   * - ENQ poll, nothing waiting
     - ``SOH addr dev 18h ETX LRC``
   * - ENQ poll, a typed line queued
     - ``SOH addr 61h 13h <text> ESC B ETX LRC``
   * - Valid data frame (``11h``/``12h``/``0Ch``)
     - ``SOH addr dev 06h ETX LRC`` (``06h`` = ACK)

For example, with ``HELLO`` queued on channel 0 a poll returns:

.. code-block:: text

   16 x11  01 70 61 13 48 45 4C 4C 4F 1B 42 03 E4 16

and an idle poll returns:

.. code-block:: text

   16 x11  01 70 60 18 03 F5 16

Host to user data
~~~~~~~~~~~~~~~~~

The data portion must end with an ESC trailer, otherwise the ROM discards it
(``03D4h``-``03F3h``):

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Trailer
     - Destination
   * - ``ESC B`` or ``ESC "``
     - The channel's console (addr minus ``70h``), with CR/LF appended
   * - ``ESC space`` or ``ESC !``
     - The printer port (8255 port A), with CR/LF characters around the text
       (part of the text was lost in testing, so this path needs more work)

The ``ctl`` byte also matters: ``11h`` gives plain text, while ``12h`` and
``0Ch`` put a ``1Fh`` byte in front (probably home or clear-screen).

Link-lost timeout
~~~~~~~~~~~~~~~~~

SOH clears the counters at ``429Bh`` and ``429Ch``. The RST 3 handler
decrements them; when both run out it sets ``429Dh`` and broadcasts
``[CYBER LINK LOST]`` (string at ``17F7h``) to all channels. The real-time
length depends on the tick rate, which is unknown.

Printing
--------

Printing is started by the Cyber host. No typed command or key that starts a
print was found, and nothing prints while the link is down.

Activation
~~~~~~~~~~

The host sends a data frame whose text ends with ``ESC`` followed by a space
(``20h``):

.. code-block:: text

   SYN SOH addr dev ctl <cc> <text...> ESC space ETX LRC

* ``addr`` (the channel) and ``dev`` make no difference: channels 1, 5 and 11
  printed as well as channel 0, and all four ``dev`` values gave the same result.
* ``ctl`` should be ``12h`` (DC2). With ``11h`` or ``0Ch`` the ROM drops two
  bytes of the text instead of one. The reason is not known.
* The ROM acknowledges the frame at once (``ctl`` ``06h``). A separate task does
  the printing, so the host is not held up.
* ``03D4h``-``03E4h`` chooses the destination from the trailer: ``ESC B`` and
  ``ESC "`` go to the console, ``ESC space`` goes to the printer. ``ESC !``
  (``21h``) is acknowledged but printed nothing in any test.

Text format
~~~~~~~~~~~

The first byte of the text, ``<cc>``, is a carriage-control character that the
ROM consumes:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - ``<cc>``
     - Printer output
   * - ``A``
     - Form feed (``0Ch``)
   * - ``J``
     - Extra line feed, then line feed and carriage return
   * - anything else (tested: space, ``0``, ``1``, ``+``, ``-``, ``2``, ``@``)
     - Line feed, carriage return

The digit ``1`` is single spacing in this ROM, not a page eject. Inside the text,
``ESC`` plus a character (``1953h``-``1993h``):

.. list-table::
   :header-rows: 1
   :widths: 24 46 30

   * - After ``ESC``
     - Effect
     - Tested
   * - ``23h``-``3Fh``
     - Prints (character - ``20h``) spaces
     - ``#`` = 3, ``%`` = 5, ``0`` = 16
   * - ``43h``-``4Fh``
     - Prints (character - ``40h``) zeros
     - ``C`` = 3, ``J`` = 10
   * - ``@`` or ``A``
     - Carriage return (overprint)
     -
   * - anything else
     - Ignored
     - ``P``

Hardware conditions
~~~~~~~~~~~~~~~~~~~

* PB5 (port ``51h`` bit 5) must be low. While it is high nothing prints; the host
  still gets its acknowledgement and the text prints once PB5 clears.
* If a busy state was seen, PB3 must also be low before the ROM retries. With PB3
  high the task keeps yielding even after PB5 clears. PB3 high looks like an
  offline or fault input. This was only observed after a busy had been seen.
* The strobe is PC7, idle high, pulsed low then high for each character.

Searched for and not found
~~~~~~~~~~~~~~~~~~~~~~~~~~

Every control character (``00h``-``1Fh`` and ``7Fh``) was typed on channel 0
followed by ``X`` and a carriage return. Most pass through to the host
unchanged. Ctrl-A (``01h``) is sent as ``ESC Q`` and Ctrl-V (``16h``) as
``ESC R``; Ctrl-C and CR drop the text and send only ``ESC B``; Backspace edits
the line. Ctrl-A and Ctrl-V could be function keys that make the host start a
print, but that is speculation.

Methodology
-----------

The sequence of steps, so that the analysis can be repeated or extended:

1. **Hex dump** the image. Recognise 8080 code, ``76h`` padding and ASCII
   strings.
2. **Recursive-descent disassembly** from the reset and RST vectors.
   This reached only about 2,800 bytes because the firmware uses computed
   jumps (``PCHL`` on the I/O stub tables) and interrupt entry points.
   Unreached ranges were disassembled linearly and marked with ``?``.
3. **Write the 8080 core** and run the ROM with default I/O (all reads
   return 0). The checksum and RAM test pass without any I/O help.
4. **Log all I/O** to learn the port layout and the 8251 reset sequences.
5. **Model the 8251 status bits** (TxRDY/RxRDY) and inject RST 3 ticks to get
   the banner.
6. **Inject bytes** via RST 6 and record the call graph to find the input
   path; try several commands.
7. **Model the sync 8251** and inject frames via RST 2, inspecting the state
   variables after each byte; model RST 4 to capture replies; then vary
   ``addr``/``dev``/``ctl`` and the ESC trailers to map the behaviour.

Open questions
--------------

* What ``ESC !`` does, and why ``ctl`` ``11h`` and ``0Ch`` drop an extra byte.
* What PB3 and PC4 (8255) are wired to.
* Whether the interrupt module clears an enable bit when an interrupt is taken,
  and what sets the timer tick period (the ROM never writes ``FFh``).
* The proper acknowledgement of a queued line: in testing a line was resent on
  every poll until a data frame was sent.
* One reply in the printer test matrix showed address ``84h`` instead of
  ``70h``. It did not recur and is unexplained.
* The code at ``125Bh``-``14FEh`` is linked for base ``7D00h`` (it would run at
  ``8F5Bh``-``91FFh``), is never referenced, and calls addresses that do not
  exist in this ROM. Its origin is not known.
* Which clock sets the 8251 baud rates, and whether they can be selected.

Appendix: key routine addresses
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Address
     - Routine
   * - ``0000h``
     - Reset vector
   * - ``0040h``
     - Sync-line error reset (writes ``96h`` to ``A1h``)
   * - ``005Bh``
     - Sync receive ISR (RST 2)
   * - ``0087h``
     - Receive error path
   * - ``01D6h``
     - Start sync transmit
   * - ``020Bh``
     - Sync transmit ISR (RST 4)
   * - ``02E0h``
     - Poll-service task
   * - ``0621h``
     - Per-channel state pointer
   * - ``0671h``
     - Buffer allocation
   * - ``0760h``
     - Timer ISR (RST 3)
   * - ``07C8h``
     - Task switch
   * - ``0869h``
     - Idle loop
   * - ``0880h``
     - Async receive ISR (RST 6)
   * - ``08B3h``
     - Character handler and ISR exit
   * - ``0A35h``
     - Buffer or queue a character for the host
   * - ``0C04h``/``0C33h``/``0C62h``/``0C91h``
     - IN data / OUT data / IN status / OUT control stub tables
   * - ``0CC0h``
     - Poll all channels for a ready status bit
   * - ``0D45h``
     - Indexed jump into the stub tables
   * - ``0DA0h``
     - Boot and self-test
   * - ``1500h``
     - Command-name matcher
   * - ``1529h``/``1530h``
     - Table get/set helpers
   * - ``1537h``
     - Command dispatcher
   * - ``15ECh``
     - Build reply / broadcast message
   * - ``1694h``
     - Copy a length-prefixed string
   * - ``169Eh``
     - Command-name table
   * - ``17F7h``/``180Dh``
     - ``[CYBER LINK LOST]`` / ``[CYBER LINK ESTABLISHED]`` messages
   * - ``19E1h``
     - Printer byte output (8255, strobe on PC7)
