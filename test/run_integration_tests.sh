#!/bin/bash

source integration_tests.sh

run_test test_1_0 "$checkfiles_dir/test_1_0"
run_test test_1_1 "$checkfiles_dir/test_1_1"
run_test test_1_2 "$checkfiles_dir/test_1_2"
run_test test_2_0 "$checkfiles_dir/test_2_0"
run_test test_3_0 "$checkfiles_dir/test_3_0"
run_test test_3_1 "$checkfiles_dir/test_3_1"
run_test test_3_2 "$checkfiles_dir/test_3_2"
run_test test_4_0 "$checkfiles_dir/test_4_0"
run_test test_4_1 "$checkfiles_dir/test_4_1"
run_test test_4_2 "$checkfiles_dir/test_4_2"
run_test test_5_0 "$checkfiles_dir/test_5_0"
run_test test_5_1 "$checkfiles_dir/test_5_1"
run_test test_5_2 "$checkfiles_dir/test_5_2"
run_test test_5_3 "$checkfiles_dir/test_5_3"
