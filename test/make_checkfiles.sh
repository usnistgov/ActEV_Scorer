#!/bin/bash

. integration_tests.sh

all_tests="test_1_0 test_1_1 test_1_2 test_2_0 test_3_0 test_3_1 test_3_2 test_4_0 test_4_1 test_4_2 test_5_0 test_5_1 test_5_2 test_5_3 test_6_0 test_7_0 test_7_1 test_8_0 test_9_0 test_9_1 test_9_2 test_9_3 test_10_0 test_10_1 test_11_0 test_11_1 test_11_2 test_11_3 test_12_0 test_12_1 test_13_0 test_13_1 test_13_2 test_13_3"

tests="$all_tests"
if [ ! "$1" = "" ] ; then
    tests=$*
fi
for test in $tests ; do
    echo "make_checkfiles $test"
    if [ ! -d $checkfiles_dir/$test ] ; then mkdir -p $checkfiles_dir/$test ; fi
    $test "$checkfiles_dir/$test" > "$checkfiles_dir/$test/$test.log"
done
