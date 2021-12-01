#!/bin/bash

. integration_tests.sh

all_tests="test_1_0 test_1_1 test_1_2 test_2_0 test_3_0 test_3_1 test_3_2 test_4_0 test_4_1 test_4_2 test_5_0 test_5_1 test_5_2 test_5_3 test_6_0 test_7_0 test_7_1 test_8_0 test_9_0 test_9_1 test_9_2 test_9_3 test_10_0 test_10_1 test_11_0 test_11_1 test_11_2 test_11_3 test_11_4 test_11_5 test_12_0 test_12_1 test_13_0 test_13_1 test_13_2 test_13_3 test_13_4 test_13_5 test_13_6 test_14_0 test_15_0 test_15_1 test_15_2 test_15_3 test_15_4 test_15_5 test_16_0 test_17_0 test_18_0 test_19_0 test_19_1 test_19_2 test_19_3 test_20_0 test_20_1 test_20_2 test_20_3 test_21_0 test_22_0 test_22_1 test_22_2 test_22_3 test_22_4 test_22_5 test_22_6 test_22_7 test_23_0 test_23_1 test_23_2 test_23_3 test_23_4 test_23_5 test_23_6 test_23_7 test_24_0"

tests="$all_tests"
if [ ! "$1" = "" ] ; then
    tests=$*
fi
for test in $tests ; do
    echo "make_checkfiles $test"
    if [ ! -d $checkfiles_dir/$test ] ; then mkdir -p $checkfiles_dir/$test ; fi
    $test "$checkfiles_dir/$test" > "$checkfiles_dir/$test/$test.log"
done
