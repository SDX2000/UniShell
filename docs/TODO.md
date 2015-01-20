# Todo next
* Generate custom ASG

# Todo
## Implement language features
### ASG - Abstract Semantic Graph
* Generate custom ASG (Abstract semantic graph) using the node visitor. 
    * ASG nodes should be callables
    * Executing the root node should start an inorder execution from left to right. Non leaf nodes may also execute code and/or aggregate the results of their child nodes.
    * Running the ASG should not change it in anyway. The ASG should operate on the context provided to it. Think of an ASG as a compiled representation of the parsed program.

### Literals
* Add hex and octal integer literals. Use separate float and integer literals.
* string escapes, string operations
* dictionaries d = {x:1 y:2}; d = (dict [a b c d])
* regular expression literals /abc/ig, =~
* lambdas: \x y -> x == y; \ -> $a; \x -> len x
* wildcards *,**,?,{}

### Language
* Operators
    * Arithmetic: + - * / %
    * Boolean: and or not
    * Relational: < > <= >= == != (in boolean contexts)
    * External command: !cmd, "!2to3"
    * Redirection: < > << >> (in command contexts)
    * Pipe:|

* NOTE: Redirection and piping should work for both external and internal commands. The user should be able to pipe output from external commands to internal commands and viceversa.

* External commands
    * Implement search paths
    * Implement non-blocking commands with support for error checking using callbacks.
    * An external command should follow the syntax of regular commands (enable redirection and piping for regular commands too!)
    * Syntax examples
        * cat abc.txt | !grep "foobar"
        * !cmd  < abc.txt >def.txt 2>&1

    
    
* Conditionals if / else / elif. Model it after python. External commands which fail should thow a BadExit. Exit codes cannot not be checked using conditionals directly you will have to catch BadExit first. Need to handle BadExits asynchronously for non-blocking commands, may be a callbacks can be provided to check for success/errors (take inspiration from JQuery).
* Loops
* Lists, a = [a b c], len a, a[0], a[1:]
* Constants
* Slicing
* Functions
    * Check if the return keyword can be avoided. Using a mandatory else part for if may help. Use match when if/elif/else becomes cumbersome.
    * doc strings
* Variable scopes, persistence (use json/sqlite?)
* Exceptions (try, catch, finally)
* Pattern matching with match
* Be case insensitive
* Structs?
    struct Person:
        Name #Indentation acts as a comma (but what do we do with newlines (which act like a semicolons)?)
        Age
        Email
    struct Point: x, y
* value types / reference types: Everything is a value type in shells?
    * Let numbers be value types and strings be immutable (use COW (Copy on write) when someone tries to modify them)
* namespaces?
* modules (import abc)
    
* Interop
    * Python
        * import python modules
        * Execute python code
    * C
        * Load shared libraries and call functions

## Implement console features
### Editing/Usage
* Autocomplete
* History
* Find/implement pure python implementation of readline and ncurses for windows.
### Misc
* Add an option to echo commands as they are being executed. $(setopt echo on). Create a separate option variables space.
* choose_prompt, set_prompt, save_prompt_as (use ncurses for UI if required), use separate option variables space for storing prompts.

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
* getopt, docopt
 
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
    * use __str__ to convert objects into terminal output for the time being
* literals should return their value when used as a command
* string interpolation "$x, ${x}H, $(time)". The $ sign is only required within strings for interpolation.
* SCRIPT_DIR

# Rejected
* Reset interpreter between scripts. REASON: This is not required a separate instance of the interpreter should be launched and the script should be run inside it if a new environment is required. Running multiple scripts in the same env can be useful. REVISIT LATER? Maybe.

* Use rule names as indices to the childrens array in visit_* functions instead of numbers. REASON: This will not work since the lower nodes may not return a SemanticActions dictionary. The subnodes may decide to return custom data instead.