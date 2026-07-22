"""
End-to-end CLI tests for `pce_assess.py`, run as real subprocesses
against the actual script -- the same convention this repository's own
`tests/test_r21_certificates.py` and `tests/test_tracking_adapter_*.py`
already establish for their CLI round trips (a real process boundary,
not merely calling a Python function in-process).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from proof_carrying_exactness import verify_certificate_bytes

from generator_fixtures import ALL_INSTANCES

REPO_ROOT = Path(__file__).resolve().parent.parent
SUBPROCESS_TIMEOUT = 30


def _write_instance(tmp_path: Path, name: str, instance: dict) -> Path:
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(instance), encoding="utf-8")
    return path


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "pce_assess.py", *args],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
    )


@pytest.mark.parametrize("verdict", sorted(ALL_INSTANCES))
def test_cli_complete_run_for_each_verdict(tmp_path, verdict):
    instance_path = _write_instance(tmp_path, verdict.lower(), ALL_INSTANCES[verdict])
    cert_path = tmp_path / f"{verdict.lower()}_certificate.json"

    result = _run_cli(str(instance_path), "--certificate-out", str(cert_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"ACCEPT {verdict}" in result.stdout
    assert "Certificate verified independently." in result.stdout
    assert cert_path.exists()

    verification = verify_certificate_bytes(cert_path.read_bytes())
    assert verification.accepted
    assert verification.verdict == verdict


@pytest.mark.parametrize("verdict", sorted(ALL_INSTANCES))
def test_human_readable_wording_for_each_verdict(tmp_path, verdict):
    expected_wording = {
        "EXACT": "Claim is invariant across every permitted repair.",
        "UNDERDETERMINED": "the declared claim changes along a permitted gauge direction",
        "OBSTRUCTED": "No permitted repair reconciles the evidence",
        "INADMISSIBLE": "ancestry relation exists between evidence declared independent",
    }[verdict]
    instance_path = _write_instance(tmp_path, verdict.lower(), ALL_INSTANCES[verdict])

    result = _run_cli(str(instance_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert expected_wording in result.stdout


def test_certificate_bytes_are_deterministic_across_separate_cli_runs(tmp_path):
    instance_path = _write_instance(tmp_path, "exact", ALL_INSTANCES["EXACT"])
    cert_path_1 = tmp_path / "cert1.json"
    cert_path_2 = tmp_path / "cert2.json"

    result1 = _run_cli(str(instance_path), "--certificate-out", str(cert_path_1))
    result2 = _run_cli(str(instance_path), "--certificate-out", str(cert_path_2))

    assert result1.returncode == 0 and result2.returncode == 0
    assert cert_path_1.read_bytes() == cert_path_2.read_bytes()


def test_malformed_json_exits_nonzero_and_writes_no_certificate(tmp_path):
    instance_path = tmp_path / "bad.json"
    instance_path.write_text("{not valid json", encoding="utf-8")
    cert_path = tmp_path / "certificate.json"

    result = _run_cli(str(instance_path), "--certificate-out", str(cert_path))

    assert result.returncode == 1
    assert "REJECT" in result.stdout
    assert not cert_path.exists()


def test_malformed_instance_schema_exits_nonzero_and_writes_no_certificate(tmp_path):
    instance_path = tmp_path / "bad_schema.json"
    instance_path.write_text(json.dumps({"D": "not-a-matrix", "r": ["1"]}), encoding="utf-8")
    cert_path = tmp_path / "certificate.json"

    result = _run_cli(str(instance_path), "--certificate-out", str(cert_path))

    assert result.returncode == 1
    assert "REJECT" in result.stdout
    assert not cert_path.exists()


def test_unrecognized_instance_field_is_a_malformed_schema_rejection(tmp_path):
    instance = dict(ALL_INSTANCES["EXACT"])
    instance["unexpected_field"] = True
    instance_path = _write_instance(tmp_path, "extra_field", instance)
    cert_path = tmp_path / "certificate.json"

    result = _run_cli(str(instance_path), "--certificate-out", str(cert_path))

    assert result.returncode == 1
    assert not cert_path.exists()


def test_generator_failure_exits_nonzero_and_writes_no_certificate(tmp_path):
    # Schema-valid (no unrecognized fields, correct shapes), but neither
    # an admissibility violation nor an algebraic system (D, r) is
    # supplied -- the generator has nothing to certify.
    instance = {
        "provenance": {"vertices": ["row-0", "row-1"], "edges": []},
        "policy": {"independent_pairs": [], "policy_version": "pce-policy/v1"},
    }
    instance_path = _write_instance(tmp_path, "unresolvable", instance)
    cert_path = tmp_path / "certificate.json"

    result = _run_cli(str(instance_path), "--certificate-out", str(cert_path))

    assert result.returncode == 2
    assert "REJECT" in result.stdout
    assert "No certificate could be generated" in result.stdout
    assert not cert_path.exists()


def test_unwritable_output_path_exits_nonzero(tmp_path):
    instance_path = _write_instance(tmp_path, "exact", ALL_INSTANCES["EXACT"])
    unwritable_path = tmp_path / "no-such-directory" / "certificate.json"

    result = _run_cli(str(instance_path), "--certificate-out", str(unwritable_path))

    assert result.returncode == 4
    assert "ACCEPT EXACT" in result.stdout  # verification itself succeeded; only the write failed
    assert not unwritable_path.exists()
    assert not unwritable_path.parent.exists()


def test_missing_instance_file_exits_nonzero(tmp_path):
    result = _run_cli(str(tmp_path / "does-not-exist.json"))
    assert result.returncode == 1
    assert "REJECT" in result.stdout


def test_exit_code_contract(tmp_path):
    # One assertion per documented exit code, all in one place so the
    # contract itself (not just each individual scenario) is pinned.
    exact_path = _write_instance(tmp_path, "exact", ALL_INSTANCES["EXACT"])
    assert _run_cli(str(exact_path)).returncode == 0

    bad_json_path = tmp_path / "bad.json"
    bad_json_path.write_text("{not valid json", encoding="utf-8")
    assert _run_cli(str(bad_json_path)).returncode == 1

    unresolvable_path = _write_instance(tmp_path, "unresolvable", {
        "provenance": {"vertices": [], "edges": []},
        "policy": {"independent_pairs": [], "policy_version": "pce-policy/v1"},
    })
    assert _run_cli(str(unresolvable_path)).returncode == 2

    unwritable_path = tmp_path / "no-such-directory" / "certificate.json"
    assert _run_cli(str(exact_path), "--certificate-out", str(unwritable_path)).returncode == 4
