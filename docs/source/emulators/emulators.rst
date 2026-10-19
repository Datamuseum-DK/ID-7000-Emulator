=========
Emulators
=========

Two emulators have been in use for this project. One is based on 
a similar project for the Q1 Microlite micro computer.

Most of the fundamentals are identical and rather than duplicating
the documentation effort we refer to:

https://q1-lite-emulator.readthedocs.io/en/latest/

But for ID-7000A the novel thing is that I have been prompting 
Claude to help with the reverse engineering.

This turned out to provide results much faster than I am able to 
do.

This has resulted in the development of a new i8080 emulator. While 
being very similar in the ideas I used it is currently smaller in 
size, fully written in python and has some nicer abstractions.

It was used by Claude to test its guesses and could be used as the 
basis for further developments of ID-7000 A. So far I didn't repeat the 
exercise for ID-7000 SPS/FUNK.
