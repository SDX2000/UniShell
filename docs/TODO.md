# Todo next
* Move the interpreter out into its own folder
* Move ASG nodes into a separate folder within the interpreter folder
* Workout a better way of hiding command output for selected commands like cd, set and echo when autoprint is on. Create a String pipeline object. Note: Pipeline object != ASG object.
* Implement an auto command loader. Scan the commands module for function names beginning with cmd.
* Add a no banner flag (--no-banner)

# Todo
## Implement language features

### Literals
* Add hex and octal integer literals. Use separate float and integer literals.
* dictionaries d = {x:1 y:2}; d = (dict [a b c d])
* regular expression:/abc/ig, =~
* lambdas: \x y -> x == y; \ -> $a; \x -> len x
* wildcards *,**,?,{}
* Add support for the \e escape code in strings

### Language
* New exported variable/function syntax
    * pub var x = 10
    * pub func f(x)
         echo $x
      end
* Operators
    * Assignment: x = 10; pub y = 10
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
* String operations (slicing, sub-scripting, replacement)
* Functions
    * Check if the return keyword can be avoided. Using a mandatory else part for if may help. Use match when if/elif/else becomes cumbersome.
    * Doc strings
    * func f(x)
         echo $x
      end
    * Nested functions?
* End all blocks with the end keyword instead of using braces. This way the overhead of an opening brace can be avoided. 
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
* Script directives
    * Add an option to echo commands as they are being executed. $(setopt echo on).
    
    * user defined prompts ("prompt", "prompt2")
* choose_prompt, save_prompt_as (use ncurses for UI if required), use separate option variables space for storing prompts.

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
* 

## Testing
* Add a test for the -s/--syntax switch
* Test on cygwin/mintty in addition to cmd.exe on windows


# Done
* Script directives
    * Create a separate option variable/command space.
    * pushopt, popopt, peekopt
    * Add an autoprint script option
        * When autoprint is true the output of all commands should be printed even if it is not printed explicitly. The output should not be printed twice if echo/set is called.
* Add a check syntax option (-s). Run the parser and quit when this option is specified.
* Translate escapes
* Remove the ExecutionContext class and use plain dictionaries instead
    * Check if we really need to differentiate between commands and variables. If not then replace the execution context class with a single dictionary containing both commands and variables. Use a separate dictionary for script options.

* Generate custom ASG (Abstract semantic graph) using the node visitor. 
    * ASG nodes should be callables
    * Executing the root node should start an inorder execution from left to right. Non leaf nodes may also execute code and/or aggregate the results of their child nodes.
    * Running the ASG should not change it in anyway. The ASG should operate on the context provided to it. Think of an ASG as a compiled representation of the parsed program.
* Pass the whole script to the parser instead of executing it line by line
* Change the string interpolation logic to split the string using the regex instead of substituting the values at parse time. The values should be evaluated and concatenated at run time (__call__)
* Introduced integer and float in grammar
* Generate custom ASG
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