#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

if [ ! -x "$root/eidolon_gen" ]; then
    printf '%s\n' "error: $root/eidolon_gen is missing or not executable; run make" >&2
    exit 1
fi

exec "${PYTHON:-python3}" -m unittest discover -s "$root/tests" -p 'test_*.py' -v
