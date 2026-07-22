"""
INADMISSIBLE verdict tests (SPEC SS9). Traceability: docs/PCE_VERIFIER_TRACEABILITY.md.
"""

from proof_carrying_exactness import verify_certificate_bytes

from pce_fixtures import inadmissible_certificate, to_bytes


def test_inadmissible_accepts_valid_simple_ancestry_path():
    result = verify_certificate_bytes(to_bytes(inadmissible_certificate()))
    assert result.accepted
    assert result.verdict == "INADMISSIBLE"


def test_rejects_unrecognized_rule_id():
    cert = inadmissible_certificate()
    cert["witness"]["rule_id"] = "independent_rows_no_common_ancestor"  # not yet supported
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "unrecognized rule_id" in result.reason


def test_rejects_unrecognized_direction():
    cert = inadmissible_certificate()
    cert["witness"]["direction"] = "sideways"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "unrecognized direction" in result.reason


def test_rejects_direction_that_does_not_match_the_supplied_path():
    cert = inadmissible_certificate()
    cert["witness"]["direction"] = "left_to_right"  # the actual path only holds right_to_left
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_nonexistent_provenance_edge():
    cert = inadmissible_certificate()
    cert["witness"]["ancestry_path"] = ["row-1", "nonexistent-node", "row-0"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_endpoint_mismatch():
    cert = inadmissible_certificate()
    cert["witness"]["ancestry_path"] = ["row-1", "derived-intermediate", "row-2"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_repeated_vertex_in_ancestry_path():
    cert = inadmissible_certificate()
    cert["witness"]["ancestry_path"] = ["row-1", "derived-intermediate", "row-0", "derived-intermediate", "row-0"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "repeated vertex" in result.reason


def test_rejects_path_referencing_unknown_vertex():
    cert = inadmissible_certificate()
    cert["witness"]["ancestry_path"] = ["row-1", "ghost-vertex"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_policy_no_longer_declaring_the_pair_independent():
    cert = inadmissible_certificate()
    cert["instance"]["policy"]["independent_pairs"] = [["row-0", "row-9"]]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_rejects_path_with_fewer_than_two_entries():
    cert = inadmissible_certificate()
    cert["witness"]["ancestry_path"] = ["row-0"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_inadmissible_forbids_D_r_L_entirely():
    cert = inadmissible_certificate()
    assert "D" not in cert["instance"]
    assert "r" not in cert["instance"]
    assert "L" not in cert["instance"]

    for field, value in [("D", [["1"]]), ("r", ["1"]), ("L", [["1"]])]:
        tampered = inadmissible_certificate()
        tampered["instance"][field] = value
        result = verify_certificate_bytes(to_bytes(tampered))
        assert not result.accepted, f"expected {field!r} to be rejected under INADMISSIBLE"
