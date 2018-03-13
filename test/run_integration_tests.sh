#!/bin/bash

source integration_tests.sh

run_test test_1_0 "$checkfiles_dir/test_1_0"
run_test test_2_0 "$checkfiles_dir/test_2_0"
run_test test_3_0 "$checkfiles_dir/test_3_0"
run_test test_3_1 "$checkfiles_dir/test_3_1"
run_test test_4_0 "$checkfiles_dir/test_4_0"
run_test test_4_1 "$checkfiles_dir/test_4_1"
