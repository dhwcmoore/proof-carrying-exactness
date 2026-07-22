"""
EXACT verdict tests (SPEC SS6). Traceability: docs/PCE_VERIFIER_TRACEABILITY.md.
"""

from proof_carrying_exactness import verify_certificate_bytes

from pce_fixtures import exact_certificate, exact_common_ancestor_certificate, to_bytes


def test_exact_accepts_valid_repair():
    result = verify_certificate_bytes(to_bytes(exact_certificate()))
    assert result.accepted
    assert result.verdict == "EXACT"


def test_exact_accepts_common_ancestor_case_despite_shared_weak_component():
    # a <- c -> b: no directed path in either direction, so admissible,
    # even though row-a/row-b share one weakly connected component --
    # the completeness case a component-labelling witness could never
    # certify (SPEC SS10).
    result = verify_certificate_bytes(to_bytes(exact_common_ancestor_certificate()))
    assert result.accepted
    assert result.verdict == "EXACT"


def test_exact_rejects_tampered_repair_witness():
    cert = exact_certificate()
    cert["witness"]["repair_witness"][0] = "999"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "D @ u != r" in result.reason


def test_exact_rejects_tampered_factorisation_witness():
    cert = exact_certificate()
    cert["witness"]["factorisation_witness"][0][0] = "999"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_exact_rejects_tampered_claimed_value():
    cert = exact_certificate()
    cert["witness"]["claimed_value"][0] = "999"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "M @ r" in result.reason or "claimed_value" in result.reason


def test_exact_accepts_a_different_but_equally_valid_repair_with_the_same_claim():
    # (-4, -1, 1) = (-5, -2, 0) + (1, 1, 1) is a DIFFERENT, equally
    # valid repair (D u' = r still holds -- (1,1,1) is exactly the
    # gauge direction, ker(D)). M r = x does not even depend on u, so
    # this alternate witness verifies too, with the SAME claimed value
    # -- the concrete demonstration of SPEC SS6's own claim that EXACT
    # does not require a unique internal repair, only a claim invariant
    # across the whole fibre.
    cert = exact_certificate()
    cert["witness"]["repair_witness"] = ["-4", "-1", "1"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert result.accepted
    assert result.verdict == "EXACT"


def test_exact_rejects_a_repair_that_does_not_satisfy_D_u_equals_r():
    cert = exact_certificate()
    cert["witness"]["repair_witness"] = ["0", "0", "0"]  # D @ (0,0,0) = (0,0) != r
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "D @ u != r" in result.reason


def test_exact_requires_L_in_instance():
    cert = exact_certificate()
    del cert["instance"]["L"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_exact_rejects_missing_admissibility_witness():
    cert = exact_certificate()
    del cert["witness"]["admissibility_witness"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
