#!/usr/bin/env bash

# summarize.sh
# Author(s): Baptiste Chocot, Jonathan Fiscus

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

# This script compares two outputs from ActEV_Scorer, showing the difference of
# detections between both related systems.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

tm(){
    type=$1
    $DIR/TableMan.pl -t $type -S -T -c Alpha -r Alpha 2> /dev/null 
}

if [ $# -ne 4 ]; then
    echo "usage: $0 <folder_A> <alias_A> <folder_B> <alias_B>"
fi

a=$1
a_alias=$2
b=$3
b_alias=$4

echo "Summary of instance Agreement - new"

awk -F\| '{if ($2 == "CD") {t="agree"; } else if ($2 == "FA") {t="_B_-Only"} else {t="_A_-Only"}; print $1,"Instances-'$b'|Comparisions|"t}' < $b/alignment.csv | sort | uniq -c |  \
    grep -v activ > data
tail -n +2 $b/alignment.csv | egrep '(CD|MD)' |  awk -F\| '{print $1,"Instances-'$b'|RawCount|_A_"}' | sort | uniq -c >> data
tail -n +2 $b/alignment.csv | egrep '(CD|FA)' |  awk -F\| '{print $1,"Instances-'$b'|RawCount|_B_"}' | sort | uniq -c >> data

egrep '(rfa|tfa|tfa_denom|p_miss)\|' $b/scores_by_activity_and_threshold.csv | sed 's/None/0/' | awk -F\| '{print sprintf("%.3f",$4),$1,"Performance|'$b'|"$3}' >> data
egrep '(rfa|tfa|tfa_denom|p_miss)\|' $a/scores_by_activity_and_threshold.csv | sed 's/None/0/' | awk -F\| '{print sprintf("%.3f",$4),$1,"Performance|'$a'|"$3}' >> data

rm -f data.sum
for col in `cat data | awk '{print $3}' | sort -u` ; do
    awk '{if ($3 == "'"$col"'"){print}}' < data | \
	perl -e 'while (<>){@a = split(); $s+=$a[0]; $c=$a[2]; $n++} print "$n ~Overall:N $c\n"; printf("%.3f ~Overall:Mean %s\n",$s/$n,$c)' >> data.sum
done
cat data data.sum | sed 's/\.000//' | perl -pe "s/_A_/$a_alias/g; s/_B_/$b_alias/g" | tm Txt > data.txt
cat data data.sum | sed 's/\.000//' | perl -pe "s/_A_/$a_alias/g; s/_B_/$b_alias/g" | tm HTML > data.html
