sourcecode = """
{

# macros that translate directly to builtin commands (but know the amount of arguments)
!putchar(c){c .putchar}
!add(a b){a b .add}
!mult(a b){a b .mult}
!div(a b){a b .div}
!mod(a b){a b .mod}
!bitand(a b){a b .bitand}
!bitor(a b){a b .bitor}
!shiftup(a b){a b .shiftup}
!exit(code){code .exit}
!jump(to){to .jump}
!jumpifz(condition to){condition to .jumpifz}
!setstack(to){to .setstack}
!not(a){a .not}


# macros that almost translate directly to builtins
!minus(val){val .neg}
!isnegative(a){a .negative}
!deref (ptr) {ptr .movefrom}
!setref(ptr value){
	ptr
	value
	.swap
	.moveto
}

# other macros
!dupsecond {
	.swap
	.dup
	.drop
	.swap
	.undrop
}
!printint(val){
	val
	putchar(40)
	.putint
	putchar(41)
}
!sub(a b){
	add(a minus(b))
}
!lt (left right){
	isnegative(sub(left right))
}
!neq(a b){
	sub(a b)
}
!eq (a b){
	not(sub(a b))
}
!dowhile (condition body)(:whilestart) {
	:whilestart
	body
	jumpifz(not(condition) whilestart)
}
!if(condition body)(:ifend) {
	jumpifz(condition ifend)
	body
	:ifend
}
!and(a b) (:end){
	a
	jumpifz(.dup end)
	.drop
	b
	:end
}
!ifelse(condition ifbody elsebody)(:elsepart :ifend) {
	jumpifz(condition elsepart)
	ifbody
	jump(ifend)
	:elsepart
	elsebody
	:ifend
}
!while (condition body) {
	if(condition {
		dowhile (condition body)
	})
}
!varptr(id) {
	add(deref(@funcmem) id)
}
!setvar(id value){
	setref(varptr(id) value)
}
!getvar(id){
	deref(varptr(id))
}

!addto (pos val){
	setref(pos add(deref(.dup) val))
}
!calls(fun)(:returnpos){
	returnpos
	jump(fun)
	:returnpos
}
!call(fun args){
	args
	calls(fun)
}
!function(label nargs nvars body){
	label
	# remember old stack location
	deref(@funcmem)
	
	# remember current stack location
	.getstack
	@funcmem
	.moveto
	
	# remember argument number
	nargs
	# remember number of local variables
	nvars
	
	# reserve space for local variables
	.dup
	.getstack
	.add
	.setstack
	.drop
	# execute function body
	body
	
	returns
}
!endfunc{
	# store old stack and old mem location location in temporary globals
	setref(@memtmp getvar(-1))
	setref(@calltmp getvar(-2))
	.getstack
	minus(add(add(deref(@funcmem) getvar(1)) 1))
	.add
	@returntmp
	.moveto
	
	# move return values to top of regular stack
	# source location start
	.getstack
	minus(deref(@returntmp))
	.add
	# amount of return values
	deref(@returntmp)
	.swap
	# destination location start
	sub(deref(@funcmem) add(getvar(0) 2))
	# remember destination location for later (because getvar(0) might get overwritten)
	.dup
	@funcmem
	.moveto
	# actually move the return values
	.memmove
	
	# move stack to end of return values
	setstack(add(deref(@funcmem) deref(@returntmp)))
	
	# recall old stack location
	setref(@funcmem deref(@memtmp))
}
!returns {
	endfunc
	# return to previous position
	jump(deref(@calltmp))
}
!return(val){
	val
	returns
}
!tailcalls(fun){
	endfunc
	deref(@calltmp)
	jump(fun)
}
!tailcall(fun val){
	val
	tailcalls(fun)
}
!print(string)(:stringstart :stringend){
	stringstart
	while( neq(.dup stringend) {
		putchar(deref(.dup))
		add({ } 1)
	})
	jump(stringend)
	:stringstart
	string
	:stringend
	.drop
}
!println(string){
	print(string)
	putchar(10)
}
!putint(val){
	val
	0
	.swap
	while(.dup {
		add(mod(.dup 10) 48)
		.swap
		div({ } 10)
	})
	.drop
	while(.dup {
		.putchar
	})
	.drop
}
!alloc(amount) {
	# there's no free yet so it's not necessary to keep track of allocated memory
	deref(@freeheapstart)
	addto(@freeheapstart amount)
}

# actual code part

# some initializer metadata
[
0
@codestart # initial location of the code pointer
@codeend # initial location of the stack pointer
]

# place where the code starts executing
:codestart
alloc(2048) # reserve 2048 words space for the stack

# end with as exit code the return value from main
exit(call(@main { }))

# function to print a newline character
function(
	:printnl # function name (label)
	0 # number of arguments
	0 # number of local variables
	putchar(10) # function body
)

function ( # define a new function
	:factorial # name (label) of the function
	1 # number of arguments
	1 # number of local variables
	{ # function body
		# setvar and getvar set/return local variables
		# local variables are represented by positive ids starting at 2
		# arguments are represented by negative ids up to -3
		# the ids -2, -1 and 0 and 1 are reserved
		setvar(2 1)
		while({ getvar(-3)} {
			setvar(2 {
				mult(getvar(2) getvar(-3))
			})
			setvar(-3 add(getvar(-3) -1))
		})
		getvar(2) # if there's no explicit return then whatever is still on the stack at the end of the function is returned
		# this could be multiple values
	}
)

function (:fizzbuzz 1 1 {
	setvar(2 1)
	while (lt(getvar(2) getvar(-3)) {
		ifelse({
			and(not(mod(getvar(2) 3)) not(mod(getvar(2) 5))) 
		} {
			print("FizzBuzz ")
		} {
			ifelse (not(mod(getvar(2) 3)) {
				print("Fizz ")
			} {
				ifelse (not(mod(getvar(2) 5)) {
					print("Buzz ")
				} {
					putint(getvar(2))
					print(" ")
				})
			})
		})
		setvar(2 add(getvar(2) 1))
	})
	print("\n")
})

function (:pow 2 0 {
	!base -4
	!exponent -3
	tailcall(@powhelper {
		getvar(base)
		1
		getvar(exponent)
	})
})

function (:powhelper 3 0 {
	!base -5
	!accum -4
	!exponent -3
	if (bitand(getvar(exponent) 1){
		# exponent is odd: multipy with base
		setvar(accum mult(getvar(accum) getvar(base)))
		setvar(exponent add(getvar(exponent) -1))
	})
	if (not(getvar(exponent)) {
		# exponent is 0: return
		return(getvar(accum))
	})
	# exponent is even: multiply with itself and half exponent
	setvar(base mult(getvar(base) getvar(base)))
	setvar(exponent div(getvar(exponent) 2))
	tailcall(@powhelper {
		getvar(base)
		getvar(accum)
		getvar(exponent)
	})
})

function (:gcd 2 0 {
	if (eq(getvar(-4) 0){
		return(getvar(-3))
	})
	tailcall(@gcd {mod(getvar(-3) getvar(-4)) getvar(-4)})
})

function (:main 0 0 {
	# print all printable ascii characters
	32 # if there is just a number then that number is pushed to the stack
	while (lt(.dup 127) { # dup copies the top value of the stack
		# curly braces form a code block
		# this allows multiple expressions to be passed as a single macro argument
		putchar(.dup)
		add({ } 1) # { } is an empty code block (without return value). It can be used in place of a macro argument to take the top value from the stack instead
	})
	.drop # drop the top value from the stack

	# call the printnl function without arguments
	call(@printnl { })

	# call the factorial function and print the result as integer
	# This function takes one value as argument
	putint(call(@factorial 6))

	call(@printnl { })

	# print some text
	println("hello world")

	# call the fizzbuzz function, which also takes one argument
	call(@fizzbuzz 50)

	print("3^7 = ")
	putint(call(@pow {3 7}))
	print("\n")
	
	print("Greatest Common Divisor of 24 and 128 = ")
	putint(call(@gcd {24 128}))
	print("\n")
	0
})
# some extra space of memory
# this is used for global constants and variables
[0]
:freeheapstart # pointer to the first free address of memory that can be used as heap
[@codeend]
:funcmem # pointer to the location of the function arguments and local variables
[0]
:calltmp # hold the previous call frame when the stack is being manipulated
[0]
:memtmp # hold the previous funcmem location when the stack is being manipulateds
[0]
:returntmp # hold the amount of return values during a return
[0]
# the stack begins here
:codeend
[0]
}
"""
