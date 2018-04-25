#!/bin/bash

source integration_tests.sh

test_1_0 "$checkfiles_dir/test_1_0" >"$checkfiles_dir/test_1_0/test_1_0.log"
test_1_1 "$checkfiles_dir/test_1_1" >"$checkfiles_dir/test_1_1/test_1_1.log"
test_1_2 "$checkfiles_dir/test_1_2" >"$checkfiles_dir/test_1_2/test_1_2.log"
test_2_0 "$checkfiles_dir/test_2_0" >"$checkfiles_dir/test_2_0/test_2_0.log"
test_3_0 "$checkfiles_dir/test_3_0" >"$checkfiles_dir/test_3_0/test_3_0.log"
test_3_1 "$checkfiles_dir/test_3_1" >"$checkfiles_dir/test_3_1/test_3_1.log"
test_3_2 "$checkfiles_dir/test_3_2" >"$checkfiles_dir/test_3_2/test_3_2.log"
test_4_0 "$checkfiles_dir/test_4_0" >"$checkfiles_dir/test_4_0/test_4_0.log"
test_4_1 "$checkfiles_dir/test_4_1" >"$checkfiles_dir/test_4_1/test_4_1.log"
test_4_2 "$checkfiles_dir/test_4_2" >"$checkfiles_dir/test_4_2/test_4_2.log"
test_5_0 "$checkfiles_dir/test_5_0" >"$checkfiles_dir/test_5_0/test_5_0.log"
test_5_1 "$checkfiles_dir/test_5_1" >"$checkfiles_dir/test_5_1/test_5_1.log"
test_5_2 "$checkfiles_dir/test_5_2" >"$checkfiles_dir/test_5_2/test_5_2.log"
test_5_3 "$checkfiles_dir/test_5_3" >"$checkfiles_dir/test_5_3/test_5_3.log"
