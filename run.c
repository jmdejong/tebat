
#include <stdio.h>
#include <string.h>
#include "run.h"


const size_t MEM_SIZE = 1<<27;
const size_t INITIAL_MEM_SIZE = 1 << 27;


Execution Execution_new(uint32_t *code, size_t codelen){
	
	uint32_t *mem = malloc(sizeof(uint32_t) * INITIAL_MEM_SIZE);
	size_t code_ptr = code[1];
	size_t stack_ptr = code[2];
	memcpy(mem, code, codelen * sizeof(uint32_t));
	Execution ex = {code_ptr, stack_ptr, INITIAL_MEM_SIZE, mem};
	return ex;
}



static inline Result run_instr(Execution *ex, int8_t *errcode){
	if (ex->code_ptr < 1 || ex->stack_ptr < 1 || ex->code_ptr > (1<<19) || ex->stack_ptr > (1<<19)){
		printf("code or stack ptr incorrect: %ld %ld\n", ex->code_ptr, ex->stack_ptr);
		return Error;
	}
	Command command = ex->mem[ex->code_ptr];
	++(ex->code_ptr);
	uint32_t tmp, amount, *src, *dest, val, *newmem;
	int inchar;
	int32_t returncode;
	switch(command){
		case NOOP:
			return Ok;
		case EXIT:
			returncode = (int32_t)ex->mem[--ex->stack_ptr];
			*errcode = returncode;
			return Stop;
		case PUSH:
			ex->mem[ex->stack_ptr++] = ex->mem[ex->code_ptr++];
			return Ok;
		case DUP:
			ex->mem[ex->stack_ptr] = ex->mem[ex->stack_ptr-1];
			++ex->stack_ptr;
			return Ok;
		case DROP:
			--ex->stack_ptr;
			return Ok;
		case UNDROP:
			++ex->stack_ptr;
			return Ok;
		case SWAP:
			tmp = ex->mem[ex->stack_ptr-(2)];
			ex->mem[ex->stack_ptr-(2)] = ex->mem[ex->stack_ptr-(1)];
			ex->mem[ex->stack_ptr-(1)] = tmp;
			return Ok;
		case JUMP:
			ex->code_ptr = ex->mem[ex->stack_ptr - 1];
			--ex->stack_ptr;
			return Ok;
		case JUMPIFZ:
			if (ex->mem[ex->stack_ptr - 2] == 0){
				ex->code_ptr = ex->mem[ex->stack_ptr - 1];
			}
			ex->stack_ptr -= 2;
			return Ok;
		case GETSTACK:
			ex->mem[ex->stack_ptr] = ex->stack_ptr;
			++ex->stack_ptr;
			return Ok;
		case SETSTACK:
			ex->stack_ptr = ex->mem[ex->stack_ptr - 1];
			return Ok;
		case MOVEFROM:
			val = ex->mem[ex->stack_ptr - 1];
			if (val < 1 || val >= MEM_SIZE){
				printf("move from invalid address %d\n", val);
				return Error;
			}
			ex->mem[ex->stack_ptr - 1] = ex->mem[val];
			return Ok;
		case MOVETO:
			val = ex->mem[ex->stack_ptr - 1];
			if (val < 1 || val >= MEM_SIZE){
				printf("move to invalid address %d\n", val);
				return Error;
			}
			ex->mem[val] = ex->mem[ex->stack_ptr - 2];
			ex->stack_ptr -= 2;
			return Ok;
		case MEMMOVE:
			amount = ex->mem[ex->stack_ptr - 3];
			src = &ex->mem[ex->mem[ex->stack_ptr - 2]];
			dest = &ex->mem[ex->mem[ex->stack_ptr - 1]];
			
			if (ex->mem[ex->stack_ptr-1] < 1 || ex->mem[ex->stack_ptr-1] + amount >= MEM_SIZE || ex->mem[ex->stack_ptr-2] < 1 || ex->mem[ex->stack_ptr-2] + amount >= MEM_SIZE){
				printf("ex->memmove to invalid address: %d %d\n", ex->mem[ex->stack_ptr-1], ex->mem[ex->stack_ptr-2]);
				return Error;
			}
			memcpy(dest, src, sizeof(uint32_t) * amount);
			ex->stack_ptr -= 3;
			return Ok;
		case ADD:
			ex->mem[ex->stack_ptr - 2] = (ex->mem[ex->stack_ptr - 2] + ex->mem[ex->stack_ptr - 1]);
			ex->stack_ptr -= 1;
			return Ok;
		case NEG:
			ex->mem[ex->stack_ptr - 1] = (uint32_t)-(int32_t)ex->mem[ex->stack_ptr - 1];
			return Ok;
		case MULT:
			ex->mem[ex->stack_ptr - 2] = (ex->mem[ex->stack_ptr - 2] * ex->mem[ex->stack_ptr - 1]);
			ex->stack_ptr -= 1;
			return Ok;
		case DIV:
			if (ex->mem[ex->stack_ptr-1] == 0){
				printf("division by zero\n");
				return Error;
			}
			ex->mem[ex->stack_ptr - 2] /= ex->mem[ex->stack_ptr-1];
			ex->stack_ptr -= 1;
			return Ok;
		case MOD:
			if (ex->mem[ex->stack_ptr-1] == 0){
				printf("division remainder by zero\n");
				return Error;
			}
			ex->mem[ex->stack_ptr - 2] %= ex->mem[ex->stack_ptr-1];
			ex->stack_ptr -= 1;
			return Ok;
		case BITOR:
			ex->stack_ptr -= 1;
			ex->mem[ex->stack_ptr - 1] = (ex->mem[ex->stack_ptr] | ex->mem[ex->stack_ptr - 1]);
			return Ok;
		case BITAND:
			ex->stack_ptr -= 1;
			ex->mem[ex->stack_ptr - 1] = (ex->mem[ex->stack_ptr] & ex->mem[ex->stack_ptr - 1]);
			return Ok;
		case SHIFTUP:
			ex->mem[ex->stack_ptr - 2] <<= ex->mem[ex->stack_ptr - 1];
			ex->stack_ptr -= 1;
			return Ok;
		case SHIFTDOWN:
			ex->mem[ex->stack_ptr - 2] >>= ex->mem[ex->stack_ptr - 1];
			ex->stack_ptr -= 1;
			return Ok;
		case NOT:
			ex->mem[ex->stack_ptr - 1] = !ex->mem[ex->stack_ptr - 1];
			return Ok;
		case NEGATIVE:
			ex->mem[ex->stack_ptr - 1] = (int)ex->mem[ex->stack_ptr - 1] < 0;
			return Ok;
		case MEMSIZE:
			ex->mem[ex->stack_ptr] = ex->mem_size;
			ex->stack_ptr += 1;
			return Ok;
		case BRK:
			newmem = realloc(ex->mem, ex->mem[ex->stack_ptr - 1] * sizeof(uint32_t));
			if (newmem == NULL){
				ex->mem = newmem;
				ex->mem_size = ex->mem[ex->stack_ptr - 1];
			}
			ex->mem[ex->stack_ptr - 1] = newmem != NULL;
		case PUTCHAR:
			putchar(ex->mem[ex->stack_ptr - 1]);
			fflush(stdout);
			ex->stack_ptr -= 1;
			return Ok;
		case GETCHAR:
			inchar = getchar();
			if (inchar == EOF){
				inchar = -1;
			}
			ex->mem[ex->stack_ptr] = inchar;
			ex->stack_ptr += 1;
			return Ok;
		default:
			printf("Invalid command %d\n", command);
			return Error;
	}
	return Ok;
}


Result run(uint32_t *code, size_t codelen){
	if (code[0] != 1415933300){
		printf("Not valid tebat code!\n");
		printf("identifier should be %d but is %d\n", 1415933300, code[0]);
		exit(-1);
	}
	Execution ex = Execution_new(code, codelen);
	Result result;
	int8_t errcode;
	while((result = run_instr(&ex, &errcode)) == Ok) {
	}
	if (result == Error){
		printf("Interpreter error\n");
		errcode = -1;
	}
	free(ex.mem);
	return errcode;
}

