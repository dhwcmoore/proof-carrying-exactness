"""
Strict parser tests for proof_carrying_exactness (SPEC SS3, SS5).
Traceability: see docs/PCE_VERIFIER_TRACEABILITY.md.
"""

import pytest

from proof_carrying_exactness import verify_certificate_bytes

from pce_fixtures import exact_certificate, to_bytes


def test_rejects_non_bytes_gracefully():
    # verify_certificate_bytes never raises -- even for a wrong input type.
    result = verify_certificate_bytes("not bytes")  # type: ignore[arg-type]
    assert not result.accepted


def test_rejects_malformed_json():
    result = verify_certificate_bytes(b"{not json")
    assert not result.accepted


def test_rejects_malformed_utf8():
    result = verify_certificate_bytes(b"\xff\xfe\x00\x01")
    assert not result.accepted


def test_rejects_duplicate_top_level_key():
    raw = to_bytes(exact_certificate()).decode()
    # Splice in a duplicate "verdict" key by hand -- json.dumps never
    # produces one, so this exercises the object_pairs_hook directly.
    tampered = raw.replace('"verdict": "EXACT"', '"verdict": "EXACT", "verdict": "OBSTRUCTED"', 1)
    result = verify_certificate_bytes(tampered.encode())
    assert not result.accepted


def test_rejects_duplicate_key_at_any_nesting_level():
    # Duplicate-key rejection is a property of the parser
    # (object_pairs_hook applies to EVERY JSON object encountered, not
    # just the top level), tested directly and in isolation rather than
    # via fragile string surgery on a full certificate.
    from proof_carrying_exactness.canonical import strict_json_loads
    from proof_carrying_exactness.errors import CertificateRejected

    nested_duplicate = b'{"a": {"x": 1, "x": 2}}'
    with pytest.raises(CertificateRejected):
        strict_json_loads(nested_duplicate)


def test_rejects_unknown_top_level_key():
    cert = exact_certificate()
    cert["unexpected_field"] = "surprise"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_unknown_verdict_specific_instance_key():
    cert = exact_certificate()
    cert["instance"]["claim_metadata"] = "not allowed under EXACT"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_unknown_witness_key():
    cert = exact_certificate()
    cert["witness"]["surprise_field"] = "1"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_missing_required_key():
    cert = exact_certificate()
    del cert["witness"]["factorisation_witness"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_incorrect_json_type_for_matrix():
    cert = exact_certificate()
    cert["instance"]["D"] = "not a matrix"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_floating_point_rational():
    cert = exact_certificate()
    cert["instance"]["r"][0] = "3.0"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_non_canonical_rational_string():
    cert = exact_certificate()
    cert["instance"]["r"][0] = "6/2"  # not in lowest terms
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_negative_denominator():
    cert = exact_certificate()
    cert["witness"]["claimed_value"][0] = "5/-1"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_ragged_matrix():
    cert = exact_certificate()
    cert["instance"]["D"][0] = ["-1", "1"]  # now shorter than the other row
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_dimension_mismatch_between_D_and_r():
    cert = exact_certificate()
    cert["instance"]["r"].append("0")
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_accepts_well_formed_certificate():
    result = verify_certificate_bytes(to_bytes(exact_certificate()))
    assert result.accepted
    assert result.verdict == "EXACT"


@pytest.mark.parametrize("bad_schema", ["proof-carrying-exactness/certificate/v2", "", None])
def test_rejects_unrecognized_schema(bad_schema):
    cert = exact_certificate()
    cert["schema"] = bad_schema
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_unrecognized_verdict():
    cert = exact_certificate()
    cert["verdict"] = "MOSTLY_EXACT"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
