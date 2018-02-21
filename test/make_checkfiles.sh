#!/bin/bash

source integration_tests.sh

test_1_0 "$checkfiles_dir/test_1_0" >"$checkfiles_dir/test_1_0/test_1_0.log"
test_2_0 "$checkfiles_dir/test_2_0" >"$checkfiles_dir/test_2_0/test_2_0.log"
test_3_0 "$checkfiles_dir/test_3_0" >"$checkfiles_dir/test_3_0/test_3_0.log"
test_3_1 "$checkfiles_dir/test_3_1" >"$checkfiles_dir/test_3_1/test_3_1.log"
