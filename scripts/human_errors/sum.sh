#!/usr/bin/env bash


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

tm(){
    type=$1
    $DIR/TableMan.pl -t $type -S -T -c Alpha -r Alpha # 2> /dev/null 
}


cat data data.sum | sed 's/\.000//' | tm Txt > data.txt
cat data data.sum | sed 's/\.000//' | tm HTML > data.html
