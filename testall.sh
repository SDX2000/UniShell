#!/bin/bash
pushd tests
unishell -c "echo Hello A"
#unishell -c "echo Hello A" -t
unishell -c 'set msg "Hello B"' -c 'echo $msg'
#unishell -c 'set msg "Hello B"' -c 'echo $msg' -t
unishell -c 'set msg "Hello C"; echo $msg'
#unishell -c 'set msg "Hello C"; echo $msg' -t

unishell -c 'exit 1'
unishell -c 'exit 2'


for i in *.ush;
do 
    eval ./$i; 
done

popd