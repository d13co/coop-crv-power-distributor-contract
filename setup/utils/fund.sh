#!/bin/bash

# fund account $dest with $amt algo in sandbox

dest=$1
amt=${2:-500000000000}

if [ "$dest" == "" ]; then
  echo no destination
  exit 1;
fi

src=$(sandbox goal account list | sort -nrk4 | awk '{print $3}' | head -n 1)

echo "Send $amt $src > $dest"

sandbox goal clerk send -f $src -a $amt -t $dest
