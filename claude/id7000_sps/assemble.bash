#!/bin/bash

PRGS="ctr32 fib fib_noname fib_plc"
for prg in $PRGS
do
  echo "Assemble $prg.asm"
  python asm8080.py examples/$prg.asm --hex examples/$prg.hex
done
