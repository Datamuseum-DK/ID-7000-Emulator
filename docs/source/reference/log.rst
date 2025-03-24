

Log book
========
This project started around November 22, 2024. Some code was quickly put
together based on the building blocks from the Q1 emulator project.

A github repo was created March 20 2025. Log entries before then have been
resonstructed from memory and emails



2024 11 29
----------

Emulator is running. Log entry in danish copied from an email to DDF mailinglist.

.. code-block:: text
  Jeg har kikket i bitarkivet for ID-7000, fundet nogle prom images, nogle datablade, gættet lidt og
  valgt et (forhåbentlig) passende image at starte med.

  Dette image er så forsøgt emuleret med hjælp fra kode genbrugt fra Q1 emulatoren.

  Så vidt jeg kan se kører koden som den skal: RAM bliver initialiseret og der bliver lavet
  RAM og PROM checks.

  Jeg kan f.eks. fremprovokere en fejlmeddelelse ved at fake forkert skrivning i nogle RAM
  adresser:

    4.870: 60 out - 30 (0)
    4.871: 60 out - 07 (.)
    4.871: ** ERROR IN RAM MEMORY DETECTED IN HEX AREA 7000-8000
    4.871: 60 out - 07 (.)

  ID-7000 benytter en masse IO adresser: Der er (initielt) identisk output
  (0x03 0x53 0xfa 0x25 '.S.%') på 12 IO adresser 0x61, 0x63, 0x65, 0x67, 69, 6b, 6d, 6f,71, 73,
  75 og 0x77. Men det er ikke en sekvens der siger mig noget.

  I RAM ser det ud til at der bliver kopieret tekst fra PROM i flere lokationer. Heraf 12 med
  identisk tekst der ligner en prompt:

  42a0 41 5b 43 59 42 45 52 20 4c 49 4e 4b 3a 20 53 49  A[CYBER LINK: SI
  42b0 54 45 20 41 44 44 52 45 53 53 20 31 20 20 20 4e  TE ADDRESS 1   N
  42c0 4f 54 20 41 43 54 49 56 45 5d 1b 41 99 fe 98 fe  OT ACTIVE].A....
  ...
  4f40 5f 1b 41 49 44 2d 37 30 30 30 20 2a 52 45 41 44  _.AID-7000 *READ
  4f50 59 2a 20 28 32 30 30 55 54 2f 53 49 4d 29 20 56  Y* (200UT/SIM) V
  4f60 45 52 53 49 4f 4e 20 30 31 2e 30 32 2e 38 33 1b  ERSION 01.02.83.
  ...
  5360 4f f6 7a 71 4d 1b 41 49 44 2d 37 30 30 30 20 2a O..qM.AID-7000 *
  5370 52 45 41 44 59 2a 20 28 32 30 30 55 54 2f 53 49  READY* (200UT/SI
  5380 4d 29 20 56 45 52 53 49 4f 4e 20 30 31 2e 30 32  M) VERSION 01.02
  5390 2e 38 33 1b 41 f6 34 f6 33 f6 32 f6 31 f6 30 f6 .83.A.4.3.2.1.0.
  ...
  5780 3f f4 3e f4 3d f4 79 71 3b 1b 41 49 44 2d 37 30 ?.>.=.yq;.AID-70
  5790 30 30 20 2a 52 45 41 44 59 2a 20 28 32 30 30 55  00 *READY* (200U
  57a0 54 2f 53 49 4d 29 20 56 45 52 53 49 4f 4e 20 30  T/SIM) VERSION 0
  57b0 31 2e 30 32 2e 38 33 1b 41 f4 22 f4 21 f4 20 f4 1.02.83.A.".!. .
  ...
  5ba0 2f f2 2e f2 2d f2 2c f2 2b f2 78 71 29 1b 41 49 /...-.,.+.xq).AI
  5bb0 44 2d 37 30 30 30 20 2a 52 45 41 44 59 2a 20 28  D-7000 *READY* (
  5bc0 32 30 30 55 54 2f 53 49 4d 29 20 56 45 52 53 49  200UT/SIM) VERSI
  5bd0 4f 4e 20 30 31 2e 30 32 2e 38 33 1b 41 f2 10 f2  ON 01.02.83.A...
  ...
  5fd0 17 1b 41 49 44 2d 37 30 30 30 20 2a 52 45 41 44  ..AID-7000 *READ
  5fe0 59 2a 20 28 32 30 30 55 54 2f 53 49 4d 29 20 56  Y* (200UT/SIM) V
  5ff0 45 52 53 49 4f 4e 20 30 31 2e 30 32 2e 38 33 1b  ERSION 01.02.83.
  ...
  63f0 07 ee 76 71 05 1b 41 49 44 2d 37 30 30 30 20 2a ..vq..AID-7000 *
  6400 52 45 41 44 59 2a 20 28 32 30 30 55 54 2f 53 49  READY* (200UT/SI
  6410 4d 29 20 56 45 52 53 49 4f 4e 20 30 31 2e 30 32  M) VERSION 01.02
  6420 2e 38 33 1b 41 ed ec ed eb ed ea ed e9 ed e8 ed .83.A...........
  ...
  6810 f7 eb f6 eb f5 eb 75 71 f3 1b 41 49 44 2d 37 30 ......uq..AID-70
  6820 30 30 20 2a 52 45 41 44 59 2a 20 28 32 30 30 55  00 *READY* (200U
  6830 54 2f 53 49 4d 29 20 56 45 52 53 49 4f 4e 20 30  T/SIM) VERSION 0
  6840 31 2e 30 32 2e 38 33 1b 41 eb da eb d9 eb d8 eb 1.02.83.A.......
  ...
  6c30 e7 e9 e6 e9 e5 e9 e4 e9 e3 e9 74 71 e1 1b 41 49 ..........tq..AI
  6c40 44 2d 37 30 30 30 20 2a 52 45 41 44 59 2a 20 28  D-7000 *READY* (
  6c50 32 30 30 55 54 2f 53 49 4d 29 20 56 45 52 53 49  200UT/SIM) VERSI
  6c60 4f 4e 20 30 31 2e 30 32 2e 38 33 1b 41 e9 c8 e9  ON 01.02.83.A...
  ...
  7060 cf 1b 41 49 44 2d 37 30 30 30 20 2a 52 45 41 44  ..AID-7000 *READ
  7070 59 2a 20 28 32 30 30 55 54 2f 53 49 4d 29 20 56  Y* (200UT/SIM) V
  7080 45 52 53 49 4f 4e 20 30 31 2e 30 32 2e 38 33 1b  ERSION 01.02.83.
  ...
  7470 c7 e5 c6 e5 c5 e5 c4 e5 c3 e5 c2 e5 c1 e5 c0 e5 ................
  7480 bf e5 72 71 bd 1b 41 49 44 2d 37 30 30 30 20 2a ..rq..AID-7000 *
  7490 52 45 41 44 59 2a 20 28 32 30 30 55 54 2f 53 49  READY* (200UT/SI
  74a0 4d 29 20 56 45 52 53 49 4f 4e 20 30 31 2e 30 32  M) VERSION 01.02
  74b0 2e 38 33 1b 41 e5 a4 e5 a3 e5 a2 e5 a1 e5 a0 e5 .83.A...........
  ...
  78a0 af e3 ae e3 ad e3 71 71 ab 1b 41 49 44 2d 37 30 ......qq..AID-70
  78b0 30 30 20 2a 52 45 41 44 59 2a 20 28 32 30 30 55  00 *READY* (200U
  78c0 54 2f 53 49 4d 29 20 56 45 52 53 49 4f 4e 20 30  T/SIM) VERSION 0
  78d0 31 2e 30 32 2e 38 33 1b 41 e3 92 e3 91 e3 90 e3 1.02.83.A.......
  ...
  7cc0 9f e1 9e e1 9d e1 9c e1 9b e1 70 71 99 1b 41 49 ..........pq..AI
  7cd0 44 2d 37 30 30 30 20 2a 52 45 41 44 59 2a 20 28  D-7000 *READY* (
  7ce0 32 30 30 55 54 2f 53 49 4d 29 20 56 45 52 53 49  200UT/SIM) VERSI
  7cf0 4f 4e 20 30 31 2e 30 32 2e 38 33 1b 41 e1 80 e1  ON 01.02.83.A...

  Det ser ud til at systemet nu venter på en passende interrupt, men jeg har endnu ikke
  findet nogen beskrivelse af dette.

  Inden jeg kører videre ud af en tangent skal jeg lige høre om der er nogen der allerede har
  opnået lignende resultater, om dette har interesse,  og om der er nogen der ved lidt mere
  om systemet?
