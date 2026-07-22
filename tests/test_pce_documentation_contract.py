"""
Documentation-contract test for `proof-carrying-exactness` ITSELF --
the project-native counterpart to
`tests/test_inherited_foundation_inventory.py` (which covers the
inherited Rocq foundation and its upstream provenance record). Checks
this repository's own README makes exactly the claims it should, links
to the documents it should, and does NOT announce a product that has
not been built yet.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
TRACEABILITY = REPO_ROOT / "docs" / "PCE_VERIFIER_TRACEABILITY.md"
GENERATOR_TRACEABILITY = REPO_ROOT / "docs" / "PCE_GENERATOR_TRACEABILITY.md"
GENERATOR_PACKAGE_DIR = REPO_ROOT / "proof_carrying_exactness_generator"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_links_to_the_semantic_spec():
    assert "PROOF_CARRYING_EXACTNESS_SPEC.md" in _read(README)


def test_readme_links_to_the_certificate_spec():
    assert "PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md" in _read(README)


def test_readme_links_to_upstream_provenance():
    text = _read(README)
    assert "UPSTREAM_PROVENANCE.md" in text


def test_traceability_manifest_exists():
    assert TRACEABILITY.exists()


def test_generator_traceability_manifest_exists():
    assert GENERATOR_TRACEABILITY.exists()


def _assert_all_named_test_files_exist(manifest: Path) -> None:
    text = _read(manifest)
    # Matches `test_pce_whatever.py` (with or without a `::test_name`
    # suffix, and with or without a leading `tests/`) anywhere in the
    # manifest's prose or tables.
    named_files = sorted(set(re.findall(r"(test_[A-Za-z0-9_]+\.py)", text)))
    assert named_files, f"no test file names found in {manifest.name} -- did its format change?"
    missing = [name for name in named_files if not (REPO_ROOT / "tests" / name).exists()]
    assert not missing, f"{manifest.name} names test file(s) that do not exist: {missing}"


def test_every_test_path_named_in_the_traceability_manifest_exists():
    _assert_all_named_test_files_exist(TRACEABILITY)


def test_every_test_path_named_in_the_generator_traceability_manifest_exists():
    _assert_all_named_test_files_exist(GENERATOR_TRACEABILITY)


def test_readme_describes_all_four_verdicts():
    text = _read(README)
    for verdict in ("EXACT", "UNDERDETERMINED", "OBSTRUCTED", "INADMISSIBLE"):
        assert verdict in text, f"README.md does not mention the {verdict!r} verdict"


def test_readme_does_not_announce_an_unbuilt_cli_or_adapter():
    # These specific phrases must not appear as though describing
    # something ALREADY BUILT (e.g. "pce-assess accepts...", "the
    # tracking adapter integrates..."). Checked over the whole document
    # with a nearby-negation window (not line-by-line, since markdown
    # soft-wraps a sentence's negation onto a different line than the
    # phrase it negates) -- the README's own current wording only ever
    # uses these phrases negatively ("no pce-assess", "not yet built: ...
    # a command-line assessment tool"); this test guards against that
    # flipping to an affirmative claim without a corresponding
    # implementation commit. (The generator itself is now built and
    # deliberately NOT in this list -- see test_generator_package_exists
    # and test_readme_identifies_the_generator_package_as_untrusted.)
    text = _read(README)
    negations = ("no ", "not yet", "not built", "does not")
    for phrase in (
        "pce-assess",
        "command-line assessment tool",
        "region-native adapter",
        "tracking/sensor-fusion adapter",
        "end-to-end demonstration",
    ):
        for match in re.finditer(re.escape(phrase), text):
            window = text[max(0, match.start() - 80):match.start()].lower()
            assert any(neg in window for neg in negations), (
                f"README.md mentions {phrase!r} without a nearby negation -- confirm this reflects "
                f"something actually built, not a premature claim (context: {text[max(0, match.start()-80):match.end()+20]!r})"
            )


def test_generator_package_exists():
    assert GENERATOR_PACKAGE_DIR.is_dir()
    assert (GENERATOR_PACKAGE_DIR / "__init__.py").exists()


def test_readme_identifies_the_generator_package_as_untrusted():
    # The generator now exists -- unlike the CLI/adapter/demonstrator,
    # this claim must be POSITIVE, not negated. It must name the actual
    # package and describe it as untrusted/outside the trusted
    # computing base, not merely mention the word "generator" in
    # passing.
    text = _read(README)
    assert "proof_carrying_exactness_generator" in text, (
        "README.md does not mention the proof_carrying_exactness_generator package"
    )
    lowered = text.lower()
    assert "untrusted" in lowered or "trusted computing base" in lowered, (
        "README.md mentions the generator package but never describes it as untrusted "
        "or outside the trusted computing base"
    )
