"""
Locks `docs/PCE_END_TO_END_DEMONSTRATION.md` against silent drift: runs
the real `pce_assess.py` CLI, as a subprocess, over each committed
`examples/pce_assess/*.json` fixture, and asserts the verdict and
`input_digest` match what that document records verbatim. If the
generator, the verifier, or the digest scheme ever changes what these
four instances certify to, this test fails and the documentation claim
is caught out of date rather than silently wrong -- the same discipline
`tests/test_r21_demonstration.py` already establishes for `docs/
R21_END_TO_END_DEMONSTRATION.md`.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples" / "pce_assess"
SUBPROCESS_TIMEOUT = 30

# (verdict, input_digest) as recorded in docs/PCE_END_TO_END_DEMONSTRATION.md.
RECORDED = {
    "exact": ("EXACT", "sha256:1d53c4f0d509d71e7edf2afe857d374b9eedbd69daf39a0c77ed381aa5d6eef2"),
    "underdetermined": ("UNDERDETERMINED", "sha256:50c1cbf6ea9fd156c072637533fd937d957f1085858f02ec95ef41dad1573779"),
    "obstructed": ("OBSTRUCTED", "sha256:e4b1e621a7d20826c3819fd07d645971331ba71f38b35d099b802a903c66a13b"),
    "inadmissible": ("INADMISSIBLE", "sha256:93cb61a7cfbc9af08d5cd28d7d8e150ba1749b3de48800a859621b7d37b19011"),
}


def _run_cli(instance_name: str, cert_path: Path) -> subprocess.CompletedProcess:
    instance_path = EXAMPLES_DIR / f"{instance_name}.json"
    return subprocess.run(
        [sys.executable, "pce_assess.py", str(instance_path), "--certificate-out", str(cert_path)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
    )


def test_example_fixtures_exist_for_all_four_verdicts():
    for instance_name in RECORDED:
        assert (EXAMPLES_DIR / f"{instance_name}.json").exists()


def test_recorded_verdicts_and_digests_still_hold(tmp_path):
    for instance_name, (expected_verdict, expected_digest) in RECORDED.items():
        cert_path = tmp_path / f"{instance_name}.json"
        result = _run_cli(instance_name, cert_path)

        assert result.returncode == 0, result.stdout + result.stderr
        assert f"ACCEPT {expected_verdict}" in result.stdout

        cert = json.loads(cert_path.read_text())
        assert cert["verdict"] == expected_verdict
        assert cert["input_digest"] == expected_digest


def test_recorded_exact_certificate_bytes_are_deterministic_across_cli_runs(tmp_path):
    cert_path_1 = tmp_path / "run1.json"
    cert_path_2 = tmp_path / "run2.json"

    result1 = _run_cli("exact", cert_path_1)
    result2 = _run_cli("exact", cert_path_2)

    assert result1.returncode == 0 and result2.returncode == 0
    assert cert_path_1.read_bytes() == cert_path_2.read_bytes()
