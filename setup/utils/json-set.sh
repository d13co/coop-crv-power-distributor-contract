#!/bin/bash

# utility to set a json key/value with jq

set -e

file=$1
keyvalues=${@:2}

if [ "$file" == "" ]; then
  cd $(dirname $(realpath $0))
  file="constants.json"
fi

if [ ! -f $file ]; then
  echo $file not found
  exit 1
fi

json_set() {
  tmp=$(mktemp)
  v=${@:2}
  jq -c --arg key $1 --argjson value "$v" '.[$key] = $value' $file > $tmp 2> /dev/null || \
    jq -c --arg key $1 --arg value "$v" '.[$key] = $value' $file > $tmp
  mv $tmp $file
  cat $file
}

i=0
for kv in $keyvalues; do
  if [ $(expr $i % 2) == "0" ]; then
    key=$kv
  else
    if [ ${kv:0:1} == "@" ]; then
      kv=$(cat ${kv:1})
    fi
    json_set $key $kv
  fi
  i=$((i+1))
done
