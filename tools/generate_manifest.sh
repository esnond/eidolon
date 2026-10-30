#!/bin/sh
set -eu
SEED=${1:-20261030}
OUT=results/manifest.txt
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p results
{
    echo "# eidolon reproducibility manifest"
    echo "# generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# version: $(cat VERSION 2>/dev/null || echo unversioned)"
    echo "# binary: eidolon_gen"
    echo "# binary_sha256: $(sha256sum eidolon_gen | cut -d' ' -f1)"
    echo "# compiler: $(cc --version | head -1)"
    echo "# cflags: -std=c99 -pedantic -Wall -Wextra -Werror -O2 -ffp-contract=off"
    echo "# seed: $SEED"
    echo "# python: $(python3 --version)"
    echo "# python_env_sha256: $(python3 -m pip freeze 2>/dev/null | sort | sha256sum | cut -d' ' -f1)"
    python3 - <<'PY'
import numpy, pandas, sklearn, scipy, matplotlib
print(f"# numpy: {numpy.__version__}")
print(f"# pandas: {pandas.__version__}")
print(f"# sklearn: {sklearn.__version__}")
print(f"# scipy: {scipy.__version__}")
print(f"# matplotlib: {matplotlib.__version__}")
PY
    START=$(date +%s)
    ./eidolon_gen --seed "$SEED" --out "$TMP/replay.csv"
    END=$(date +%s)
    echo "# generator_replay_seconds: $((END - START))"
    if cmp -s data/cohort.csv "$TMP/replay.csv"; then
        echo "# determinism: PASS (cmp data/cohort.csv vs replay)"
    else
        echo "# determinism: FAIL"
    fi
    echo "# cohort_sha256: $(sha256sum data/cohort.csv | cut -d' ' -f1)"
    echo "# chaos_sha256: $(sha256sum data/chaos.csv | cut -d' ' -f1)"
    echo "# g5_sha256: $(sha256sum data/g5.csv | cut -d' ' -f1)"
    echo "# chaos_flags: --chaos --n1 100 --n2 0 --n3 0 --n4 0"
    echo "# g5_flags: --n1 200 --n2 150 --n3 150 --n4 100 --n5 150"
    echo
    echo "## hashes"
    find data results paper src python tools tests -type f \
        \( -name '*.csv' -o -name '*.json' -o -name '*.png' -o -name '*.md' \
        -o -name '*.py' -o -name '*.c' -o -name '*.h' -o -name '*.sh' \) \
        ! -name 'manifest.txt' -print0 2>/dev/null \
        | sort -z | xargs -0 sha256sum
    sha256sum Makefile hypotheses.md README.md requirements.txt VERSION LICENSE LICENSE-CC-BY-4.0 NOTICE CITATION.cff PROVENANCE.md 2>/dev/null || true
} > "$OUT"
if grep -q "determinism: FAIL" "$OUT"; then
    echo "DETERMINISM_BROKEN: manifest not published" >&2
    exit 1
fi
echo "wrote $OUT"
