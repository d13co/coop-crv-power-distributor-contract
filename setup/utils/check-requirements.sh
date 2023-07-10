#!/usr/bin/env bash

if ! jq --version > /dev/null; then
  echo '"jq"' missing. install with your package manager and try again.
  exit 1
fi
