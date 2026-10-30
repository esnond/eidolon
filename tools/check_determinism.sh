#!/bin/sh
set -eu
BIN=${1:-./eidolon_gen}
SEED=${2:-20261030}
AGAINST=${3:-}
TMP=$(mktemp -d)
: "${TMPDIR:=/tmp}"
trap 'rm -rf "$TMP"' EXIT
"$BIN" --seed "$SEED" --out "$TMP/run1.csv"
"$BIN" --seed "$SEED" --out "$TMP/run2.csv"
if ! cmp -s "$TMP/run1.csv" "$TMP/run2.csv"; then
    echo "DETERMINISM_BROKEN: run1 != run2"
    exit 1
fi
if [ "$AGAINST" = "--against-published" ] && [ -f data/cohort.csv ]; then
    if ! cmp -s "$TMP/run1.csv" data/cohort.csv; then
        echo "DETERMINISM_BROKEN: replay != data/cohort.csv"
        exit 1
    fi
fi
echo "DETERMINISM_PASS"
sha256sum "$TMP/run1.csv" "$TMP/run2.csv"
