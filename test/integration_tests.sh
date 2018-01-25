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
    diff -r "$checkfile_outdir" "$compcheckfile_outdir"
    check_status
    
    echo "*** OK ***"
}

# ActEV18 integration test 1
test_1_0() {
    ../ActEV_Scorer.py \
	"ActEV18" \
	-s "data/VIRAT_S_000000_fake-sysout.json" \
	-r "data/VIRAT_S_000000.json" \
	-a "data/VIRAT_S_000000_activity-index.json" \
	-f "data/VIRAT_S_000000_file-index.json" \
	-o "$1" \
	-d \
	-v
}

# ActEV18 integration test 2
test_2_0() {
    ../ActEV_Scorer.py \
	"ActEV18" \
	-s "data/VIRAT_S_000001_fake-sysout.json" \
	-r "data/VIRAT_S_000001.json" \
	-a "data/VIRAT_S_000001_activity-index.json" \
	-f "data/VIRAT_S_000001_file-index.json" \
	-o "$1" \
	-d \
	-v
}
