#!/bin/sh
set -eu
BIN=${1:-./eidolon_gen}
SEED=${2:-20261030}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
"$BIN" --seed "$SEED" --out "$TMP/g5.csv" \
    --n1 200 --n2 150 --n3 150 --n4 100 --n5 150
N=$(wc -l < data/cohort.csv)
head -n "$N" "$TMP/g5.csv" > "$TMP/head.csv"
if cmp -s "$TMP/head.csv" data/cohort.csv; then
    echo "G5_ISOLATION_PASS"
else
    echo "G5_ISOLATION_BROKEN: g1-g4 rows changed"
    exit 1
fi
