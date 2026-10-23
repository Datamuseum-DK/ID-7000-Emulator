 
Analysis - Claude
==================

.. contents:: Contents
   :local:
   :depth: 2

.. note::

   This document describes a 16 KB firmware image for the ID-7000, built from
   the eight ROM files ``SPS_1`` to ``SPS_5`` (``SPS_n_5_890505_ADR_255``) and
   ``FUNK_1`` to ``FUNK_3`` (``FUNK_n_3_881229``), concatenated in that order
   at address ``0000h``. Everything is *inferred* from the firmware and from
   behaviour observed in a Python emulator. Nothing has been checked against
   hardware manuals or schematics. Statements are marked as *inferred* or
   *unverified* where that matters.

Summary
-------

* The CPU is a plain **Intel 8080**. There is no ``RIM``/``SIM`` and no 8085-only
  opcode. The vector at ``0024h`` (the 8085 TRAP address) jumps to ``F000h``,
  where a debugger ROM that is not part of these files would sit.
* The image is a small **multitasking operating system, IPC/1**, with eight
  start-up processes, priority scheduling, semaphores and mailboxes.
* On top of it runs a **PLC runtime, SPC/1** ("SPS" in the file names is the
  German abbreviation for a programmable logic controller). It scans digital
  and analog inputs, calls a compiled boolean user program and writes the
  outputs.
* The user program is **downloaded over a serial link** (the "aux link",
  ports ``08h``/``09h``) and relocated in place by a loader in the ROM.
  The link uses HDLC-like frames with byte stuffing and a CRC-16.
* The **FUNK** ROMs hold a library of function blocks that compiled programs
  call by number.
* The operator console (ports ``60h``/``61h``) shows a Danish menu
  (``VELKOMMEN TIL IPC/1 OPERATIVSYSTEMET``) with commands ``C``, ``D`` and
  ``P``.

Image layout
------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Files
     - Address
     - Content
   * - ``SPS_1``-``SPS_5``
     - ``0000h``-``27FFh``
     - IPC/1 kernel, drivers, SPC/1 runtime. ROM date 5 May 1989. The last
       byte (``27FFh`` = ``FFh``) is the station address on the aux link, which
       matches "ADR 255" in the file names.
   * - ``FUNK_1``-``FUNK_3``
     - ``2800h``-``3FFFh``
     - A function pointer table at ``2800h``-``287Fh`` followed by the
       function code. ROM date 29 December 1988.

A version string ``88.03.14`` sits at ``1211h``. The command interpreter
returns it for command ``60h``.

Text is Danish in the 7-bit national character set: ``[`` is Æ, ``\\`` is Ø and
``]`` is Å. The ROM text ``V[LG IMELLEM F\\LGENDE`` therefore reads
"VÆLG IMELLEM FØLGENDE".

Memory map (inferred)
---------------------

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Range
     - Contents
   * - ``0000h``-``3FFFh``
     - ROM
   * - ``4000h``-``4BB1h``
     - Kernel and driver variables, zeroed at boot. Includes the process queues
       (``4014h`` + 5 x priority), semaphores, console and aux state, the RAM
       I/O stubs at ``48EEh`` and ``48F1h``, and the CRC tables
       (``49A8h``/``4AA8h``).
   * - ``4BB2h``-``4C0xh``
     - SPC/1 variables: image base pointers (``4BB4h`` outputs, ``4BB6h``
       inputs, ``4BB8h`` markers), I/O configuration pointer (``4BC4h``),
       function table pointer (``4BD3h``), user program entry (``4BD5h``),
       download pointer (``4C00h``), PLC state (``4C02h``).
   * - ``4C06h``-``4D0Ch``
     - Aux message buffer (``4C06h``), received frame (``4C08h``), command
       buffer (``4C8Ch``).
   * - ``4D0Dh``-``508Dh``
     - Reply buffer and the aux transmit ring (``4D8Dh``-``508Dh``).
   * - ``52D5h``, ``5A55h``
     - Digital output image and input image (1920 bytes each, one byte per
       point). Taken from the pointers observed after boot.
   * - about ``77F0h``
     - Analog value table, 4-byte records (inferred from a diff of two runs).
   * - ``7F5Fh``-``7FFFh``
     - RAM copy of the function table (copied from ``2800h`` at boot).
   * - ``8000h``-``807Bh``
     - User program header as downloaded.
   * - ``807Ch``
     - User program entry (initial value of ``4BD5h``).
   * - ``F000h``
     - Debugger (external, missing from these files).

The firmware writes up to ``7FFEh`` during boot, and the downloaded program
lives at ``8000h`` and above, so the RAM extends at least to about ``81xxh``.
The upper limit is not confirmed. The emulator treats everything above the
ROM as RAM.

I/O map (inferred)
------------------

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Ports
     - Device
   * - ``60h``/``61h``
     - 8251 operator console. Init ``03h, 53h, 7Ah, 26h`` then ``27h``:
       7 data bits, even parity, 1 stop bit, x16 clock. Interrupt driven in
       both directions.
   * - ``08h``/``09h``
     - 8251 aux link. Init ``03h, 53h, 6Fh, 16h``: 8 data bits, no parity,
       1 stop bit, x64 clock, receiver on first.
   * - ``0Ah``
     - Written every 5 timer ticks by the clock process. Possibly a watchdog
       retrigger or heartbeat. *Unverified.*
   * - ``10h``-``17h``
     - Digital outputs: 8 ports, 64 points.
   * - ``20h``-``33h``
     - Digital inputs: 20 ports, 160 points, active low.
   * - ``40h``-``4Bh``
     - Six analog input modules (see below).
   * - ``FEh``
     - System latch. The boot code ORs bits ``10h``, ``04h`` and ``02h`` into
       it after setting up the console, the aux UART and the I/O modules. The
       meaning is not known.
   * - ``FFh``
     - Read by the timer ISR (tick acknowledge).

The port numbers in the digital I/O and analog scans are patched into two
RAM stubs at run time (``48EEh``: ``IN p; RET``, ``48F1h``: ``OUT p; RET``),
so the ``IN`` and ``OUT`` instructions for those ports do not appear in the
ROM.

Interrupts and vectors
----------------------

.. list-table::
   :header-rows: 1
   :widths: 12 15 73

   * - RST
     - Address
     - Behaviour
   * - reset
     - ``0000h``
     - ``DI; JMP 00CAh`` (boot)
   * - 1
     - ``0008h``
     - ``JMP 0392h``: **timer tick**
   * - 2
     - ``0010h``
     - ``JMP 0E31h``: **aux UART**
   * - 3
     - ``0018h``
     - ``EI; RET``
   * - 4
     - ``0020h``
     - ``JMP 07A2h``: **console UART**
   * - 5, 6, 7
     - ``0028h``-``0038h``
     - ``EI; RET``
   * - TRAP
     - ``0024h``
     - ``JMP F000h`` (debugger, external)

Both UART ISRs read the 8251 status and branch on bits 0 and 1: RxRDY goes to
the receive handler and TxRDY to the transmit handler. The transmitter is
switched on only while there is something to send, so the interrupt model in an
emulator must raise RST 2 or RST 4 *while* a UART has received data, or has its
transmitter enabled and empty.

Boot sequence
-------------

1. ``0000h``: ``DI``, jump to ``00CAh``.
2. Write ``0`` to ``FEh``, read ``FFh``.
3. Zero RAM ``4000h``-``4BB1h``, set SP to ``4908h``.
4. Patch the two RAM I/O stubs (``48EEh``, ``48F1h``).
5. Initialise the console UART (``03h, 53h, 7Ah, 26h``) and the aux UART
   (``03h, 53h, 6Fh, 16h``), updating bits in ``FEh`` as it goes. The CRC
   tables are built at the same time.
6. Initialise the SPC/1 runtime (``1219h``): allocate the I/O images and
   tables from the configuration at ``2114h``, set the user entry to ``807Ch``,
   copy the function table from ``2800h`` to ``7F5Fh``.
7. Write ``0`` to ports ``40h``-``4Ah`` (analog module mux selects).
8. Enable the console transmitter (``27h`` to ``61h``).
9. Create the eight start-up processes from the table at ``01F5h`` and start
   the scheduler.

The kernel (IPC/1)
------------------

Processes
^^^^^^^^^

The table at ``01F5h``-``026Ch`` holds eight 15-byte entries: PCB address,
priority (0 is highest), two queue pointers and a word, four id bytes and the
entry point.

.. list-table::
   :header-rows: 1
   :widths: 14 10 76

   * - Entry
     - Prio
     - Role
   * - ``02C7h``
     - 0
     - Clock process. Waits for the 5-tick semaphore (``4047h``), writes
       port ``0Ah`` and keeps time counters.
   * - ``09CFh``
     - 3
     - Operator dialog (menu on the console).
   * - ``056Eh``
     - 8
     - Idle loop.
   * - ``13D4h``
     - 3
     - Aux receive: takes frames from the link, accepts only station address
       ``FFh``, posts the message to mailbox ``40BFh``.
   * - ``1E6Bh``
     - 3
     - Aux transmit: takes reply bytes from the ring, builds a frame at
       ``5090h`` and starts the transmit.
   * - ``1456h``
     - 3
     - Aux message handler: takes messages from ``40BFh`` and feeds each
       sub-message to the command interpreter, then streams the replies into
       the transmit ring.
   * - ``151Eh``
     - 3
     - Command interpreter: waits for a command, dispatches through the table
       at ``1CABh``.
   * - ``1FB2h``
     - 4
     - PLC main cycle.

Six more PCB templates at ``026Dh``-``02C6h`` (15 bytes each) are used by the
``P`` command for operator-started processes.

Scheduling
^^^^^^^^^^

* There are 8 ready queues at ``4014h`` + 5 x priority.
* The timer ISR (RST 1) counts ticks, signals the 5-tick semaphore, and
  decrements a time-slice counter that forces a switch when it expires.
* In the emulator tests a process at priority 4 or lower never ran, because the
  PLC cycle process (priority 4) does not block. A busy process at priority 1-3
  ran but also kept the dialog process (priority 3) from running when it was at
  the same priority, so equal priorities did not appear to share time.
  A user process should therefore wait on a semaphore regularly.

API jump table (``0040h``-``00C9h``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A table of ``JMP`` instructions at fixed addresses, used by the function
library and by user code. Entries identified so far:

.. list-table::
   :header-rows: 1
   :widths: 14 24 62

   * - Entry
     - Target
     - Meaning
   * - ``0052h``
     - ``05B9h``
     - Signed divide helper
   * - ``0073h``
     - ``0772h``
     - Copy B bytes from (DE) to (HL)
   * - ``007Ch``
     - ``05A0h``
     - Multiply helper
   * - ``0085h``
     - ``0595h``
     - Test HL (zero)
   * - ``00ACh``
     - ``0490h``
     - Send a node to a mailbox
   * - ``00B2h``
     - ``04AEh``
     - Signal a semaphore (BC = address)
   * - ``00B8h``
     - ``054Fh``
     - Wait on a semaphore (BC = address)
   * - ``00BBh``
     - ``0897h``
     - Read a line from the console
   * - ``00BEh``
     - ``0916h``
     - Send a block to the console
   * - ``00C1h``
     - ``11B1h``
     - Send an aux frame
   * - ``00C4h``
     - ``103Dh``
     - Wait for and return an aux frame

Console and operator dialog
---------------------------

The console is a terminal with ADM-style escape sequences: ``ESC +`` clears the
screen, ``ESC = row col`` positions the cursor (both offset by ``20h``) and
``ESC T`` clears to the end of the line. NUL bytes are sent as padding after
some sequences.

Input handling
^^^^^^^^^^^^^^

The path of a typed character is:

``RST 4`` -> ``console_isr`` (``07A2h``) -> ``console_rx`` (``07E5h``).

* The parity bit is stripped.
* ``ESC`` signals the attention semaphore (``4101h``) if the dialog is waiting
  on it, and aborts a line being read.
* Backspace edits the line, CR ends it, and the limit is 80 characters.
* Typed characters are echoed through the transmit side (``08B6h``).
* A completed line wakes the reader through ``SEM_CON_LINE`` (``48AFh``).

Menu and commands
^^^^^^^^^^^^^^^^^

The dialog process (``09CFh``) draws the menu once and then reads commands
(upper and lower case are accepted):

.. list-table::
   :header-rows: 1
   :widths: 12 88

   * - Key
     - Behaviour
   * - ``C``
     - "Dialog med SPC/1": in this image it only redraws the menu.
   * - ``D``
     - "Hop til debugger": ``DI; CALL F008h``. The debugger ROM is not part
       of the image.
   * - ``P``
     - "Opstart af proces": asks for a priority (1-8, ``INDTAST PRIORITET``)
       and a hexadecimal start address (``INDTAST STARTADRESSE``), then takes
       one of six PCB templates and starts the process. With none free it prints
       ``INGEN PROCESKONTROLBLOKKE LEDIGE``. Afterwards the dialog waits for ESC,
       then clears the screen and redraws the menu (without the title line).
   * - other
     - ``INDTASTNINGSFEJL !``, then the prompt ``KOMMANDO :`` again.

The aux link
------------

Link layer
^^^^^^^^^^

.. code-block:: text

   7E  LEN  ADDR  N  sub-message...  CRC-hi CRC-lo  7E

* ``7Eh`` is the frame flag.
* ``LEN`` counts itself and everything up to, but not including, the CRC bytes.
* The bytes ``40h``, ``7Eh``, ``06h``, ``15h`` and ``1Bh`` are never sent
  as such. Each is sent as ``40h K C`` where ``K xor C`` is the original
  byte (the table at ``1201h``: ``40h``: F0 B0, ``7Eh``: F0 8E, ``06h``: FF F9,
  ``15h``: FF EA, ``1Bh``: FF E4).
* Single ``06h`` and ``15h`` bytes outside frames are ACK and NAK.
* The CRC is a table-driven 16-bit CRC. The two tables (built at ``2556h``)
  are the reflected 8408h polynomial. The update at ``253Dh`` is
  ``idx = byte xor hi; hi = T1[idx] xor lo; lo = T2[idx]``, where ``T1`` holds
  the *low* bytes and ``T2`` the *high* bytes of the table values. The register
  starts at 0 and covers the length byte, the data and the CRC itself. A frame
  is good when the final value is 0, with the CRC sent high byte first.
* The receive status returned to the aux receive process is 0 for a good
  frame, 1 for a line error, 2 for a frame that is too long (inferred), 3 for a short
  frame and 4 for a CRC error.
* The receiver accepts a frame only if ``ADDR`` equals ROM byte ``27FFh``
  (``FFh``).

Message layer
^^^^^^^^^^^^^

A request is ``ADDR N`` followed by *N* sub-messages. Each sub-message is
``len code args...`` where ``len`` counts itself.

The first frame after reset only triggers a start-up reply. After that the
reply to a request is built like this:

.. code-block:: text

   LEN  ADDR  02  03 79 00  <reply sub-messages>  00

* ``03 79 00`` acknowledges the frame.
* Every reply sub-message is ``len code data...`` where ``code`` is the command
  code.
* The final ``00`` closes the list.
* An unknown command code gets the reply ``03 3B 00``.

The ROM also sends an unprompted pair ``03 79 00 03 7A 00 00`` (the "start-up"
announcement) in the reply to the first frame.

Commands
^^^^^^^^

The command code, masked with ``7Fh``, indexes a 128-word jump table at
``1CABh``. Replies seen in the emulator:

.. list-table::
   :header-rows: 1
   :widths: 12 18 70

   * - Code
     - Handler
     - Observed behaviour
   * - ``02h``, ``04h``
     - ``153Dh``
     - Image bit access; reply 2 bytes.
   * - ``07h``
     - ``159Fh``
     - Reply 5 zero bytes.
   * - ``0Ah``-``0Dh``
     - ``15DCh``, ``1617h``
     - Reply 2 bytes.
   * - ``0Eh``
     - ``1656h``
     - Never answers; the command interpreter is blocked afterwards. Probably
       waits for an event.
   * - ``0Fh``
     - ``1688h``
     - Reply 5 zero bytes (status).
   * - ``1Eh``
     - ``16D4h``
     - **Download a program block** (see below).
   * - ``20h``
     - ``1756h``
     - **Run control**: argument 0 stops, 1 runs (after loading), 2 restarts
       the system.
   * - ``34h``, ``5Fh``
     - ``17B5h``
     - Reply 2 bytes.
   * - ``3Ah``
     - ``17E3h``
     - Restart the system (``JMP 0000h``).
   * - ``40h``, ``41h``, ``43h``
     - ``17FBh``
     - Read from the input image, output image or marker image (inferred);
       3-byte reply.
   * - ``42h``, ``44h``
     - ``1935h``
     - 1-byte reply.
   * - ``45h``, ``59h``, ``47h``
     - ``19C8h``, ``1A68h``
     - 5-byte reply.
   * - ``60h``
     - ``1B00h``
     - Reply carries the version string ``88.03.14``.
   * - ``61h``
     - ``1B40h``
     - Reply carries the function table words from ``2802h``.
   * - ``6Dh``
     - ``1BA4h``
     - Reply carries the I/O configuration table (``2114h``).
   * - ``6Eh``
     - ``1C00h``
     - Five bytes ``82h``: the digital input groups.
   * - ``6Fh``
     - ``1C21h``
     - Two bytes ``83h``: the digital output groups.
   * - ``70h``
     - ``1C4Dh``
     - Module table reply.
   * - ``79h``, ``7Ah``
     - ``1C6Eh``
     - Acknowledge and start-up replies.
   * - anything else
     - ``17E6h``
     - Illegal command, reply code ``3Bh``.

The PLC runtime (SPC/1)
-----------------------

I/O configuration
^^^^^^^^^^^^^^^^^

The table at ``2114h`` is a list of (type, base port) pairs ending in ``FFFFh``:

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Type
     - Base ports
     - Meaning
   * - ``02h``
     - ``20h``, ``24h``, ``28h``, ``2Ch``, ``30h``
     - Digital input groups: 4 ports (32 points) each, 160 inputs in total.
   * - ``03h``
     - ``10h``, ``14h``
     - Digital output groups: 4 ports each, 64 outputs in total.
   * - ``04h``
     - ``40h``, ``42h``, ``44h``, ``46h``, ``48h``, ``4Ah``
     - Analog input modules.

Main cycle
^^^^^^^^^^

The process at ``1FB2h`` loops forever:

1. Scan the input table (``2296h`` reads four ports per group, inverts them and
   updates the input image).
2. Scan the analog modules (``2033h``).
3. If the PLC state ``4C02h`` is 3, call the user program at ``4BD5h``
   (``1FDFh``).
4. Write the outputs (``2303h``).

A scan cycle takes about 7,700 emulated instructions.

Process images
^^^^^^^^^^^^^^

Each digital point has one byte in the image, with the current state in bit 0 and
the previous state (for edge detection) in bit 1; an active input appears as
``03h`` after one scan. The images are at ``5A55h`` (inputs) and ``52D5h``
(outputs) after boot. Point *n* of the first group is bit *n* of port ``20h``
(inputs) or ``10h`` (outputs).

Analog scan
^^^^^^^^^^^

For each module the firmware writes the current mux channel (0-7, advancing once
per scan) to the module's even port, writes the odd port as a start strobe, waits
for bit 4 of the odd port, then reads the even port (high byte) and the odd port
(bits 7:6 carry the low two bits). The results go to a table of 4-byte records
starting near ``77F0h``. In the emulator model a value of *v* is stored as
``(v >> 2) * 128``, so the exact bit packing and scaling in the ROM is not yet
understood.

Program download and loader
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A program is downloaded with command ``1Eh``. Each block is the sub-message
``len 1E block-no more data...``:

* block number 0 resets the load pointer (``4C00h``) to ``8000h``;
* the reply is ``1E block-no state 00``;
* a block with ``more = 0`` is the last one and sets the PLC state to 1
  ("loaded");
* the image has a 7Ch-byte header area at ``8000h`` and the code starts at
  ``807Ch``.

Command ``20h`` with argument 1 starts the program. The loader at ``2359h``
first relocates the code **in place** and then sets the state to 3 ("running").
The loader works as follows:

* ``LXI H`` operands are split into a segment nibble and a 12-bit offset. The
  segment selects a base address from the table at ``4BB4h`` (1 = output image,
  2 = input image) and the operand becomes the absolute address.
* ``CALL n`` operands are function numbers; they are replaced with the entry of
  function *n* from the table at ``4BD3h`` (the RAM copy of ``2800h``).
  An unresolved number is an error.
* ``JMP``/``JZ``/``JNZ`` operands are relative and become absolute.
* Opcodes tested as accepted: ``LXI H``, ``CMA``, ``MVI A``, ``MOV B,A``,
  ``MOV D,L``, ``MOV M,A``, ``MOV A,B``, ``MOV A,M``, ``ANA B``, ``ANA M``,
  ``ORA B``, ``ORA M``, ``RNZ``, ``RZ``, ``JNZ``, ``JMP``, ``JZ``, ``RET``,
  ``ANI``, ``POP PSW``, ``PUSH PSW`` and ``CALL``. Other opcodes made the
  loader report an error in my tests.

This is boolean-logic code: load a point address, read the byte, combine,
store it back. A tested program that copies input point 0 to output point 0 is:

.. code-block:: text

   21 00 20    LXI H,<input image, offset 0>
   7E          MOV A,M
   21 00 10    LXI H,<output image, offset 0>
   77          MOV M,A
   C9          RET

After relocation the operands become ``21 55 5A`` and ``21 D5 52``. With port
``20h`` bit 0 pulled low, port ``10h`` bit 0 goes high on the next cycle.

Function library (FUNK)
^^^^^^^^^^^^^^^^^^^^^^^

The table at ``2800h``-``287Fh`` has 64 words. Word *n* is the entry of function
block *n* (0000h = not implemented). 23 entries are used (numbers 01-0A,
10-12, 14-1A, 1C, 1E, 1F). The code runs from ``2880h`` to ``3FFFh``; the last
function (``316Ch``) is about 3.7 KB long.

Calling convention (inferred from the entry code):

* the accumulator, bit 0, carries the condition from the preceding logic;
  most functions begin ``ANI 01h; RZ``, so they act only when it is set;
* the return address on the stack points to an **inline parameter block**
  after the ``CALL``; the function does ``POP H; PUSH H`` and then steps over
  the block with ``INX H``;
* a helper at ``3775h`` resolves operand addresses;
* state for each block is kept in the inline block.

What each function block does (timer, counter, arithmetic, ...) has not been
determined.

The emulator
------------

The package ``id7000_sps_emu`` contains:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - File
     - Purpose
   * - ``cpu8080.py``
     - 8080 core (documented opcodes), unchanged from the board 5 emulator.
   * - ``machine.py``
     - ROM and RAM, both 8251s, timer tick, interrupt generation, analog
       modules, digital I/O helpers (``set_din``, ``dout``).
   * - ``aux.py``
     - Host side of the aux link: frame builder with the ROM-exact CRC and
       byte stuffing, ``AuxHost`` with ``connect()`` and ``command()``.
   * - ``terminal.py``
     - Small ADM-style terminal that renders the console screen.
   * - ``demo_console.py``
     - Boot, menu, ``P`` command, ESC, invalid command.
   * - ``demo_plc.py``
     - Aux link, download, run, digital and analog I/O.
   * - ``sps_funk_image.bin``
     - The combined 16 KB image.

Console demo output (excerpt):

.. code-block:: text

                        VELKOMMEN TIL IPC/1 OPERATIVSYSTEMET
                         VÆLG IMELLEM  FØLGENDE KOMMANDOER:
                             'C'- DIALOG  MED SPC/1
                             'D'- HOP TIL  DEBUGGER
                             'P'- OPSTART AF PROCES

   KOMMANDO :

PLC demo output:

.. code-block:: text

   version (60h)    -> [(121, b'\x00'), (96, b'\x00\x0088.03.14\x00')]
   run (20h,1)      -> [(121, b'\x00'), (32, b'\x01\x00')] | PLC_STATE = 3
   relocated code   -> 21 55 5a 7e 21 d5 52 77 c9
   input 0 active   -> output 0 = True   (port 20h=FE, port 10h=01)

Model details that matter
^^^^^^^^^^^^^^^^^^^^^^^^^

* RST 1 is raised every ``TICK = 4000`` steps (a guess at the tick rate).
* RST 4 is raised while the console UART has received data (and the
  receiver is on) or has its transmitter enabled. RST 2 does the same for the
  aux UART.
* The first aux frame only produces the start-up reply; a command must be sent
  in a later frame.
* A user process started with ``P`` should wait on a semaphore (for example the
  tick semaphore ``4047h`` through API ``00B8h``). A busy loop at the same or a
  higher priority starves the dialog.

Comparison with the board 5 image
---------------------------------

Both images are 8080 firmware for the ID-7000 and share the same hardware
family.

.. list-table::
   :header-rows: 1
   :widths: 24 38 38

   * - Aspect
     - Board 5 (terminal concentrator)
     - IPC/1 + SPC/1 (PLC)
   * - Console UART
     - 12 x 8251 at ``60h``-``77h``, 7E2 x16
     - ``60h``/``61h``, 7E1 x16
   * - Reset sequence
     - ``03h, 53h`` then mode, command
     - same ``03h, 53h`` pattern
   * - Other serial
     - Sync 8251 at ``A0h``/``A1h`` (Cyber link, SYN, odd parity)
     - Async 8251 at ``08h``/``09h`` (HDLC-like frames, CRC-16)
   * - Timer
     - RST 3, ``IN FFh``
     - RST 1, ``IN FFh``
   * - System latch
     - ``FEh``, bits 2 and 4
     - ``FEh``, bits 1, 2 and 4
   * - Other I/O
     - 8255 printer port at ``50h``-``53h``
     - Digital and analog I/O at ``10h``-``4Bh``
   * - Software model
     - Interrupt-driven, one idle loop
     - Preemptive multitasking kernel with semaphores
   * - RAM
     - ``4000h``-``BFFFh`` tested
     - starts at ``4000h``, used up to about ``81xxh``
   * - Terminal
     - ``ESC`` host escapes (``ESC B``, ``ESC A``)
     - ADM-style cursor addressing

Both use ``60h``/``61h`` for the console and ``FEh``/``FFh`` for the latch and
tick acknowledge, and both pad vectors with ``76h``. The code is otherwise
unrelated.

Open questions
--------------

* What command codes ``02h``-``0Fh``, ``34h``, ``40h``-``47h``, ``59h`` and
  ``5Fh`` do exactly, and why ``0Eh`` never answers.
* The exact bit packing and scaling of the analog values, and what port
  ``0Ah`` does.
* What each function block (01-1F) computes and how its inline parameter
  block is laid out.
* The structure of the loader opcode table at ``24B0h`` and the PCB template
  fields.
* The real tick rate, the RAM size and the meaning of the ``FEh`` bits.
* Whether equal-priority processes are ever time-sliced.
* What the ``C`` command was meant to do, and what the missing debugger at
  ``F000h`` provides.

Appendix: key addresses
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Address
     - Routine or data
   * - ``0040h``
     - API jump table
   * - ``00CAh``
     - Boot
   * - ``01F5h``
     - Start-up process table
   * - ``026Dh``
     - Dynamic PCB templates
   * - ``0392h``
     - Timer ISR
   * - ``07A2h``
     - Console ISR
   * - ``0916h``
     - Console put block
   * - ``09CFh``
     - Operator dialog process
   * - ``0C9Dh``
     - Console text
   * - ``0E31h``
     - Aux UART ISR
   * - ``0EAEh``
     - Aux receive state machine
   * - ``103Dh``
     - Receive a frame
   * - ``1201h``
     - Byte-stuffing table
   * - ``1219h``
     - SPC/1 initialisation
   * - ``13D4h``
     - Aux receive process
   * - ``1456h``
     - Aux message process
   * - ``151Eh``
     - Command interpreter
   * - ``16D4h``
     - Download command
   * - ``1756h``
     - Run control command
   * - ``1CABh``
     - Command jump table
   * - ``1E6Bh``
     - Aux transmit process
   * - ``1FB2h``
     - PLC main cycle
   * - ``2114h``
     - I/O configuration table
   * - ``2296h``
     - Digital input scan
   * - ``2303h``
     - Digital output scan
   * - ``2359h``
     - Program loader
   * - ``253Dh``
     - CRC update
   * - ``2556h``
     - CRC table build
   * - ``27FFh``
     - Station address byte
   * - ``2800h``
     - Function pointer table
   * - ``2880h``
     - Function library
