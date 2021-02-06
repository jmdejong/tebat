
# Tebat specification

Tebat is a stack based bytecode language that works on 32 bit words.
Each command itself is a 32 bit word.

## Tebat file structure

The first word in a tebat file the magic number 1415933300.
If the first word is 1953326420 then the endianness is wrong and should be changed.

The second word is the initial value for the code pointer.
This is the address from which the code will start executing.

The third word is the initial value of the stack pointer.
A reasonable amount of memory should be reserved after this address.

The words after this are unused, up to the address that is store in the code pointer.
These words could be given use in further versions, for example to denote dialect, version, or compression schema.

## Execution model

Tebat is very much stack based.
The stack pointer points to the first address that is not in use by the stack
The "top of the stack" refers to the address that is one smaller than the stack pointer.
Pushing some value to the stack means putting that value in the address pointed to by the stack pointer, and then incrementing the stack pointer.
Taking/popping a value from the stack means decrementing the stack pointer, and usually it also means doing something with the value that the stack pointer now points to.


## Tebat commands

### NOOP
Code: 1

does not do anything

### Exit
Code: 2

End the execution.
Give the top of the stack as return value

### PUSH
Code: 3
Push the next word in the code as a literal value on the top of the stack.

### DUP
Code: 4

Duplicate the top value of the stack

### DROP
Code: 5

Take a value from the top of the stack and ignore it.
This value should not be changed until a later command overwrites it.

### UNDROP
Code: 6

Increment the stack pointer.
This will put whatever is in memory beyond the stack top on top of the stack.
This can be dangerous and should only be used in a very controlled setting (typically only in combination with DROP and SWAP)

### SWAP
Code: 7

Take 2 value from the stack an push them back on the stack in reverse order

### JUMP
Code: 8

Take a value from the top of the stack and set the code pointer to that value.
The value being pointed at is the address of the next instruction to execute.

This instruction may be removed later since in can also be done with the sequence `PUSH 0 SWAP JUMPIFZ`.

### JUMPIFZ
Code: 9

Like JUMP, but will only perform the jump if the value below the top of this stack is 0
This value will be popped from the stack too.

### GETSTACK
Code: 10

Take the current value of the stack pointer and push it on top of the stack.
The increment of the stack pointer happens after taking the value of the stack pointer

### SETSTACK
Code: 11

Take the value on top of the stack and set the stack pointer to that value

### MOVEFROM
Code: 12

Take a value from the top of the stack and push the value in the memory address that this value points to on top of the stack


### MOVETO
Code: 13

Take 2 values from the top of the stack. Move the value below the top to the address in the top value

### MEMMOVE
Code: 14


Take 3 values from the stack.
The top value is the destination address, the value below that is the source address and the value below that is the length.
Move the words in the region that starts at the source address to the region that starts at de destination address.

This is similar to `memcpy` in C's string.h, not `memmove` (it may or may not work correctly when the memory areas overlap).

### ADD
Code: 16

Take 2 words from the top of the stack and push their sum to the stack (all words are treated as unsigned integers)

### NEG
Code: 17

Take a word from the top of the stack and push its negative value to the stack

### MULT
Code: 18

Take 2 words from the top of the stack and push their product to the stack (all words are treated as unsigned integers)

### DIV
Code: 19

Divide the value below the top by the value on top of the stack (all words are treated as unsigned integers).
Division by zero is an error.
Decrement the stack pointer.

### MOD
Code: 20

Make the value below the top of the stack into the the division remainder of that value when divided by the value on top of the stack (all words are treated as unsigned integers).
Division by zero is an error.
Decrement the stack pointer.

### BITOR
Code: 21

Take 2 words from the top of the stack and push their bitwise or to the stack (all words are treated as unsigned integers)

### BITAND
Code: 22

Take 2 words from the top of the stack and push their bitwise and to the stack (all words are treated as unsigned integers)

### SHIFTUP
Code: 23


Multipy the value below the top of the stack by 2 to the power of the value on top of the stack (all words are treated as unsigned integers)


### SHIFTDOWN
Code: 24

Divide the value below the top of the stack by 2 to the power of the value on top of the stack (all words are treated as unsigned integers)

### NOT
Code: 25

Take a value from the top of the stack. If it is zero, push one. Otherwise, push zero.

### NEGATIVE
Code: 26

Take a value from top of the stack. If the highest bit is set: push one, otherwise: push zero.

### PUTCHAR
Code: 32

Take a value from top of the stack and print it as a character to stdout

### GETCHAR
Code: 33

Take a character from stdin and push it on top of the stack

### MEMSIZE
Code: 48

Push the size of the available memory on top of the stack.

### BRK
Code: 49

Try to grow the memory to the size that is specified in the value on top of the stack
