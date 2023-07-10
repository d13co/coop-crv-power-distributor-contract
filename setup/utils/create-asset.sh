#!/usr/bin/env bash

# create asset in sandbox

set -e

creator=$1
name=$2
unitname=$3
total=$4

if [ "$total" == "" ]; then
  echo Expected CREATOR NAME UNITNAME TOTAL
  exit 1
fi

echo "Creating $name($unitname) with $creator"

output=$(sandbox goal asset create --creator $creator --name "$name" --unitname "$unit" --total $total)

aid=$(echo "$output" | grep -oE "Created asset with asset index [0-9]+" | grep -oE '[0-9]+')
if [ "$aid" == "" ];then
  echo ERROR CREATING $name $unitname
  echo -e "$output"
  echo ERROR CREATING $name $unitname
  exit 1
fi
echo $unitname aid=$aid

# ./utils/json-set.sh ./config/assets/aids.json "$unitname" $aid > /dev/null

echo -n "$unitname $aid " >> ./config/assets/temp.txt
