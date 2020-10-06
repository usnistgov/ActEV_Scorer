#!/bin/bash

. integration_tests.sh

all_tests="test_1_0 test_1_1 test_1_2 test_2_0 test_3_0 test_3_1 test_3_2 test_4_0 test_4_1 test_4_2 test_5_0 test_5_1 test_5_2 test_5_3 test_6_0 test_7_0 test_7_1 test_8_0 test_9_0 test_9_1 test_9_2 test_9_3 test_10_0 test_10_1 test_11_0 test_11_1 test_11_2 test_11_3 test_11_4 test_11_5 test_12_0 test_12_1 test_13_0 test_13_1 test_13_2 test_13_3 test_13_4 test_13_5 test_13_6 test_14_0 test_15_0 test_15_1 test_15_2 test_15_3 test_16_0 test_17_0 test_18_0 test_19_0 test_19_1 test_19_2 test_19_3"

tests="$all_tests"
if [ ! "$1" = "" ] ; then
    tests=$*
fi
for test in $tests ; do
    run_test $test $checkfiles_dir/$test
done

