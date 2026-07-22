"""
Cross-verdict substitution tests (SPEC SS11). Traceability: docs/PCE_VERIFIER_TRACEABILITY.md.
"""

from proof_carrying_exactness import verify_certificate_bytes

from pce_fixtures import exact_certificate, inadmissible_certificate, obstructed_certificate, to_bytes


def test_exact_witness_presented_as_obstructed_rejected():
    cert = exact_certificate()
    cert["verdict"] = "OBSTRUCTED"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_obstruction_witness_presented_as_exact_rejected():
    cert = obstructed_certificate()
    cert["verdict"] = "EXACT"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_repair_witness_presented_as_underdetermined_without_gauge_direction_rejected():
    cert = exact_certificate()
    cert["verdict"] = "UNDERDETERMINED"
    del cert["witness"]["factorisation_witness"]
    del cert["witness"]["claimed_value"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_inadmissibility_path_presented_as_obstruction_rejected():
    cert = inadmissible_certificate()
    cert["verdict"] = "OBSTRUCTED"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_exact_certificate_missing_its_factorisation_witness_rejected():
    cert = exact_certificate()
    del cert["witness"]["factorisation_witness"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_extra_instance_field_rejected_under_exact():
    cert = exact_certificate()
    cert["instance"]["claim_metadata"] = "not allowed under EXACT"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_extra_instance_field_rejected_under_underdetermined():
    from pce_fixtures import underdetermined_certificate

    cert = underdetermined_certificate()
    cert["instance"]["claim_metadata"] = "not allowed under UNDERDETERMINED"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_extra_instance_field_rejected_under_obstructed():
    cert = obstructed_certificate()
    cert["instance"]["L"] = [["1"]]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_extra_instance_field_rejected_under_inadmissible():
    cert = inadmissible_certificate()
    cert["instance"]["D"] = [["1"]]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
