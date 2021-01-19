

#include <stdlib.h>
#include <stdint.h>


typedef enum Command {
	NOOP = 1,
	EXIT = 2,
	PUSH = 3,
	DUP = 4,
	DROP = 5,
	UNDROP = 6,
	SWAP = 7,
	JUMP = 8,
	JUMPIFZ = 9,
	GETSTACK = 10,
	SETSTACK = 11,
	MOVEFROM = 12,
	MOVETO = 13,
	MEMMOVE = 14,
	ADD = 16,
	NEG = 17,
	MULT = 18,
	DIV = 19,
	MOD = 20,
	BITOR = 21,
	BITAND = 22,
	SHIFTUP = 23,
	NOT = 24,
	NEGATIVE = 25,
	PUTCHAR = 32,
	GETCHAR = 33,
	MEMSIZE = 48
} Command;

typedef struct Execution {
	size_t code_ptr;
	size_t stack_ptr;
	uint32_t *mem;
} Execution;

typedef enum Result{
	Ok,
	Error,
	Stop
} Result;


Result run(uint32_t *code, size_t codelen);



