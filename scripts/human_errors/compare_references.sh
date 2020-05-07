#!/usr/bin/env bash

# compare_references.sh
# Author(s): Baptiste Chocot

# This software was developed by employees of the National Institute of
# Standards and Technology (NIST), an agency of the Federal
# Government. Pursuant to title 17 United States Code Section 105, works
# of NIST employees are not subject to copyright protection in the
# United States and are considered to be in the public
# domain. Permission to freely use, copy, modify, and distribute this
# software and its documentation without fee is hereby granted, provided
# that this notice and disclaimer of warranty appears in all copies.

# THE SOFTWARE IS PROVIDED 'AS IS' WITHOUT ANY WARRANTY OF ANY KIND,
# EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
# TO, ANY WARRANTY THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, AND FREEDOM FROM INFRINGEMENT, AND ANY WARRANTY THAT THE
# DOCUMENTATION WILL CONFORM TO THE SOFTWARE, OR ANY WARRANTY THAT THE
# SOFTWARE WILL BE ERROR FREE. IN NO EVENT SHALL NIST BE LIABLE FOR ANY
# DAMAGES, INCLUDING, BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR
# CONSEQUENTIAL DAMAGES, ARISING OUT OF, RESULTING FROM, OR IN ANY WAY
# CONNECTED WITH THIS SOFTWARE, WHETHER OR NOT BASED UPON WARRANTY,
# CONTRACT, TORT, OR OTHERWISE, WHETHER OR NOT INJURY WAS SUSTAINED BY
# PERSONS OR PROPERTY OR OTHERWISE, AND WHETHER OR NOT LOSS WAS
# SUSTAINED FROM, OR AROSE OUT OF THE RESULTS OF, OR USE OF, THE
# SOFTWARE OR SERVICES PROVIDED HEREUNDER.

# Distributions of NIST software should also include copyright and
# licensing statements of any third-party software that are legally
# bundled with the code in compliance with the conditions of those
# licenses.

# This script compares two reference files, produces readable reports.
# WARNING: if a reference is a file, its name must ends with `.json`

if [ $# -ne 4 ]; then
    echo "usage: $0 <reference_A> <reference_B> <file_index> <activity_index>"
    exit 1
fi

refA=$1
refB=$2
fInd=$3
aInd=$4

check_reference () {
    pattern="json$"
    if [ -f $1 ] && ! [[ $1 =~ $pattern ]]; then
        echo "reference file '$1' must end with '.json'"
        exit 1
    fi
}
for ref in $refA $refB
do
    check_reference $ref
done


# STEP 0: Init
DIR=$(cd $(dirname $0) ; pwd)
echo "Scripts directory: $DIR"
wd="tmp-$RANDOM"
mkdir $wd
echo "Working directory: $wd"

# STEP 1: Aggregating if necessary
echo "Aggregating..."
if [[ -d "$refA" ]]; then
    echo "Aggregating A..."
    $DIR/aggregate.py -d $refA -o $wd/refA.json -r
    refA="$wd/refA.json"
fi
if [[ -d "$refB" ]]; then
    echo "Aggregating B..."
    $DIR/aggregate.py -d $refB -o $wd/refB.json -r
    refB="$wd/refB.json"
fi
echo "Aggregation done."

# STEP 2: Reducing data
function rep () {
    echo $1 | rev | cut -d/ -f1 | rev | sed s/json$/$2.json/
}
echo "Reducing..."
$DIR/reduce.py $refA $refB $fInd $wd/reduce
refA="$wd/reduce/$(rep $refA 'reduced')"
refB="$wd/reduce/$(rep $refB 'reduced')"
fInd="$wd/reduce/$(rep $fInd 'reduced')"
echo "Reduce done."

# STEP 3: Generating sysouts
echo "Generating system outputs..."
for ref in $refA $refB
do
    $DIR/ref_to_sysout.py $ref
done
sysA=$(echo $refA | sed s/json$/sysout.json/)
sysB=$(echo $refB | sed s/json$/sysout.json/)
echo "Generate system outputs done."

# STEP 4: Scoring
echo "Scoring..."
$DIR/../ActEV_Scorer.py ActEV_SDL_V2 -s $sysA -r $refB -a $aInd -f $fInd -o $wd/outA_refB -v
$DIR/../ActEV_Scorer.py ActEV_SDL_V2 -s $sysB -r $refA -a $aInd -f $fInd -o $wd/outB_refA -v
echo "Score done."

# STEP 5: Generating report
echo "Generating report..."
$DIR/summarize.sh $wd/outA_refB "System A" $wd/outB_refA "System B"
echo "Generate report done."

# STEP-1: Cleaning
echo "Cleaning..."
rm -rf $wd
echo "Clean done."
