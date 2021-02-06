# Tebat and Temat

Tebat is a stack-based minimal bytecode interpreted language.
This repository currently contains two interpreters for Tebat: one in python and one in C.
These can be found in the files run.py, run.c and run.h
Tebat has 32 bit words as only type.

Temat is a programming language that compiles into tebat.
The script parser.py is a compiler from temat into tebat.
A self-hosted compiler is being created.

An in between form, Tebbat is under consideration too.
Tebbat is like tebat, but each word in the representation also has a tag whether it's a builtin, a literar value, a reference or a label.
Tebbat could possibly be compiled to other (bytecode) languages.

See [tebat_specification.md](tebat_specification.md) for an explanation of the Tebat bytecode language

See [temat.md](temat.md) for an explanation of the temat language.
