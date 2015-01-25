#!/bin/bash

pushd $(dirname $0) > /dev/null
SCRIPT_DIR=$(pwd -P)
popd > /dev/null

export PATH=$PATH:$SCRIPT_DIR

TESTS_DIR=$SCRIPT_DIR/tests

#echo TESTS_DIR=$TESTS_DIR

REF_DIR=reference_output
OUTPUT_DIR=output

pushd $TESTS_DIR > /dev/null

mkdir -p $OUTPUT_DIR >/dev/null 2>&1

for i in $(ls *.ush *.sh 2> /dev/null);
do
    echo RUNNING: $PWD/$i
    OUTPUT_FILE=$OUTPUT_DIR/$i.txt

    eval ./$i > $OUTPUT_FILE 2>&1;

    if [ ! -d $REF_DIR ]; then
        continue;
    fi

    REF_FILE=$REF_DIR/$i.txt

    diff "$OUTPUT_FILE" "$REF_FILE" >/dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo PASS
    else
        echo FAIL: diff "$TESTS_DIR/$OUTPUT_FILE" "$TESTS_DIR/$REF_FILE"
    fi
    echo
done

if [ ! -d $REF_DIR ]; then
    echo "Reference directory does not exist. Renaming the output folder ($OUTPUT_DIR) to create the new reference directory ($REF_DIR)."
    mv $OUTPUT_DIR $REF_DIR
fi

popd > /dev/null