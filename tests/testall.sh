#!/bin/bash

unishell -c "echo Hello A"
unishell -c "echo Hello A" -t
unishell -c 'set msg "Hello B"' -c 'echo $msg'
unishell -c 'set msg "Hello B"' -c 'echo $msg' -t
unishell -c 'set msg "Hello C"; echo $msg'
unishell -c 'set msg "Hello C"; echo $msg' -t

for i in *.ush;
do 
    eval ./$i; 
done