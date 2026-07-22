"""
OBSTRUCTED verdict tests (SPEC SS8). Traceability: docs/PCE_VERIFIER_TRACEABILITY.md.
"""

from proof_carrying_exactness import verify_certificate_bytes

from pce_fixtures import obstructed_certificate, to_bytes


def test_obstructed_accepts_valid_separator():
    result = verify_certificate_bytes(to_bytes(obstructed_certificate()))
    assert result.accepted
    assert result.verdict == "OBSTRUCTED"


def test_obstructed_rejects_separator_with_nonzero_yTD():
    cert = obstructed_certificate()
    cert["witness"]["separator"][0] = "999"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "y^T @ D != 0" in result.reason


def test_obstructed_rejects_separator_with_zero_yTr():
    cert = obstructed_certificate()
    cert["witness"]["separator"] = ["0", "0", "0", "0"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "y^T @ r == 0" in result.reason


def test_obstructed_forbids_L_as_an_irrelevant_algebraic_field():
    cert = obstructed_certificate()
    cert["instance"]["L"] = [["1"]]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_obstructed_does_not_require_a_claim_map_for_its_own_proof():
    # No L anywhere in a valid OBSTRUCTED certificate at all -- the
    # obstruction test is blocked before claim invariance is relevant
    # (SPEC SS8's own claim-map boundary).
    cert = obstructed_certificate()
    assert "L" not in cert["instance"]


def test_obstructed_claim_metadata_is_optional_and_digest_bound_but_not_checked_mathematically():
    cert = obstructed_certificate()
    assert cert["instance"]["claim_metadata"] == "global coherent assignment of four regional values"
    # Tampering it changes input_digest (digest-bound)...
    tampered = obstructed_certificate()
    tampered["instance"]["claim_metadata"] = "a different attempted claim"
    result = verify_certificate_bytes(to_bytes(tampered))
    assert not result.accepted
    assert "input_digest" in result.reason
