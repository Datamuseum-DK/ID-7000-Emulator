Comparison of the Two ID-7000 ROM Images
========================================

.. contents:: Contents
   :local:
   :depth: 2

.. note::

   The two images compared here are the *board 5 image* (``board5_eproms_0_to_6.bin``,
   described in :doc:`board5_terminal_concentrator`) and the *IPC/1 + SPC/1 image*
   (``SPS_1``-``SPS_5`` followed by ``FUNK_1``-``FUNK_3``, described in
   :doc:`sps_funk_ipc1`). Everything is inferred from the firmware and the
   emulators, except that ports ``FEh``/``FFh`` are an interrupt and timer module,
   which was supplied with the project.

Summary
-------

* Both are plain 8080 firmware for the same machine family. They share the same
  conventions for the console UART, the 8251 reset sequence, the vector area and
  the interrupt and timer module, but the application code is unrelated.
* The board 5 image is a **terminal concentrator**: twelve user terminals and a
  synchronous line to a CDC Cyber host, simulating a CDC 200 User Terminal.
* The IPC/1 image is a **multitasking operating system with a PLC runtime**: one
  operator console, a serial programming link, and digital and analog process
  I/O.
* In both images bit *n* of port ``FEh`` enables the interrupt source that
  raises ``RST n``, and a read of port ``FFh`` acknowledges the timer tick.

At a glance
-----------

.. list-table::
   :header-rows: 1
   :widths: 18 41 41

   * - Aspect
     - Board 5 image
     - IPC/1 + SPC/1 image
   * - Source files
     - One 7 KB file (seven 1 KB EPROMs, numbers 0-6)
     - Eight 2 KB files: ``SPS_1``-``SPS_5`` and ``FUNK_1``-``FUNK_3``
   * - Size and addresses
     - 7168 bytes, ``0000h``-``1BFFh``
     - 16384 bytes, ``0000h``-``3FFFh``
   * - CPU
     - 8080
     - 8080 (the vector at ``0024h`` jumps to ``F000h``, the 8085 TRAP address)
   * - Dates
     - Banner ``VERSION 01.02.83``
     - ROM files dated 29 Dec 1988 (FUNK) and 5 May 1989 (SPS); SPC/1 version
       string ``88.03.14``
   * - Role
     - Terminal concentrator, CDC 200UT simulator
     - Operating system (IPC/1) with a PLC runtime (SPC/1)
   * - Text language
     - English
     - Danish (7-bit national character set)
   * - Software structure
     - Interrupt driven, idle ``HLT`` loop, small task switch
     - Preemptive kernel: 8 priorities, semaphores, mailboxes, API jump table
   * - Self-test
     - ROM checksum and RAM test with error messages
     - None found in the boot path
   * - Operator interface
     - 12 async channels; local commands start with ``:``
     - One console: menu with ``C``, ``D``, ``P``
   * - Host link
     - Synchronous 8251, SYN lead-in, ``SOH ... ETX LRC`` frames
     - Async 8251, ``7Eh`` flag frames, byte stuffing, CRC-16
   * - Process I/O
     - 8255 printer port only
     - 160 digital inputs, 64 digital outputs, 6 analog modules
   * - User code
     - None
     - Downloadable PLC program, function library, operator-started processes
   * - Debugging
     - None seen
     - ``D`` command calls an external debugger at ``F008h``

Shared conventions
------------------

* **Console UART.** An 8251 at ports ``60h``/``61h`` (data even, control odd), in
  both images.
* **8251 reset.** Every 8251 gets ``03h`` and then ``53h`` first (a dummy write
  followed by the internal-reset command), then its mode and command bytes.
* **Interrupt and timer module.** ``FEh`` is written ``00h`` at the start of boot
  and then bits are set; ``FFh`` is read in the timer ISR.
* **Vector area.** The restart vectors are eight bytes apart and padded with
  ``76h`` (``HLT``). Unused vectors are ``EI; RET``.
* **Port numbers.** Both address devices with 8-bit ``IN``/``OUT`` port numbers
  and keep RAM from ``4000h``.
* **Terminal control.** Both send ``ESC`` sequences to a CRT terminal.
* **Cyber link and aux link.** Both use a second 8251 with a framed protocol and a
  station address (``70h`` plus the channel, or ROM byte ``27FFh``).

Interrupt assignment
--------------------

.. list-table::
   :header-rows: 1
   :widths: 10 12 39 39

   * - RST
     - Bit in ``FEh``
     - Board 5 image
     - IPC/1 + SPC/1 image
   * - 1
     - ``02h``
     - Unused (``EI; RET``)
     - Timer tick (``0392h``)
   * - 2
     - ``04h``
     - Sync line receive (``005Bh``)
     - Aux UART, receive and transmit (``0E31h``)
   * - 3
     - ``08h``
     - Timer tick (``0760h``)
     - Unused (``EI; RET``)
   * - 4
     - ``10h``
     - Sync line transmit (``020Bh``)
     - Console UART, receive and transmit (``07A2h``)
   * - 5
     - ``20h``
     - Unused (``EI; RET``)
     - Unused (``EI; RET``)
   * - 6
     - ``40h``
     - Async receive, 12 channels (``0880h``)
     - Unused (``EI; RET``)
   * - 7
     - ``80h``
     - Restarts the system (``JMP 0DA0h``)
     - Unused (``EI; RET``)

The bit numbers were deduced from the ``ORI`` constants in the firmware (see the
next section), not read from a manual.

The interrupt and timer module in both images
---------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 24 38 38

   * - Aspect
     - Board 5 image
     - IPC/1 + SPC/1 image
   * - Start of boot
     - ``OUT FEh,00h`` (``0DA3h``)
     - ``OUT FEh,00h`` (``00CFh``) and a dummy ``IN FFh`` (``00D1h``)
   * - How sources are enabled
     - All at once: ``OUT FEh,7Eh`` (bits 1-6) at the end of initialisation, plus
       ``ORI 04h`` in the sync receive reset and ``ORI 10h`` at each transmit start
     - One at a time, each right after its device is set up: ``ORI 10h`` (console),
       ``ORI 04h`` (aux UART), ``ORI 02h`` (timer, when the clock process starts)
   * - Bits ever cleared
     - No
     - No
   * - Timer acknowledge
     - ``IN FFh`` at ``0762h``
     - ``IN FFh`` at ``0396h``
   * - Tick period set by the ROM
     - No (``FFh`` is never written)
     - No (``FFh`` is never written)
   * - Use of the tick
     - Link timeout counters
     - Time slice, 5-tick semaphore, uptime counter at ``4000h``

Serial devices
--------------

.. list-table::
   :header-rows: 1
   :widths: 22 30 48

   * - Device
     - Initialisation bytes
     - Meaning
   * - Board 5, user channels (12)
     - ``03h, 53h, FAh, 25h``
     - 7 data bits, even parity, 2 stop bits, x16 clock; transmitter and receiver
       on, RTS
   * - Board 5, Cyber link
     - ``03h, 53h, 98h, 16h, 96h``
     - Synchronous, 7 bits, odd parity, one sync character ``16h`` (SYN); receiver
       hunting
   * - IPC/1, console
     - ``03h, 53h, 7Ah, 26h``, later ``27h``
     - 7 data bits, even parity, 1 stop bit, x16 clock; transmitter switched on
       when there is output
   * - IPC/1, aux link
     - ``03h, 53h, 6Fh, 16h``
     - 8 data bits, no parity, 1 stop bit, x64 clock; receiver on

Port map
--------

.. list-table::
   :header-rows: 1
   :widths: 18 41 41

   * - Ports
     - Board 5 image
     - IPC/1 + SPC/1 image
   * - ``08h``/``09h``
     - Not used
     - Aux link 8251
   * - ``0Ah``
     - Not used
     - Written every 5 ticks by the clock process (watchdog or heartbeat, unverified)
   * - ``10h``-``17h``
     - Not used
     - Digital outputs (64 points)
   * - ``20h``-``33h``
     - Not used
     - Digital inputs (160 points, active low)
   * - ``40h``-``4Bh``
     - Not used
     - Six analog input modules
   * - ``50h``-``53h``
     - 8255 printer port
     - Not used
   * - ``60h``-``77h``
     - 12 user-channel 8251s
     - Console 8251 at ``60h``/``61h`` only
   * - ``A0h``/``A1h``
     - Synchronous 8251 (Cyber link)
     - Not used
   * - ``FEh``/``FFh``
     - Interrupt and timer module
     - Interrupt and timer module

Memory maps
-----------

.. list-table::
   :header-rows: 1
   :widths: 22 39 39

   * - Range
     - Board 5 image
     - IPC/1 + SPC/1 image
   * - ROM
     - ``0000h``-``1BFFh``
     - ``0000h``-``3FFFh`` (``2800h``-``3FFFh`` is the FUNK library)
   * - RAM
     - ``4000h``-``BFFFh``, tested at boot
     - From ``4000h``; used at least up to ``81xxh``; extent not confirmed
   * - Variables
     - ``A2xxh``-``A3xxh`` (link state), ``4000h``-``42xxh`` (tasks and timers)
     - ``4000h``-``4C0xh`` (kernel and SPC/1), images at ``52D5h``/``5A55h``
   * - Program area
     - None
     - ``8000h`` and up (downloaded program, entry ``807Ch``)
   * - External
     - Relocated block in ROM at ``125Bh``-``14FEh`` built for ``7D00h``
     - Debugger at ``F000h`` (not in the image)

The two host protocols
----------------------

.. list-table::
   :header-rows: 1
   :widths: 18 41 41

   * - Aspect
     - Cyber link (board 5)
     - Aux link (IPC/1)
   * - Direction
     - The host polls the terminal; the terminal answers every frame
     - A programming device sends requests; the target answers every frame
   * - Frame
     - ``SYN x3, SOH, addr, dev, ctl, data, ETX, LRC``
     - ``7Eh, LEN, ADDR, N, sub-messages, CRC-16, 7Eh``
   * - Delimiting
     - SYN lead-in, ``SOH`` and ``ETX``
     - ``7Eh`` flag, length byte that counts itself
   * - Special bytes
     - Sent as they are (the data uses ``ESC`` trailers)
     - ``40h``, ``7Eh``, ``06h``, ``15h``, ``1Bh`` are sent as ``40h K C`` with
       ``K xor C`` equal to the byte
   * - Integrity
     - LRC: complement of the XOR, checked on 7 bits
     - CRC-16 over the length, data and CRC (residue 0)
   * - Handshake
     - ``ctl`` ``06h`` in a reply frame
     - Single ``06h``/``15h`` bytes between frames
   * - Addressing
     - ``70h`` + channel number
     - ROM byte ``27FFh`` (``FFh``)
   * - Content
     - Poll, terminal data in and out, printer data
     - Commands: download, run control, read and write images, version, tables
   * - First frame
     - Poll brings the link up
     - First frame only triggers a start-up reply

Emulators
---------

.. list-table::
   :header-rows: 1
   :widths: 22 39 39

   * - Aspect
     - Board 5 package (``id7000_emu``)
     - IPC/1 package (``id7000_sps_emu``)
   * - CPU core
     - ``cpu8080.py``
     - The same file (byte for byte identical)
   * - Machine model
     - 12 simple 8251s, a synchronous 8251, 8255 printer stub
     - Console and aux 8251s with a one-byte holding register and character pacing,
       digital I/O, analog modules
   * - Timer
     - ``TICK = 2500`` steps, interrupt raised at every tick
     - ``TICK = 4000`` steps (800 in the front end), latched until it can be taken
   * - Interrupt module (``FEh``)
     - Not modelled: interrupts are raised whenever an event happens
     - Not modelled: interrupts are raised while the device has work
   * - Host stubs
     - Cyber host (``sync.py``), printer (``printer.py``)
     - Aux host (``aux.py``), terminal (``terminal.py``)
   * - Tools
     - Demo scripts only
     - Demo scripts, curses front end with debugger, assembler, self-test
   * - Timing guess
     - 2500 steps per tick (unknown real rate)
     - 500 ticks per second at 400,000 steps per second (assumption)

What the comparison suggests
----------------------------

* The two ROMs come from the same machine family. The common interrupt and timer
  module, the console 8251 at ``60h``/``61h`` and the habit of resetting an 8251
  with ``03h, 53h`` point to a shared CPU board, with different peripheral
  boards behind the bus.
* Hardware that does not appear in one image is simply absent from that
  configuration: the board 5 image has no process I/O, the IPC/1 image has no
  printer port and no multi-channel UART board.
* A single emulator core could host both images. It would need the 8251 model
  (with the holding register), a timer with latched ticks, and a model of ``FEh``
  that gates ``RST 1`` to ``RST 7`` by bit number. None of the emulators gates
  interrupts through ``FEh`` yet.
* The 5-tick semaphore and the uptime counter in the IPC/1 kernel suggest a
  base tick rate that the board 5 image does not reveal. The two timer
  periods in the emulators are therefore independent guesses.

Open questions
--------------

* Does the interrupt module clear an enable bit when it delivers an interrupt?
  Both images only ever set bits.
* What fixes the timer tick period, given that neither ROM writes ``FFh``?
* Is the CPU an 8085 fitted into an 8080 system? The IPC/1 vector table has a TRAP
  entry, but neither image uses ``RIM`` or ``SIM``.
* Are the board 5 channel numbers (``70h`` + n) and the IPC/1 station address
  (``FFh``) the same kind of address on different hardware, or unrelated?
