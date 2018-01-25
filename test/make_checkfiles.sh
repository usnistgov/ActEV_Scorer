#!/bin/bash

source integration_tests.sh

test_1_0 "$checkfiles_dir/test_1_0" >"$checkfiles_dir/test_1_0/test_1_0.log"
test_2_0 "$checkfiles_dir/test_2_0" >"$checkfiles_dir/test_2_0/test_2_0.log"
