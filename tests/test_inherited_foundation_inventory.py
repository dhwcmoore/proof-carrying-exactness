"""
Inventory checks over the INHERITED Rocq foundation and its upstream
provenance record, replacing `test_documentation_module_count.py`
(retired in the same commit that added this file).

That earlier test encoded `regional-obstruction-calculus`'s own
documentation identity -- module-count prose in README.md/STATUS.md/
PROJECT_MAP.md/REPRODUCIBILITY.md, all four deliberately NOT carried
over when this repository was seeded (see docs/UPSTREAM_PROVENANCE.md)
-- not anything about `proof-carrying-exactness` itself. Five of its
six assertions failed for that reason alone, not because anything
about the inherited Rocq foundation was actually wrong: `make check-
rocq` and `make check-rocq-inventory` both continued to pass
throughout. Restoring those four documents merely to satisfy an
inherited test would reintroduce the old repository's identity and
create misleading documentation; retiring the test instead is the
correct fix.

The genuinely useful, mechanical part of the old test -- that the
Makefile's own `ROCQ_MODULES` declaration matches `rocq/*.v` exactly,
with no duplicates and no drift -- is preserved here, alongside two
NEW checks specific to this project's own identity: that `docs/
UPSTREAM_PROVENANCE.md` names a real, verifiable upstream commit, and
that it (not silence) describes the inherited foundation as reference
material. See `tests/test_pce_documentation_contract.py` for the
project-native counterpart covering this repository's OWN documentation
claims (README links, verdict coverage, no premature product claims).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROCQ_DIR = REPO_ROOT / "rocq"
MAKEFILE = REPO_ROOT / "Makefile"
UPSTREAM_PROVENANCE = REPO_ROOT / "docs" / "UPSTREAM_PROVENANCE.md"

EXPECTED_ROCQ_MODULE_COUNT = 37


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _rocq_module_stems() -> set:
    return {p.stem for p in ROCQ_DIR.glob("*.v")}


def _declared_rocq_modules() -> list:
    makefile_text = _read(MAKEFILE)
    match = re.search(r"ROCQ_MODULES\s*:=\s*(.*?)\n\n", makefile_text, re.DOTALL)
    assert match, "Makefile's ROCQ_MODULES assignment not found in the expected form"
    return match.group(1).replace("\\\n", " ").split()


def test_every_declared_rocq_module_file_exists():
    declared = _declared_rocq_modules()
    discovered = _rocq_module_stems()
    missing = [m for m in declared if m not in discovered]
    assert not missing, f"Makefile declares module(s) with no corresponding rocq/*.v file: {missing}"


def test_no_rocq_module_declared_twice():
    declared = _declared_rocq_modules()
    duplicates = {m for m in declared if declared.count(m) > 1}
    assert not duplicates, f"Makefile's ROCQ_MODULES declares duplicate module(s): {sorted(duplicates)}"


def test_declared_and_discovered_rocq_modules_agree():
    declared = _declared_rocq_modules()
    discovered = _rocq_module_stems()
    assert sorted(declared) == sorted(discovered), (
        f"Makefile's ROCQ_MODULES and rocq/*.v disagree -- run `make check-rocq-inventory` "
        f"for the file-by-file diff (declared-only: {sorted(set(declared) - discovered)}, "
        f"discovered-only: {sorted(discovered - set(declared))})"
    )


def test_current_rocq_closure_is_37_modules():
    declared = _declared_rocq_modules()
    assert len(declared) == EXPECTED_ROCQ_MODULE_COUNT, (
        f"expected the inherited Rocq closure to be {EXPECTED_ROCQ_MODULE_COUNT} modules "
        f"(the count verified at import time, docs/UPSTREAM_PROVENANCE.md), found {len(declared)} -- "
        f"if this changed deliberately, update EXPECTED_ROCQ_MODULE_COUNT here and re-verify "
        f"`make check-rocq`/`make check-rocq-inventory` still pass"
    )


def test_upstream_provenance_identifies_verified_source_commit():
    text = _read(UPSTREAM_PROVENANCE)
    match = re.search(r"Exact upstream commit:\s*\n\s*([0-9a-f]{40})", text)
    assert match, "docs/UPSTREAM_PROVENANCE.md does not identify a 40-character upstream commit hash"
    assert "Confirmed directly" in text or "confirmed directly" in text, (
        "docs/UPSTREAM_PROVENANCE.md should state the commit was confirmed, not merely named"
    )


def test_upstream_provenance_describes_foundation_as_inherited_reference_material():
    text = _read(UPSTREAM_PROVENANCE).lower()
    assert "reference material" in text or "imported as reference" in text, (
        "docs/UPSTREAM_PROVENANCE.md should explicitly describe the inherited foundation as "
        "reference material, not silently imply it is this project's own finished work"
    )
