"""pipeline regression tests for eidolon, standard library unittest only."""
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "eidolon_gen"
PYTHON_DIR = ROOT / "python"
RESULTS_DIR = ROOT / "results"

CSV_HEADER = (
    "patient_id,group,day,t_s,action_seq,interval_ms,session_dur_s,"
    "action_id,section_id,is_repeat,session_idx,day_of_week,is_weekend"
)
TINY_ARGS = [
    "--seed", "20261030",
    "--days", "10",
    "--n1", "2",
    "--n2", "2",
    "--n3", "2",
    "--n4", "2",
]
EXPECTED_FEATURES = 51


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_tiny(out_path):
    command = [str(BINARY), *TINY_ARGS, "--out", str(out_path)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"generator failed with {result.returncode}: {result.stderr.strip()}"
        )
    return out_path


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class TinyCohortTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not BINARY.is_file():
            raise RuntimeError(f"missing generator {BINARY}; run make first")
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="eidolon-test-"))
        cls.addClassCleanup(shutil.rmtree, cls.tmpdir, ignore_errors=True)
        cls.first = generate_tiny(cls.tmpdir / "first.csv")
        cls.second = generate_tiny(cls.tmpdir / "second.csv")

    def test_generation_is_byte_identical(self):
        self.assertGreater(self.first.stat().st_size, 0)
        self.assertEqual(self.first.read_bytes(), self.second.read_bytes())
        self.assertEqual(sha256_file(self.first), sha256_file(self.second))

    def test_header_matches_frozen_schema_and_fields_are_integers(self):
        with open(self.first, newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            self.assertEqual(",".join(header), CSV_HEADER)
            self.assertEqual(len(header), 13)
            rows = 0
            for row in reader:
                self.assertEqual(len(row), len(header))
                for field in row:
                    if re.fullmatch(r"[0-9]+", field) is None:
                        self.fail(f"not an integer csv field {field!r} in row {row!r}")
                rows += 1
        self.assertGreater(rows, 0)

    def test_group_counts_and_patient_id_range(self):
        rows = read_rows(self.first)
        self.assertGreater(len(rows), 0)
        group_patients = {group: set() for group in (1, 2, 3, 4)}
        patient_ids = set()
        for row in rows:
            patient_id = int(row["patient_id"])
            group = int(row["group"])
            self.assertIn(group, group_patients)
            patient_ids.add(patient_id)
            group_patients[group].add(patient_id)
        counts = Counter({group: len(pids) for group, pids in group_patients.items()})
        self.assertEqual(counts, Counter({1: 2, 2: 2, 3: 2, 4: 2}))
        self.assertEqual(sorted(patient_ids), list(range(8)))
        self.assertEqual(min(patient_ids), 0)
        self.assertEqual(max(patient_ids), 7)


class FeatureExtractionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(PYTHON_DIR))
        try:
            import eidolon_features
        except ModuleNotFoundError as exc:
            raise RuntimeError(f"feature dependencies are not installed: {exc}")
        cls.ef = eidolon_features
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="eidolon-features-"))
        cls.addClassCleanup(shutil.rmtree, cls.tmpdir, ignore_errors=True)
        cohort = generate_tiny(cls.tmpdir / "cohort.csv")
        cls.features, cls.raw = cls.ef.build_features(
            str(cohort), str(cls.tmpdir / "features_raw.csv")
        )

    def test_feature_matrix_has_expected_columns(self):
        self.assertEqual(len(self.ef.FEATURE_NAMES), EXPECTED_FEATURES)
        expected = ["patient_id", "group", "window"] + self.ef.FEATURE_NAMES
        self.assertEqual(list(self.features.columns), expected)
        self.assertGreater(len(self.features), 0)
        self.assertGreater(len(self.raw), 0)

    def test_all_feature_values_are_finite(self):
        values = self.features[self.ef.FEATURE_NAMES].to_numpy(dtype=float)
        self.assertEqual(values.shape[1], EXPECTED_FEATURES)
        for value in values.ravel():
            if not math.isfinite(float(value)):
                self.fail(f"feature value is not finite: {value!r}")


class EmptyWindowGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(PYTHON_DIR))
        import eidolon_features
        cls.ef = eidolon_features
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="eidolon-guard-"))
        cls.addClassCleanup(shutil.rmtree, cls.tmpdir, ignore_errors=True)
        cls.cohort = generate_tiny(cls.tmpdir / "cohort.csv")

    def test_empty_window_raises_value_error(self):
        pd = self.ef.pd
        empty = pd.DataFrame(columns=list(self.ef.DTYPES))
        # groupby never yields empty groups; patch it to reach the defensive guard.
        groups = [((0, 1), empty)]
        with mock.patch.object(pd.DataFrame, "groupby", return_value=groups):
            with self.assertRaisesRegex(ValueError, "empty window"):
                self.ef.build_features(
                    str(self.cohort), str(self.tmpdir / "guard_raw.csv")
                )


class ResultsJsonTest(unittest.TestCase):
    @staticmethod
    def reject_constant(token):
        raise ValueError(f"json constant is not allowed: {token!r}")

    def test_results_json_is_strict_and_finite(self):
        paths = sorted(RESULTS_DIR.glob("*.json"))
        if not paths:
            self.skipTest("no results/*.json present")
        for path in paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                try:
                    json.loads(text, parse_constant=self.reject_constant)
                except ValueError as exc:
                    self.fail(f"{path.name} is not strict json: {exc}")


if __name__ == "__main__":
    unittest.main()
