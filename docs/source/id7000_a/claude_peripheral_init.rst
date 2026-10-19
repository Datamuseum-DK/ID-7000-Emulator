========================================
Peripheral Initialisation: 8251 and 8255
========================================

.. contents:: 8251 and 8255
   :local:
   :depth: 2

.. note::

   Everything here is decoded from the ``OUT`` instructions in the board 5 ROM
   (``board5_eproms_0_to_6.bin``) against the standard Intel 8251/8251A and
   8255A register formats. The pin wiring and the baud-rate clock are
   *inferred*; no schematic was available.

Overview
========

The firmware drives three kinds of peripheral chip:

.. list-table::
   :header-rows: 1
   :widths: 22 18 60

   * - Chip
     - Ports
     - Role (inferred)
   * - 8251 USART x 12
     - ``60h``/``61h`` to ``76h``/``77h``
     - Async user channels. Chip *n* uses ``60h+2n`` (data) and ``61h+2n``
       (control/status).
   * - 8251 USART x 1
     - ``A0h``/``A1h``
     - Synchronous line to the Cyber host.
   * - 8255 PPI
     - ``50h``-``53h``
     - Parallel (printer-style) output port.

The 8251 C/D pin is probably wired to address bit A0, so the odd port is
always the control/status register.

Where the code is
-----------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Address
     - Purpose
   * - ``0DA7h``-``0DB3h``
     - Channel 0 initialisation, done *before* the self-test so that error
       messages can be printed.
   * - ``0FFFh``-``1010h``
     - Synchronous 8251 initialisation (the first ``03h`` is loaded at
       ``0FFFh``).
   * - ``1012h``-``1020h``
     - 8255 initialisation.
   * - ``1022h``-``1079h``
     - Loop over channels 0-11, writing the async init sequence through the
       stub table at ``0C91h``.
   * - ``0050h``, ``01C2h``, ``01FDh``, ``0280h``
     - Runtime commands to the synchronous 8251.
   * - ``19E1h``
     - Printer byte output using the 8255.

8251 initialisation
===================

Common first step: ``03h`` then ``53h``
---------------------------------------

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
-----------------------------

.. code-block:: text

   Mode byte    D7  D6  D5  D4   D3  D2   D1  D0
   (async)      S2  S1  EP  PEN  L2  L1   B2  B1
                stop    even par  data bits   clock (01=x1, 10=x16, 11=x64)
   (sync, B=00) S2 = 1 single sync char, S1 = 0 internal sync detect

   Command byte D7  D6  D5   D4  D3    D2   D1   D0
                EH  IR  RTS  ER  SBRK  RxE  DTR  TxEN

Async channels 0-11
-------------------

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
----------------------------------------

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
------------------------------

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

The routines at ``0050h`` and ``01FDh`` also set bit 2 and bit 4 of the system
latch (port ``FEh``). What those bits control is not known.

Status bits used
----------------

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
===================

The 8255 is set up at ``1012h``-``1020h``. Port ``53h`` is the control
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
--------------------------

PC7 is the strobe. The routine:

1. Disables interrupts and reads port B (``51h``). If bit 5 is set it yields
   to another task (``task_switch``) and tries again.
2. Writes the character to port A (``50h``).
3. Writes ``0Eh`` (reset PC7, strobe low) then ``0Fh`` (set PC7, strobe high).

PC7 idles high and the strobe is active low. This is the usual Centronics-style
handshake with PB5 as a busy line, but it has not been confirmed against a
schematic. After a busy indication the code also tests PB3 (``ANI 08h``); its
meaning is unclear.

Emulator status
===============

* ``sync.py`` models the 8251 mode / sync-character / command sequence and
  the TxRDY/RxRDY status bits for the sync chip.
* The 12 async channels use a simpler stub (``machine.py``): status is
  always TxRDY plus RxRDY when a byte is queued, and control writes are
  ignored.
* The 8255 is a stub. Reads of port ``51h`` return 0, so the printer is
  always ready; PB3 and PC4 are not modelled.

Open questions
==============

* What clock sets the baud rate, and whether it is selectable.
* What bits 2 and 4 of the system latch (``FEh``) control.
* What PC4 (8255) and PB3 connect to.
* Whether the chips are 8251 or 8251A (the sequence works on both).
