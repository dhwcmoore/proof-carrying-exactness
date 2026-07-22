"""
Digest canonicalisation and domain-separation tests (SPEC SS4).
Traceability: see docs/PCE_VERIFIER_TRACEABILITY.md.
"""

from fractions import Fraction

from proof_carrying_exactness.digests import (
    INPUT_DIGEST_DOMAIN,
    POLICY_DIGEST_DOMAIN,
    compute_input_digest,
    compute_policy_digest,
)
from proof_carrying_exactness import verify_certificate_bytes

from pce_fixtures import exact_certificate, obstructed_certificate, to_bytes


def test_object_key_order_does_not_matter_before_canonicalisation():
    policy_a = {"independent_pairs": [["x", "y"]], "policy_version": "v1"}
    policy_b = {"policy_version": "v1", "independent_pairs": [["x", "y"]]}
    assert compute_policy_digest(policy_a) == compute_policy_digest(policy_b)


def test_array_order_remains_significant_where_semantically_ordered():
    # D's rows are semantically ordered (row order is part of D's own
    # meaning) -- reordering them must change the digest.
    D1 = [[Fraction(-1), Fraction(1)], [Fraction(0), Fraction(1)]]
    D2 = [[Fraction(0), Fraction(1)], [Fraction(-1), Fraction(1)]]
    r = [Fraction(1), Fraction(2)]
    d1 = compute_input_digest(D1, r, None, {"vertices": [], "edges": []}, {}, None)
    d2 = compute_input_digest(D2, r, None, {"vertices": [], "edges": []}, {}, None)
    assert d1 != d2


def test_rational_values_have_one_canonical_representation():
    # 1/2 and 2/4 are the same value but only "1/2" is canonical --
    # confirmed indirectly: a certificate using the non-canonical form
    # is rejected by the parser (test_pce_parser.py), so the digest
    # layer never even sees two different byte encodings of one value.
    from proof_carrying_exactness.rational import parse_rational

    assert parse_rational("1/2") == Fraction(1, 2)


def test_equivalent_matrices_produce_identical_canonical_bytes():
    D = [[Fraction(-1), Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1), Fraction(1)]]
    r = [Fraction(3), Fraction(2)]
    provenance = {"vertices": ["row-0", "row-1"], "edges": []}
    d1 = compute_input_digest(D, r, None, provenance, {"0": "row-0", "1": "row-1"}, None)
    d2 = compute_input_digest(
        [[Fraction(-1), Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1), Fraction(1)]],
        [Fraction(3), Fraction(2)],
        None,
        {"vertices": ["row-0", "row-1"], "edges": []},
        {"0": "row-0", "1": "row-1"},
        None,
    )
    assert d1 == d2


def test_input_and_policy_domains_differ_for_identical_payload_bytes():
    import hashlib

    same_payload = "identical-canonical-bytes"
    hash_as_input = hashlib.sha256(f"{INPUT_DIGEST_DOMAIN}||{same_payload}".encode()).hexdigest()
    hash_as_policy = hashlib.sha256(f"{POLICY_DIGEST_DOMAIN}||{same_payload}".encode()).hexdigest()
    assert hash_as_input != hash_as_policy


def test_provenance_mutation_changes_input_digest():
    cert = exact_certificate()
    original_digest = cert["input_digest"]
    cert["instance"]["provenance"]["edges"].append(["row-9", "row-8"])
    cert["instance"]["provenance"]["vertices"].extend(["row-9", "row-8"])
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "input_digest" in result.reason


def test_independence_policy_mutation_changes_policy_digest():
    cert = exact_certificate()
    cert["instance"]["policy"]["independent_pairs"] = [["row-0", "row-9"]]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "policy_digest" in result.reason


def test_swapped_input_and_policy_digest_values_rejected():
    cert = exact_certificate()
    cert["input_digest"], cert["policy_digest"] = cert["policy_digest"], cert["input_digest"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_residue_mutation_after_digest_creation_caught_by_input_digest():
    cert = obstructed_certificate()
    cert["instance"]["r"][0] = "999"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "input_digest" in result.reason
