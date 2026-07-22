"""
UNDERDETERMINED verdict tests (SPEC SS7). Traceability: docs/PCE_VERIFIER_TRACEABILITY.md.
"""

from proof_carrying_exactness import verify_certificate_bytes

from pce_fixtures import underdetermined_certificate, to_bytes


def test_underdetermined_accepts_valid_repair_and_gauge_witness():
    result = verify_certificate_bytes(to_bytes(underdetermined_certificate()))
    assert result.accepted
    assert result.verdict == "UNDERDETERMINED"


def test_underdetermined_rejects_tampered_repair_witness():
    cert = underdetermined_certificate()
    cert["witness"]["repair_witness"][0] = "999"
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "D @ u != r" in result.reason


def test_underdetermined_rejects_gauge_witness_with_Dk_nonzero():
    cert = underdetermined_certificate()
    cert["witness"]["gauge_witness"] = ["1", "1", "2"]  # D @ (1,1,2) != 0
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "D @ k != 0" in result.reason


def test_underdetermined_rejects_gauge_witness_with_Lk_zero():
    cert = underdetermined_certificate()
    cert["witness"]["gauge_witness"] = ["0", "0", "0"]  # D @ 0 = 0 but L @ 0 = 0 too
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
    assert "L @ k == 0" in result.reason


def test_underdetermined_vector_valued_Lk_inequality_means_any_component_nonzero():
    # For a vector-valued claim map (p > 1), "L k != 0" means at least
    # one component is non-zero, not every component. Constructed
    # directly: L' = [[1,0,0],[0,0,0]] against the same D/gauge k =
    # (1,1,1) -- L' k = (1, 0), which has exactly one non-zero
    # component and must still count as "L k != 0".
    from fractions import Fraction

    from proof_carrying_exactness.matrix import is_zero, mat_vec

    L = [[Fraction(1), Fraction(0), Fraction(0)], [Fraction(0), Fraction(0), Fraction(0)]]
    k = [Fraction(1), Fraction(1), Fraction(1)]
    Lk = mat_vec(L, k)
    assert Lk == [Fraction(1), Fraction(0)]
    assert not is_zero(Lk)  # at least one component non-zero -- this counts as L k != 0


def test_underdetermined_alternate_repair_is_derived_not_a_required_field():
    # The certificate's own witness schema has no field for u' at all --
    # confirmed structurally: the closed UNDERDETERMINED witness key set
    # is exactly {repair_witness, gauge_witness, admissibility_witness}.
    from proof_carrying_exactness.schemas import VERDICT_UNDERDETERMINED, WITNESS_KEYS

    assert WITNESS_KEYS[VERDICT_UNDERDETERMINED] == frozenset(
        {"repair_witness", "gauge_witness", "admissibility_witness"}
    )


def test_underdetermined_requires_L_in_instance():
    cert = underdetermined_certificate()
    del cert["instance"]["L"]
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted
