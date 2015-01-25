#!/bin/bash

export PATH=$PATH:$PWD

pushd tests

unishell -c '"Hello A"'

unishell -c 'set msg "Hello B"' -c '$msg'

unishell -c 'set msg "Hello C"; $msg'

unishell -i  --no-banner -c 'exit'

unishell -c 'exit 1'
unishell -c 'exit 2'


for i in *.ush;
do
    echo
    echo RUNNING: $PWD/${i}
    eval ./${i};
done

popd