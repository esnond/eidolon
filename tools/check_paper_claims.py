#!/usr/bin/env python3
"""mechanical gate for paper/DRAFT.md and paper/DRAFT_EN.md."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [
    os.path.join(ROOT, "paper", "DRAFT.md"),
    os.path.join(ROOT, "paper", "DRAFT_EN.md"),
]
REQUIRED = [
    ("h1 g1 idu_nat", "3.825"),
    ("h1 g3 idu_nat", "17.096"),
    ("h1b g3 idu_cohort", "0.065"),
    ("exact profile ceiling", "0.3867"),
    ("rf g1 top1", "0.818"),
    ("rf g2 top1", "0.395"),
    ("rf g3 top1", "0.387"),
    ("g6 post-only rf", "0.085"),
    ("g5 rf top1", "0.100"),
    ("g7 open-set eer", "0.455"),
    ("rank-1 participation ratio", "2.380"),
    ("rank-1 first component", "0.500"),
    ("h5 paired difference", "0.0204"),
    ("h5 p value", "0.172"),
    ("h5 achieved power", "0.354"),
    ("h5 mde", "0.285"),
    ("mask scalar mean", "0.4948"),
    ("mask scalar sd", "0.0543"),
]
REQUIRED_STATUS = ["supported", "refuted", "not established", "exploratory", "inconclusive"]
REQUIRED_MARKERS = ["underpowered", "not supported", "honesty check", "exploratory"]


def check_file(path):
    if not os.path.exists(path):
        print("FAIL missing", path)
        return 1
    text = open(path, encoding="utf-8").read()
    errors = 0
    for name, value in REQUIRED:
        if value not in text:
            print("FAIL", os.path.basename(path), "missing", name, value)
            errors += 1
    for status in REQUIRED_STATUS:
        if status not in text:
            print("FAIL", os.path.basename(path), "missing status", status)
            errors += 1
    for marker in REQUIRED_MARKERS:
        if marker not in text.lower():
            print("FAIL", os.path.basename(path), "missing marker", marker)
            errors += 1
    if text.count("exploratory") < 5:
        print("FAIL", os.path.basename(path), "exploratory label appears fewer than 5 times")
        errors += 1
    if "—" in text or "«" in text or "»" in text:
        print("FAIL", os.path.basename(path), "forbidden punctuation")
        errors += 1
    if re.search(r"rank-1[^.\n]{0,40}(подтвержд|confirmed|proven)", text):
        print("FAIL", os.path.basename(path), "rank-1 claimed as confirmed")
        errors += 1
    if re.search(r"g2[^.\n]{0,25}g3[^.\n]{0,40}(неразличим|indistinguishable|equal)", text):
        print("FAIL", os.path.basename(path), "g2/g3 claimed indistinguishable or equal")
        errors += 1
    if re.search(r"\b(доказано|proves|proven)\b", text):
        print("FAIL", os.path.basename(path), "overclaim word")
        errors += 1
    section = text.split("honesty check", 1)
    if len(section) < 2:
        print("FAIL", os.path.basename(path), "honesty check section missing")
        errors += 1
    else:
        rows = [l for l in section[1].split("## 5.", 1)[0].splitlines()
                if l.strip().startswith("|") and "---" not in l]
        if len(rows) < 9:
            print("FAIL", os.path.basename(path), f"honesty table rows {len(rows)}")
            errors += 1
    for m in re.finditer(r"(paper/[A-Za-z0-9_./-]+\.md|results/[A-Za-z0-9_./-]+\.(?:json|csv)|PROVENANCE\.md|README\.md)", text):
        rel = m.group(1)
        if not os.path.exists(os.path.join(ROOT, rel)):
            print("FAIL", os.path.basename(path), "referenced file missing", rel)
            errors += 1
    if errors == 0:
        print("PAPER_GATE_PASS", os.path.basename(path))
    return errors


def main():
    errors = 0
    for path in FILES:
        errors += check_file(path)
    if errors:
        print(f"PAPER_GATE_FAIL: {errors} errors")
        return 1
    print(f"PAPER_GATE_PASS: {len(FILES)} files, {len(REQUIRED)} numbers, {len(REQUIRED_STATUS)} statuses")
    return 0


if __name__ == "__main__":
    sys.exit(main())
