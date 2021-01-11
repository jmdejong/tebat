#!/usr/bin/env python3

import base64
import sys

class Commands:
	NOOP = 1
	EXIT = 2
	PUSH = 3
	DUP = 4
	DROP = 5
	UNDROP = 6
	SWAP = 7
	JUMP = 8
	JUMPIFZ = 9
	GETSTACK = 10
	SETSTACK = 11
	MOVEFROM = 12
	MOVETO = 13
	MEMMOVE = 14
	ADD = 16
	NEG = 17
	MULT = 18
	DIV = 19
	MOD = 20
	BITOR = 21
	BITAND = 22
	SHIFTUP = 23
	NOT = 24
	NEGATIVE = 25
	PUTCHAR = 32
	PUTINT = 33
	MEMSIZE = 48



MEM_SIZE = 2**16


command_code_to_str = {code: name for name, code in Commands.__dict__.items() if name[0] != "_"}
	

def run(code, debug=False):
	code_ptr = code[1]
	stack_ptr = code[2]
	stack_start = stack_ptr
	mem = [0] * MEM_SIZE
	mem[0:len(code)] = code
	while True:
		command = mem[code_ptr]
		if debug:
			print("\n    {} {} {} {}".format(command, command_code_to_str.get(command), stack_ptr, code_ptr))
			#print(mem[:200])
		code_ptr += 1
		if command == Commands.NOOP:
			pass
		elif command == Commands.EXIT:
			return mem[stack_ptr - 1]
		elif command == Commands.PUSH:
			if debug:
				print("      " + str(mem[code_ptr])) 
			mem[stack_ptr] = mem[code_ptr]
			code_ptr += 1
			stack_ptr += 1
		elif command == Commands.DUP:
			mem[stack_ptr] = mem[stack_ptr - 1]
			stack_ptr += 1
		elif command == Commands.DROP:
			stack_ptr -= 1
		elif command == Commands.UNDROP:
			stack_ptr += 1
		elif command == Commands.SWAP:
			tmp = mem[stack_ptr - 1]
			mem[stack_ptr - 1] = mem[stack_ptr - 2]
			mem[stack_ptr - 2] = tmp
		elif command == Commands.JUMP:
			code_ptr = mem[stack_ptr - 1]
			stack_ptr -= 1
		elif command == Commands.JUMPIFZ:
			if mem[stack_ptr - 2] == 0:
				code_ptr = mem[stack_ptr - 1]
			stack_ptr -= 2
		elif command == Commands.GETSTACK:
			mem[stack_ptr] = stack_ptr
			stack_ptr += 1
		elif command == Commands.SETSTACK:
			stack_ptr = mem[stack_ptr - 1]
		elif command == Commands.MOVEFROM:
			mem[stack_ptr - 1] = mem[mem[stack_ptr - 1]]
		elif command == Commands.MOVETO:
			mem[mem[stack_ptr - 1]] = mem[stack_ptr - 2]
			stack_ptr -= 2
		elif command == Commands.MEMMOVE:
			amount = mem[stack_ptr - 3]
			src = mem[stack_ptr - 2]
			dest = mem[stack_ptr - 1]
			mem[dest:dest+amount] = mem[src:src+amount]
			stack_ptr -= 3
		elif command == Commands.ADD:
			mem[stack_ptr - 2] = (mem[stack_ptr - 2] + mem[stack_ptr - 1]) % (2**32)
			stack_ptr -= 1
		elif command == Commands.NEG:
			mem[stack_ptr - 1] = -mem[stack_ptr - 1] % (2**32)
		elif command == Commands.MULT:
			mem[stack_ptr - 2] = (mem[stack_ptr - 2] * mem[stack_ptr - 1]) % (2**32)
			stack_ptr -= 1
		elif command == Commands.DIV:
			b = mem[stack_ptr - 1]
			if b == 0:
				return -1
			mem[stack_ptr - 2] //= b
			stack_ptr -= 1
		elif command == Commands.MOD:
			b = mem[stack_ptr - 1]
			if b == 0:
				return -1
			mem[stack_ptr - 2] %= b
			stack_ptr -= 1
		elif command == Commands.BITOR:
			stack_ptr -= 1
			mem[stack_ptr - 1] = (mem[stack_ptr] | mem[stack_ptr - 1]) % (2**32)
		elif command == Commands.BITAND:
			stack_ptr -= 1
			mem[stack_ptr - 1] = (mem[stack_ptr] & mem[stack_ptr - 1]) % (2**32)
		elif command == Commands.SHIFTUP:
			amount = mem[stack_ptr - 1]
			if amount > 0:
				mem[stack_ptr - 2] <<= amount
			elif amount < 0:
				mem[stack_ptr - 2] >>= -amount
			mem[stack_ptr - 2] %= (2**32)
			stack_ptr -= 1
		elif command == Commands.NOT:
			mem[stack_ptr - 1] = int(not mem[stack_ptr - 1])
		elif command == Commands.NEGATIVE:
			mem[stack_ptr - 1] = int((mem[stack_ptr - 1] & 2**31) != 0)
		elif command == Commands.MEMSIZE:
			mem[stack_ptr] = MEM_SIZE
			stack_ptr += 1
		elif command == Commands.PUTCHAR:
			sys.stdout.write(chr(mem[stack_ptr - 1]))
			sys.stdout.flush()
			stack_ptr -= 1
		elif command == Commands.PUTINT:
			sys.stdout.write(str(mem[stack_ptr - 1]))
			sys.stdout.flush()
			stack_ptr -= 1
		else:
			print("Invalid command ", command)
			return -1
		

