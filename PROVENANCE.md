# provenance

version: 1.1.0
date: 2026-10-30

## what is verified

- `make check` runs two generator invocations with the same seed and compares
  them byte for byte. the primary cohort sha256 is
  `7841bd667c35ee437eea9d1c58016990c081ed022d8f042389fb356b487ce1a9`.
- `results/manifest.txt` records the binary sha256, compiler, cflags, seed,
  python versions, environment hash, per file sha256 and the determinism
  verdict.
- the g1, g2 and g4 rows of `data/g5.csv` are byte identical to
  `data/cohort.csv`; only the appended g5 rows differ.
- the second seed 20261031 is used for logreg and rf replication. g3 is
  seed invariant by construction and is not an independent replication.

## what is not verified

- there is no external timestamp authority and no OSF or Zenodo deposit. the
  registration time in `hypotheses.md` is self reported. the file was edited
  later to add exploratory addenda, so the original text is not preserved by
  an independent witness.
- bitwise replay is verified locally with one compiler and one libm. the code
  uses standard `exp`, `log`, `pow`, `sin` and `sqrt`; cross platform bitwise
  equality is `UNCERTAIN` and is not claimed.
- the python pipeline is pinned by `requirements.txt` version numbers, not by
  hash locked wheels. reruns with a different BLAS, CPU or package build can
  differ in the last digits.
- the release tarball is not GPG signed. its sha256 is self attested.

## exploratory analyses

- g5 stochastic intense and the matched 150 class comparison were specified
  after the primary results were known. they are labelled exploratory and do
  not change h1..h7.
- the per model g2/g3 tests and the plurality ceiling correction are
  post hoc corrections to the original average based interpretation.

## release

- `release/eidolon-v1.1.0.tar.gz` excludes `refs/`, object files, the compiled
  binary and the release directory itself. build with `make`.
- `results/manifest.txt` is generated after the release inputs are frozen.
