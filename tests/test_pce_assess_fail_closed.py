"""
Fail-closed / bypass-proof tests for the generic end-to-end boundary.

These run IN-PROCESS (unlike `tests/test_pce_assess_cli.py`'s real
subprocess round trips) because they need to monkeypatch the generator
call itself -- simulating a generator that failed to gate its own
release (or was replaced by something actively malicious) -- to prove
that `assess_instance` and the CLI still never release anything the
production verifier has not independently accepted. This is the
generic-boundary counterpart to `tests/test_generator_fail_closed.py`.
"""

import json

import pytest

import proof_carrying_exactness_assess.assess as assess_module
import proof_carrying_exactness_assess.cli as cli_module
from proof_carrying_exactness_assess import assess_instance

from generator_fixtures import ALL_INSTANCES


def _corrupted_certificate_bytes() -> bytes:
    """A well-formed-looking but semantically bogus certificate: valid
    JSON, plausible shape, but a claimed value that does not follow
    from the residue -- exactly what a buggy or malicious generator
    might hand back if it skipped its own release gate."""
    cert = {
        "schema": "proof-carrying-exactness/certificate/v1",
        "verdict": "EXACT",
        "input_digest": "sha256:" + "0" * 64,
        "policy_digest": "sha256:" + "0" * 64,
        "instance": {
            "D": [["-1", "1", "0"], ["0", "-1", "1"]],
            "r": ["3", "2"],
            "L": [["-1", "0", "1"]],
            "provenance": {"vertices": ["row-0", "row-1"], "edges": []},
            "policy": {"independent_pairs": [["row-0", "row-1"]], "policy_version": "pce-policy/v1"},
            "row_evidence_ids": {"0": "row-0", "1": "row-1"},
        },
        "witness": {
            "repair_witness": ["-5", "-2", "0"],
            "factorisation_witness": [["1", "1"]],
            "claimed_value": ["999999"],  # does not equal M @ r
            "admissibility_witness": {
                "cuts": [{"pair": ["row-0", "row-1"], "left_not_reaches_right": ["row-0"], "right_not_reaches_left": ["row-1"]}]
            },
        },
    }
    return json.dumps(cert).encode("utf-8")


def test_verification_rejection_is_reported_distinctly(monkeypatch):
    monkeypatch.setattr(assess_module, "generate_certificate", lambda instance: _corrupted_certificate_bytes())

    result = assess_instance(json.dumps(ALL_INSTANCES["EXACT"]).encode("utf-8"))

    assert not result.accepted
    assert result.verdict is None
    assert result.certificate_bytes is None
    assert result.reason.startswith(assess_module.STAGE_VERIFICATION_REJECTED + ":")


def test_assess_instance_never_bypasses_the_verifier_even_if_the_generator_does(monkeypatch):
    # Simulate the worst case: the generator itself no longer gates its
    # own release (as if `CertificateGenerationFailed` were never
    # raised) and simply hands back something wrong. The pipeline's OWN
    # explicit call to `verify_certificate_bytes` -- not merely trust in
    # the generator's own internal check -- must still be the thing
    # that stops this from ever reaching `accepted=True`.
    monkeypatch.setattr(assess_module, "generate_certificate", lambda instance: _corrupted_certificate_bytes())

    result = assess_instance(json.dumps(ALL_INSTANCES["EXACT"]).encode("utf-8"))

    assert result.accepted is False


def test_cli_never_bypasses_the_verifier(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(assess_module, "generate_certificate", lambda instance: _corrupted_certificate_bytes())

    instance_path = tmp_path / "exact.json"
    instance_path.write_text(json.dumps(ALL_INSTANCES["EXACT"]), encoding="utf-8")
    cert_path = tmp_path / "certificate.json"

    exit_code = cli_module.main([str(instance_path), "--certificate-out", str(cert_path)])

    assert exit_code == cli_module.EXIT_VERIFICATION_REJECTED
    assert not cert_path.exists()
    captured = capsys.readouterr()
    assert "REJECT" in captured.out
    assert "ACCEPT" not in captured.out
