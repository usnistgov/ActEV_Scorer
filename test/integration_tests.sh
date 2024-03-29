#!/bin/bash

export checkfiles_dir=data/checkfiles

check_status() {
    status=$?
    if [ $status -ne 0 ]; then
    echo "*** FAILED ***"
    exit $status
    fi
}

run_test() {
    test=$1
    checkfile_outdir=$2
    checkfile_outdir_basename=`basename $checkfile_outdir`
    compcheck_outdir=${3-compcheckfiles}
    compcheckfile_outdir="$compcheck_outdir/$checkfile_outdir_basename"
    mkdir -p "$compcheckfile_outdir"

    echo "** Running integration test '$test' **"
    log_fn="$compcheckfile_outdir/$test.log"
        $test "$compcheckfile_outdir" >"$log_fn"
    check_status

    # Replace paths in logfile
    for f in "$log_fn" "${compcheckfile_outdir}/config.csv"; do
    if [ -f "$f" ]; then
        sed -e "s:${compcheckfile_outdir}:${checkfile_outdir}:g" "$f" >"$f.new"
        mv "$f.new" "$f"
    fi
    done
    # diff --exclude \*dm --exclude \*png -I "command" -I "git.commit" -r "$checkfile_outdir" "$compcheckfile_outdir"
    python3 diff.py "$checkfile_outdir" "$compcheckfile_outdir"
    check_status
    
    echo "*** OK ***"
}

# ActEV18_AD integration test 1
test_1_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/VIRAT_S_000000_fake-sysout.json" \
    -r "data/VIRAT_S_000000.json" \
    -a "data/VIRAT_S_000000_activity-index.json" \
    -f "data/VIRAT_S_000000_file-index.json" \
    -o "$1" \
    -d \
    -v
}

# ActEV18_AD integration test 1_1
# Testing passing of scoring parameters JSON
test_1_1() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/VIRAT_S_000000_fake-sysout.json" \
    -r "data/VIRAT_S_000000.json" \
    -a "data/VIRAT_S_000000_activity-index.json" \
    -f "data/VIRAT_S_000000_file-index.json" \
    -o "$1" \
    -d \
    -p "data/test_1_1.scoring_parameters.json" \
    -v
}

# ActEV18_AD integration test 1_2
# Check validation only option
test_1_2() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/VIRAT_S_000000_fake-sysout.json" \
    -a "data/VIRAT_S_000000_activity-index.json" \
    -f "data/VIRAT_S_000000_file-index.json" \
    -d \
    -v \
    -V
}

# ActEV18_AD integration test 2
test_2_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/VIRAT_S_000001_fake-sysout.json" \
    -r "data/VIRAT_S_000001.json" \
    -a "data/VIRAT_S_000001_activity-index.json" \
    -f "data/VIRAT_S_000001_file-index.json" \
    -o "$1" \
    -d \
    -v
}

# integration test 3-0
test_3_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/test_3-0_fake-sysout.json" \
    -r "data/test_3-0.json" \
    -a "data/test_3-0_activity-index.json" \
    -f "data/test_3-0_file-index.json" \
    -o "$1" \
    -d \
    -v
}

# integration test 3-1
test_3_1() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/test_3-1_fake-sysout.json" \
    -r "data/test_3-0.json" \
    -a "data/test_3-0_activity-index.json" \
    -f "data/test_3-0_file-index.json" \
    -o "$1" \
    -d \
    -v
}

# integration test 3-2
# Testing multi-file input
test_3_2() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/test_3-2_fake-sysout.json" \
    -r "data/test_3-2.json" \
    -a "data/test_3-0_activity-index.json" \
    -f "data/test_3-2_file-index.json" \
    -o "$1" \
    -d \
    -v
}

# integration test 4-0
test_4_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_4-0_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_4-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" \
    -d \
    -j \
    -v
}

# integration test 4-1
# AD scoring on AOD input
test_4_1() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/test_4-0_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_4-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" \
    -d \
    -v
}

# integration test 4-3
# Check validation only option
test_4_2() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_4-0_fake-sysout.json" \
    -a "data/test_4-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -d \
    -j \
    -v \
    -V
}


# integration test 5-0
# Activity index equivalence class testing
test_5_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_4-0_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_5-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" \
    -d \
    -j \
    -v
}

# integration test 5-1
# Activity index equivalence class testing
test_5_1() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_4-0_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_5-1_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" \
    -d \
    -j \
    -v
}

# integration test 5-2
# Activity index equivalence class testing
test_5_2() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_5-2_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_5-2_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" \
    -d \
    -j \
    -v
}

# integration test 5-3
# Activity index equivalence class testing
test_5_3() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_5-3_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_5-2_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" \
    -d \
    -j \
    -v
}

# integration test 6-0
# Check for handling of MODE metric over instances with 0 reference
# objects
test_6_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_6-0_fake-sysout.json" \
    -r "data/test_6-0.json" \
    -a "data/test_6-0_activity-index.json" \
    -f "data/test_6-0_file-index.json" \
    -o "$1" -d -j -I -v
}

# integration test 7-0
# Test ignore-extraneous-files (-F) option
test_7_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_7-0_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_4-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -F \
    -o "$1" \
    -d \
    -j \
    -v
}

# integration test 7-1
# Test ignore-extraneous-files (-F) option
test_7_1() {
    ../ActEV_Scorer.py \
    "ActEV18_AOD" \
    -s "data/test_7-0_fake-sysout.json" \
    -r "data/test_7-1.json" \
    -a "data/test_4-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -F -o "$1" -d -j -i -v
}

test_8_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AODT" \
    -s "data/test_8-0_fake-sysout.json" \
    -r "data/test_8-0.json" \
    -a "data/test_8-0_activity-index.json" \
    -f "data/test_8-0_file-index.json" \
    -F \
    -o "$1" \
    -d \
    -j \
    -v
}

### ActEV19_Test
test_9_0() {
    ../ActEV_Scorer.py \
    "ActEV19_AD" \
    -s "data/test_9-0_fake-sysout.json" \
    -r "data/test_9-0.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_9-0_file-index.json" \
    -F \
    -o "$1" \
    -v
}

### ActEV19_Test vs. ActEV18_AD
test_9_1() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/test_9-0_fake-sysout.json" \
    -r "data/test_9-0.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_9-0_file-index.json" \
    -F \
    -o "$1" \
    -d \
    -v
}

### ActEV18_AD_1SECOL
test_9_2() {
    ../ActEV_Scorer.py \
    "ActEV18_AD_1SECOL" \
    -s "data/test_9-0_fake-sysout.json" \
    -r "data/test_9-0.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_9-0_file-index.json" \
    -F \
    -o "$1" \
    -d \
    -v
}

### ActEV18_AD_TFA
test_9_3() {
    ../ActEV_Scorer.py \
    "ActEV18_AD_TFA" \
    -s "data/test_9-0_fake-sysout.json" \
    -r "data/test_9-0.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_9-0_file-index.json" \
    -F \
    -o "$1" \
    -d \
    -v
}

### ActEV18_AD_TFA
test_10_0() {
    ../ActEV_Scorer.py \
       "ActEV18_AD_TFA" \
       -s "data/test_10-0_fake-sysout.json" \
       -r "data/test_10-0.json" \
       -a "data/test_10-0_activity-index.json" \
       -f "data/test_10-0_file-index.json" \
       -o "$1" \
       -v
}

### ActEV18_AD_1SECOL
test_10_1() {
    ../ActEV_Scorer.py \
    "ActEV18_AD_1SECOL" \
    -s "data/test_10-0_fake-sysout.json" \
    -r "data/test_10-0.json" \
    -a "data/test_10-0_activity-index.json" \
    -f "data/test_10-0_file-index.json" \
    -o "$1" \
    -v
}
test_11_0() {
    ../ActEV_Scorer.py \
       "ActEV19_AD_V2" \
       -s "data/test_11-0_fake-sysout.json" \
       -r "data/test_11-0.json" \
       -a "data/test_9-0_activity-index.json" \
       -f "data/test_11-0_file-index.json" \
       -o "$1" \
       -v
}

test_11_1() {
    ../ActEV_Scorer.py \
       "ActEV19_AD_V2" \
       -s "data/test_11-1_fake-sysout.json" \
       -r "data/test_11-0.json" \
       -a "data/test_9-0_activity-index.json" \
       -f "data/test_11-0_file-index.json" \
       -o "$1" \
       -v
}

test_11_2() {
    ../ActEV_Scorer.py \
       "ActEV19_AD_V2" \
       -s "data/test_11-2_fake-sysout.json" \
       -r "data/test_11-0.json" \
       -a "data/test_9-0_activity-index.json" \
       -f "data/test_11-0_file-index.json" \
       -o "$1" \
       -v
}

test_11_3() {
    ../ActEV_Scorer.py \
       "ActEV19_AD_V2" \
       -s "data/test_11-3_fake-sysout.json" \
       -r "data/test_11-0.json" \
       -a "data/test_9-0_activity-index.json" \
       -f "data/test_11-0_file-index.json" \
       -o "$1" \
       -v
}

test_11_4() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
       -s "data/test_11-4_fake-sysout.json" \
       -r "data/test_11-4.json" \
       -a "data/test_9-0_activity-index.json" \
       -f "data/test_11-0_file-index.json" \
       -o "$1" \
       -v
}

test_11_4npr() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2NPR" \
       -s "data/test_11-4_fake-sysout-npr.json" \
       -r "data/test_11-4.json" \
       -a "data/test_9-0_activity-index.json" \
       -f "data/test_11-0_file-index.json" \
       -o "$1" \
       -v
}

test_11_5() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_11-4_fake-sysout.json" \
    -r "data/test_11-4.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_11-0_file-index.json" \
    -o "$1" \
    -v
}

test_12_0() {
    ../ActEV_Scorer.py \
       "ActEV_SDL_V1" \
       -s "data/test_12-0_fake-sysout.json" \
       -r "data/test_12-0.json" \
       -a "data/test_9-0_activity-index.json" \
       -f "data/test_12-0_file-index.json" \
       -o "$1" \
       -v
}

test_12_1() {
    ../ActEV_Scorer.py \
       "ActEV19_AD_V2" \
       -s "data/test_12-0_fake-sysout.json" \
       -r "data/test_12-0.json" \
       -a "data/test_9-0_activity-index.json" \
       -f "data/test_12-0_file-index.json" \
       -o "$1" \
       -v
}

test_13_0() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_13-0_fake-sysout.json" \
    -r "data/test_13-0.json" \
    -a "data/test_13-0_activity-index.json" \
    -f "data/test_13-0_file-index.json" \
    -o "$1" \
    -v
}
test_13_1() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_13-1_fake-sysout.json" \
    -r "data/test_13-1.json" \
    -a "data/test_13-0_activity-index.json" \
    -f "data/test_13-1_file-index.json" \
    -o "$1" \
    -v
}
test_13_2() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_13-2_fake-sysout.json" \
    -r "data/test_13-2.json" \
    -a "data/test_13-0_activity-index.json" \
    -f "data/test_13-2_file-index.json" \
    -o "$1" \
    -v
}

test_13_3() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_13-3_fake-sysout.json" \
    -r "data/test_13-3.json" \
    -a "data/test_13-0_activity-index.json" \
    -f "data/test_13-2_file-index.json" \
    -o "$1" \
    -v
}

### Tests for vempty system output for an activity
test_13_4() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_13-2_fake-sysout.json" \
    -r "data/test_13-4.json" \
    -a "data/test_13-4_activity-index.json" \
    -f "data/test_13-2_file-index.json" \
    -o "$1" \
    -v
}

### Test for --ignore-missing-files flag
test_13_5() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_13-5_fake-sysout.json" \
    -r "data/test_13-2.json" \
    -a "data/test_13-0_activity-index.json" \
    -f "data/test_13-2_file-index.json" \
    -o "$1" \
    -v \
    --ignore-missing-files
}
### Test for instances < .5 sec
test_13_6() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_13-6_fake-sysout.json" \
    -r "data/test_13-6.json" \
    -a "data/test_13-6_activity-index.json" \
    -f "data/test_13-6_file-index.json" \
    -o "$1" \
    -v \
    --ignore-missing-files
}

#Testing Unique Conf limit input (-u)
test_14_0() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_10-0_fake-sysout.json" \
    -r "data/test_10-0.json" \
    -a "data/test_10-0_activity-index.json" \
    -f "data/test_10-0_file-index.json" \
    -o "$1" \
    -t 2 \
    -d \
        -v
}

#Small test
test_15_0() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_15-0_fake-sysout.json" \
    -r "data/test_15-0.json" \
    -a "data/test_15-0_activity-index.json" \
    -f "data/test_15-0_file-index.json" \
    -o "$1" \
    -v
}
#larger test
## This is a special test case with a well-set DET curve structure.  There are no False Alarms so the RFA scoring will be wierd.
test_15_1() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_15-1_fake-sysout.json" \
    -r "data/test_15-1.json" \
    -a "data/test_15-0_activity-index.json" \
    -f "data/test_15-0_file-index.json" \
    -o "$1" \
    -v -i
}

#Test averaging
test_15_2() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_15-2_fake-sysout.json" \
    -r "data/test_15-2.json" \
    -a "data/test_15-2_activity-index.json" \
    -f "data/test_15-0_file-index.json" \
    -o "$1" \
    -v -i
}

#Test when there are no instances in ref.
test_15_3() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_15-3_fake-sysout.json" \
    -r "data/test_15-3.json" \
    -a "data/test_15-2_activity-index.json" \
    -f "data/test_15-0_file-index.json" \
    -o "$1" \
    -v -i
}

#Test when there are no instances in ref.  Two Activities Closing, Entering.  Entering has NO instancs.
### Assertion: All Closing scores should be identical to Test_15_2
#Test averaging
test_15_4() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_15-2_fake-sysout.json" \
    -r "data/test_15-4.json" \
    -a "data/test_15-2_activity-index.json" \
    -f "data/test_15-0_file-index.json" \
    -o "$1" \
    -v -i
}

# Verification of scores for Test_15_4.  This generates aggregated scores that 15_4 should be identical
test_15_5() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_15-2_fake-sysout.json" \
    -r "data/test_15-4.json" \
    -a "data/test_15-5_activity-index.json" \
    -f "data/test_15-0_file-index.json" \
    -o "$1" \
    -v -i
}

# multiprocessing test
test_16_0() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_11-4_fake-sysout.json" \
    -r "data/test_11-4.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_11-0_file-index.json" \
    -o "$1" \
    -v -n 4 -e
}

# no ppf test
test_17_0() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V1" \
    -s "data/test_15-1_fake-sysout.json" \
    -r "data/test_15-1.json" \
    -a "data/test_15-0_activity-index.json" \
    -f "data/test_15-0_file-index.json" \
    -o "$1" -c "data/test_17-0_plot-option.json" \
    -v -i
}

# Pruning test
test_18_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/VIRAT_S_000000_fake-sysout.json" \
    -r "data/VIRAT_S_000000.json" \
    -a "data/VIRAT_S_000000_activity-index.json" \
    -f "data/VIRAT_S_000000_file-index.json" \
    -o "$1" \
    -v -P 0.8 -I
}

# no score regions test - Compared to test_1_0
test_19_0() {
    ../ActEV_Scorer.py \
    "ActEV18_AD" \
    -s "data/VIRAT_S_000000_fake-sysout.json" \
    -r "data/VIRAT_S_000000.json" \
    -a "data/VIRAT_S_000000_activity-index.json" \
    -f "data/VIRAT_S_000000_file-index_no-score.json" \
    -o "$1" -I -v
}

# no score regions test - Compared to test_16_0
test_19_1() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_19-1_fake-sysout.json" \
    -r "data/test_11-4.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_19-1_file-index.json" \
    -o "$1" -v -e
}

# no score regions test - 1000 1st frames of VIRAT_S_000000
test_19_2() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_19-2_fake-sysout.json" \
    -r "data/test_19-2.json" \
    -a "data/test_19-2_activity-index.json" \
    -f "data/test_19-2_file-index.json" \
    -o "$1" -v -e
}

# Same one without the no-score region
test_19_3() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_19-2_fake-sysout.json" \
    -r "data/test_19-2.json" \
    -a "data/test_19-2_activity-index.json" \
    -f "data/test_19-3_file-index.json" \
    -o "$1" -v -e
}

# New protocol tests: processingReport
test_20_0() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_20-0_fake-sysout.json" \
    -r "data/test_11-4.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_11-0_file-index.json" \
    -o "$1" -v -e
}

# Check tests on processingReport (1,2 and 3)
test_20_1() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_20-0_fake-sysout.json" \
    -r "data/test_11-4.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_11-0_file-index.json" \
    -o "$1" -v --ignore-extraneous-files -e
}

test_20_2() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_20-0_fake-sysout.json" \
    -r "data/test_11-4.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_11-0_file-index.json" \
    -o "$1" -v --ignore-missing-files -e
}

test_20_3() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_20-0_fake-sysout.json" \
    -r "data/test_11-4.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_11-0_file-index.json" \
    -o "$1" -v --ignore-missing-files \
    --ignore-extraneous-files -e
}

# Testing that Scorer can handle negative frame numbers
test_21_0() {
    ../ActEV_Scorer.py \
    "ActEV_SDL_V2" \
    -s "data/test_21-0_fake-sysout.json" \
    -r "data/test_11-4.json" \
    -a "data/test_9-0_activity-index.json" \
    -f "data/test_11-0_file-index.json" \
    -o "$1" -v -e
}

# SRL_AD_V1 integration test with AUDC metrics 
test_22_0() {
    ../ActEV_Scorer.py \
    "SRL_AD_V1" \
    -s "data/VIRAT_S_000000_fake-sysout.json" \
    -r "data/VIRAT_S_000000.json" \
    -a "data/VIRAT_S_000000_activity-index.json" \
    -f "data/VIRAT_S_000000_file-index.json" \
    -o "$1" -v
}

# SRL_AD_V1 integration test
# Testing passing of scoring parameters JSON
test_22_1() {
    ../ActEV_Scorer.py \
    "SRL_AD_V1" \
    -s "data/VIRAT_S_000000_fake-sysout.json" \
    -r "data/VIRAT_S_000000.json" \
    -a "data/VIRAT_S_000000_activity-index.json" \
    -f "data/VIRAT_S_000000_file-index.json" \
    -o "$1" \
    -d \
    -p "data/test_1_1.scoring_parameters.json" \
    -v
}

# SRL_AD_V1 integration test
# Check validation only option
test_22_2() {
    ../ActEV_Scorer.py \
    "SRL_AD_V1" \
    -s "data/VIRAT_S_000000_fake-sysout.json" \
    -a "data/VIRAT_S_000000_activity-index.json" \
    -f "data/VIRAT_S_000000_file-index.json" \
    -d -v -V
}

# SRL_AD_V1 integration test
test_22_3() {
    ../ActEV_Scorer.py \
    "SRL_AD_V1" \
    -s "data/VIRAT_S_000001_fake-sysout.json" \
    -r "data/VIRAT_S_000001.json" \
    -a "data/VIRAT_S_000001_activity-index.json" \
    -f "data/VIRAT_S_000001_file-index.json" \
    -o "$1" -d -v
}

# SRL_AD_V1 integration test 3-0
test_22_4() {
    ../ActEV_Scorer.py \
    "SRL_AD_V1" \
    -s "data/test_3-0_fake-sysout.json" \
    -r "data/test_3-0.json" \
    -a "data/test_3-0_activity-index.json" \
    -f "data/test_3-0_file-index.json" \
    -o "$1" -d -v
}

# SRL_AD_V1 using the SmoothCurve test set
test_22_5() {
    ../ActEV_Scorer.py \
    "SRL_AD_V1" \
    -s "data/SmoothCurve.sys.json" \
    -r "data/SmoothCurve.ref.json" \
    -a "data/SmoothCurve.activity-index.json" \
    -f "data/SmoothCurve.file-index.json" \
    -F -o "$1" -v \
    -c ../lib/srl_linear_plot.json
}

# SRL_AD_V2 using the SmoothCurve test set
test_22_6() {
    ../ActEV_Scorer.py \
    "SRL_AD_V2" \
    -s "data/SmoothCurve.sys.json" \
    -r "data/SmoothCurve.ref.json" \
    -a "data/SmoothCurve.activity-index.json" \
    -f "data/SmoothCurve.file-index.json" \
    -F -o "$1" -v \
    -c ../lib/srl_linear_plot.json
}

# SRL_AD_V3 using the SmoothCurve test set
test_22_7() {
    ../ActEV_Scorer.py \
    "SRL_AD_V3" \
    -s "data/SmoothCurve.sys.json" \
    -r "data/SmoothCurve.ref.json" \
    -a "data/SmoothCurve.activity-index.json" \
    -f "data/SmoothCurve.file-index.json" \
    -F -o "$1" -v \
    -c ../lib/srl_linear_plot.json
}

# SRL_AOD_V1 integration test with AUDC metrics 
test_23_0() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V1" \
    -s "data/test_4-0_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_4-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" -v -e
}

# SRL_AOD_V1 integration test
# Check validation only option
test_23_1() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V1" \
    -s "data/test_4-0_fake-sysout.json" \
    -a "data/test_4-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" -d -v -V
}


# SRL_AOD_V1 integration test
# Activity index equivalence class testing
test_23_2() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V1" \
    -s "data/test_4-0_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_5-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" -d -v
}

# SRL_AOD_V1 integration test
# Check for handling of MODE metric over instances with 0 reference
# objects
test_23_3() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V1" \
    -s "data/test_6-0_fake-sysout.json" \
    -r "data/test_6-0.json" \
    -a "data/test_6-0_activity-index.json" \
    -f "data/test_6-0_file-index.json" \
    -o "$1" -d -I -v
}

# integration test 7-0
# Test ignore-extraneous-files (-F) option
test_23_4() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V1" \
    -s "data/test_7-0_fake-sysout.json" \
    -r "data/test_4-0.json" \
    -a "data/test_4-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -F -o "$1" -d -v
}

# SRL_AOD_V1 using the SmoothCurve test set
test_23_5() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V1" \
    -s "data/SmoothCurve.sys.json" \
    -r "data/SmoothCurve.ref.json" \
    -a "data/SmoothCurve.activity-index.json" \
    -f "data/SmoothCurve.file-index.json" \
    -F -o "$1" -v --transformations single_bbox_per_frame \
    -c ../lib/srl_linear_plot.json
}

# SRL_AOD_V2 using the SmoothCurve test set
test_23_6() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V2" \
    -s "data/SmoothCurve.sys.json" \
    -r "data/SmoothCurve.ref.json" \
    -a "data/SmoothCurve.activity-index.json" \
    -f "data/SmoothCurve.file-index.json" \
    -F -o "$1" -v --transformations single_bbox_per_frame \
    -c ../lib/srl_linear_plot.json
}
# SRL_AOD_V3 using the SmoothCurve test set
test_23_7() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V3" \
    -s "data/SmoothCurve.sys.json" \
    -r "data/SmoothCurve.ref.json" \
    -a "data/SmoothCurve.activity-index.json" \
    -f "data/SmoothCurve.file-index.json" \
    -F -o "$1" -v --transformations single_bbox_per_frame \
    -c ../lib/srl_linear_plot.json
}


# Non-regression test for --transformations single_bbox_per_frame
test_24_0() {
    ../ActEV_Scorer.py \
    "SRL_AOD_V1" \
    -s "data/test_24-0_fake-sysout.json" \
    -r "data/test_24-0.json" \
    -a "data/test_5-0_activity-index.json" \
    -f "data/test_4-0_file-index.json" \
    -o "$1" -v --transformations single_bbox_per_frame
}
