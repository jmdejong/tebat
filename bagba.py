#!/usr/bin/env python3

import base64
import sys
import parser
import run
import compileself


def main():
	
	#code = [
		#0,
		#4,
		#128,
		#0,
		#Commands.NOOP,
		#Commands.PUSH,
		#32,
		#Commands.DUP,
		#Commands.PUTCHAR,
		#Commands.PUSH,
		#1,
		#Commands.ADD,
		#Commands.DUP,
		#Commands.PUSH,
		#7,
		#Commands.SWAP,
		#Commands.PUSH,
		#126,
		#Commands.NEG,
		#Commands.ADD,
		#Commands.NOT,
		#Commands.JUMPIFZ,
		#Commands.PUSH,
		#10,
		#Commands.PUTCHAR,
		#Commands.PUSH,
		#0,
		#Commands.EXIT
	#]
	

	code = parser.compile_code(compileself.sourcecode)
	#print([run.command_code_to_str.get(c, c) for c in code])
	run.run(code)




if __name__ == "__main__":
	main()
	

