# Todo next
* Use rule names as indices to the childrens array in visit_* functions instead of numbers
* redirection
* pipes
* external commands, set search paths
* conditionals if / else / elif 
* loops
* lists, a = [a b c], len a, a[0], a[1:]

# Todo
## Implement console features
### Editing
* Autocomplete
* History
* Find/implement pure python implementation of readline and ncurses for windows.
### Misc
* Add an option to echo commands as they are being executed. $(setopt echo on). Create a separate option variables space.
* choose_prompt, set_prompt, save_prompt_as (use ncurses for UI if required), use separate option variables space for storing prompts.

## Implement language features
### Literals
* Add hex and octal integer literals. Use separate float and integer literals
* string escapes, string operations
* dictionaries d = {x:1 y:2}; d = (dict [a b c d])
* regular expression literals /abc/ig, =~
* lambdas: \x y -> x == y; \ -> $a; \x -> len x
* wildcards *,**,?,{}

### Language constructs
* constants
* slicing
* functions
* variable scopes, persistence (use json/sqlite?)
* exceptions (try, catch, finally)
* pattern matching with match
* Be case insensitive
* structs?
<code>
struct Person:
    Name #Indentation acts as a comma
    Age
    Email
struct Point: x, y
</code>
* namespaces?


## Parsing
* Improve syntax error messages. Do not say "SYNTAX ERROR:  Expected 'WS' at position..." instead skip all non essential tokens and report the next required rule match (list all rules if there are multiple choices)

## Implement commands
* Conversion: int "1", int 1.1, float "1.0", float 1, str 5, str 1.2
* ls (revisit)
* copy
* rsync
* exec $code
* alias
* echo
* funcsave, funced, vared
* basename
* dirname
* pushd, popd, nextd, prevd
* map, filter, reduce, zip etc. Look at the python pipes library, itertools module, functools and Haskell Lists module for inspiration
 
## Automatic variables
* user defined prompts 

## Testing
* Test on cygwin/mintty in addition to cmd.exe on windows

# Done
* command substitution $(pwd)
* Context.isExported(varName)
* Context.getVar() should return the value of the variable instead of the Variable class
* Let command be an expr
* Remove CmdResult class. Use generic python objects instead (like string and numbers) or create custom pipeline objects to represent command specific information
** use __str__ to convert objects into terminal output for the time being
* literals should return their value when used as a command
* string interpolation "$x, ${x}H, $(time)". The $ sign is only required within strings for interpolation.
* SCRIPT_DIR

# Rejected
* Reset interpreter between scripts. REASON: This is not required a separate instance of the interpreter should be launched and the script should be run inside it if a new environment is required. Running multiple scripts in the same env can be useful. REVISIT LATER: Maybe