<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

The Library of Babel is a hypothetical library containing every possible book, every combination of letters. Of course, this chip does not have the space to store all those combinations. One way to generate this is through pseudorandom number generation, given a seeded initial state. This is a 5 bit sequential random number generator using an random function (and arbitrary combination bit swapping, XOR, and addition; I will add the function once it's finalized). It is possible that some particular seed will result in the first page of shakespeare, but the majority of text generated will be noise, meaningless text.

## How to test

Each page of numbers is generated after resetting the module. The lower 5 bits of the input/output pinout correspond to the pseudorandom character generation. It is mapped as a-z for the first 26 binary numbers, and then " .,!?;" special characters for the remaining 6 numbers (26-31). To seed the generation, after reset is driven low, it reads the first 5 bits every clock given it is enabled ("enable input", ui[5] is high). After that, it will generate random numbers for a fixed duration until it stops ("output valid", uo[5] drops low).

## External hardware

None
