#!/bin/bash
pushd tests
unishell -c '"Hello A"'
#unishell -c '"Hello A"' -t
unishell -c 'set msg "Hello B"' -c '$msg'
#unishell -c 'set msg "Hello B"' -c '$msg' -t
unishell -c 'set msg "Hello C"; $msg'
#unishell -c 'set msg "Hello C"; $msg' -t

unishell -c 'exit 1'
unishell -c 'exit 2'


for i in *.ush;
do
    echo
    echo RUNNING: $PWD/$i
    eval ./$i; 
done

popd