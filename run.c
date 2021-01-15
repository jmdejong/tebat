
#include <stdio.h>
#include <string.h>
#include "run.h"

typedef size_t usize;
typedef uint32_t u32;


const usize MEM_SIZE = 1<<20;


#define STACK(n) (mem[stack_ptr-(n)])

int run(u32 *code, size_t codelen){
	u32 *mem = malloc(sizeof(u32) * MEM_SIZE);
	usize code_ptr = code[1];
	usize stack_ptr = code[2];
	memcpy(mem, code, codelen);
	while(1){
		Command command = mem[code_ptr];
		if (code_ptr < 1 || stack_ptr < 1 || code_ptr > (1<<19) || stack_ptr > (1<<19)){
			printf("code or stack ptr incorrect: %ld %ld", code_ptr, stack_ptr);
			free(mem);
			return -1;
		}
		++code_ptr;
		u32 tmp, amount, *src, *dest, val;
		int inchar;
		int32_t returncode;
		switch(command){
		case NOOP:
			break;
		case EXIT:
			returncode = (int32_t)mem[--stack_ptr];
			free(mem);
			return returncode;
		case PUSH:
			mem[stack_ptr++] = mem[code_ptr++];
			break;
		case DUP:
			mem[stack_ptr] = mem[stack_ptr-1];
			++stack_ptr;
			break;
		case DROP:
			--stack_ptr;
			break;
		case UNDROP:
			++stack_ptr;
			break;
		case SWAP:
			tmp = mem[stack_ptr-(2)];
			mem[stack_ptr-(2)] = mem[stack_ptr-(1)];
			mem[stack_ptr-(1)] = tmp;
			break;
		case JUMP:
			code_ptr = mem[stack_ptr - 1];
			--stack_ptr;
			break;
		case JUMPIFZ:
			if (mem[stack_ptr - 2] == 0){
				code_ptr = mem[stack_ptr - 1];
			}
			stack_ptr -= 2;
			break;
		case GETSTACK:
			mem[stack_ptr] = stack_ptr;
			++stack_ptr;
			break;
		case SETSTACK:
			stack_ptr = mem[stack_ptr - 1];
			break;
		case MOVEFROM:
			val = mem[stack_ptr - 1];
			if (val < 1 || val >= MEM_SIZE){
				printf("move from invalid address %d", val);
				free(mem);
				return -1;
			}
			mem[stack_ptr - 1] = mem[val];
			break;
		case MOVETO:
			val = mem[stack_ptr - 1];
			if (val < 1 || val >= MEM_SIZE){
				printf("move to invalid address %d", val);
				free(mem);
				return -1;
			}
			mem[val] = mem[stack_ptr - 2];
			stack_ptr -= 2;
			break;
		case MEMMOVE:
			amount = mem[stack_ptr - 3];
			src = &mem[mem[stack_ptr - 2]];
			dest = &mem[mem[stack_ptr - 1]];
			
			if (mem[stack_ptr-1] < 1 || mem[stack_ptr-1] + amount >= MEM_SIZE || mem[stack_ptr-2] < 1 || mem[stack_ptr-2] + amount >= MEM_SIZE){
				printf("memmove to invalid address: %d %d", mem[stack_ptr-1], mem[stack_ptr-2]);
				free(mem);
				return -1;
			}
			memcpy(dest, src, sizeof(u32) * amount);
			stack_ptr -= 3;
			break;
		case ADD:
			mem[stack_ptr - 2] = (mem[stack_ptr - 2] + mem[stack_ptr - 1]);
			stack_ptr -= 1;
			break;
		case NEG:
			mem[stack_ptr - 1] = (uint32_t)-(int32_t)mem[stack_ptr - 1];
			break;
		case MULT:
			mem[stack_ptr - 2] = (mem[stack_ptr - 2] * mem[stack_ptr - 1]);
			stack_ptr -= 1;
			break;
		case DIV:
			if (mem[stack_ptr-1] == 0){
				free(mem);
				printf("division by zero\n");
				return -1;
			}
			mem[stack_ptr - 2] /= mem[stack_ptr-1];
			stack_ptr -= 1;
			break;
		case MOD:
			if (mem[stack_ptr-1] == 0){
				free(mem);
				printf("division remainder by zero\n");
				return -1;
			}
			mem[stack_ptr - 2] %= mem[stack_ptr-1];
			stack_ptr -= 1;
			break;
		case BITOR:
			stack_ptr -= 1;
			mem[stack_ptr - 1] = (mem[stack_ptr] | mem[stack_ptr - 1]);
			break;
		case BITAND:
			stack_ptr -= 1;
			mem[stack_ptr - 1] = (mem[stack_ptr] & mem[stack_ptr - 1]);
			break;
		case SHIFTUP:
			amount = mem[stack_ptr - 1];
			if (amount > 0){
				mem[stack_ptr - 2] <<= amount;
			} else if (amount < 0){
				mem[stack_ptr - 2] >>= -amount;
			}
			stack_ptr -= 1;
			break;
		case NOT:
			mem[stack_ptr - 1] = !mem[stack_ptr - 1];
			break;
		case NEGATIVE:
			mem[stack_ptr - 1] = (int)mem[stack_ptr - 1] < 0;
			break;
		case MEMSIZE:
			mem[stack_ptr] = MEM_SIZE;
			stack_ptr += 1;
			break;
		case PUTCHAR:
			putchar(mem[stack_ptr - 1]);
			fflush(stdout);
			stack_ptr -= 1;
			break;
		case GETCHAR:
			inchar = getchar();
			if (inchar == EOF){
				inchar = -1;
			}
			mem[stack_ptr] = inchar;
			stack_ptr += 1;
			break;
		default:
			printf("Invalid command %d\n", command);
			free(mem);
			return -1;
		}
	}
	free(mem);
	return 0;
}
