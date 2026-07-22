"""
Provenance/admissibility tests (SPEC SS9-10): reachability-cut
witnesses for the algebraic verdicts, and the directed, simple-path
witness for INADMISSIBLE. Traceability: docs/PCE_VERIFIER_TRACEABILITY.md.
"""

from fractions import Fraction

import pytest

from proof_carrying_exactness import verify_certificate_bytes
from proof_carrying_exactness.digests import compute_input_digest, compute_policy_digest
from proof_carrying_exactness.errors import CertificateRejected
from proof_carrying_exactness.provenance import verify_admissibility_cuts
from proof_carrying_exactness.schemas import ENVELOPE_SCHEMA

from pce_fixtures import exact_common_ancestor_certificate, to_bytes


def _build_direct_edge_certificate(provenance_edges):
    """A minimal, self-contained EXACT-shaped certificate over a trivial
    1x1 algebraic instance, used only to exercise the admissibility-cut
    mechanism against different provenance shapes."""
    D = [["1"]]
    r = ["1"]
    L = [["1"]]
    provenance = {"vertices": ["a", "b"] + (["c"] if any("c" in e for e in provenance_edges) else []), "edges": provenance_edges}
    policy = {"independent_pairs": [["a", "b"]], "policy_version": "pce-policy/v1"}
    fake_cut = {"cuts": [{"pair": ["a", "b"], "left_not_reaches_right": ["a"], "right_not_reaches_left": ["b"]}]}
    witness = {
        "repair_witness": ["1"],
        "factorisation_witness": [["1"]],
        "claimed_value": ["1"],
        "admissibility_witness": fake_cut,
    }
    D_frac = [[Fraction(x) for x in row] for row in D]
    r_frac = [Fraction(x) for x in r]
    L_frac = [[Fraction(x) for x in row] for row in L]
    return {
        "schema": ENVELOPE_SCHEMA,
        "verdict": "EXACT",
        "input_digest": compute_input_digest(D_frac, r_frac, L_frac, provenance, {}, None),
        "policy_digest": compute_policy_digest(policy),
        "instance": {"D": D, "r": r, "L": L, "provenance": provenance, "policy": policy, "row_evidence_ids": {}},
        "witness": witness,
    }


def test_common_ancestor_case_admissible_despite_shared_weak_component():
    result = verify_certificate_bytes(to_bytes(exact_common_ancestor_certificate()))
    assert result.accepted


def test_direct_edge_defeats_a_falsely_claimed_cut():
    cert = _build_direct_edge_certificate([["a", "b"]])
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_longer_path_defeats_a_falsely_claimed_cut():
    cert = _build_direct_edge_certificate([["a", "c"], ["c", "b"]])
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_cut_omitting_the_required_vertex_itself_rejected():
    cert = exact_common_ancestor_certificate()
    cert["witness"]["admissibility_witness"]["cuts"][0]["left_not_reaches_right"] = []
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_cut_improperly_including_the_excluded_endpoint_rejected():
    cert = exact_common_ancestor_certificate()
    cert["witness"]["admissibility_witness"]["cuts"][0]["left_not_reaches_right"].append("row-b")
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_cut_with_duplicate_vertices_rejected():
    provenance = {"vertices": ["a", "b"], "edges": []}
    policy = {"independent_pairs": [["a", "b"]], "policy_version": "v1"}
    witness = {"cuts": [{"pair": ["a", "b"], "left_not_reaches_right": ["a", "a"], "right_not_reaches_left": ["b"]}]}
    with pytest.raises(CertificateRejected):
        verify_admissibility_cuts(provenance, policy, witness)


def test_cut_with_unknown_vertex_rejected():
    provenance = {"vertices": ["a", "b"], "edges": []}
    policy = {"independent_pairs": [["a", "b"]], "policy_version": "v1"}
    witness = {"cuts": [{"pair": ["a", "b"], "left_not_reaches_right": ["a", "ghost"], "right_not_reaches_left": ["b"]}]}
    with pytest.raises(CertificateRejected):
        verify_admissibility_cuts(provenance, policy, witness)


def test_missing_cut_for_a_declared_independent_pair_rejected():
    provenance = {"vertices": ["a", "b"], "edges": []}
    policy = {"independent_pairs": [["a", "b"]], "policy_version": "v1"}
    witness = {"cuts": []}
    with pytest.raises(CertificateRejected):
        verify_admissibility_cuts(provenance, policy, witness)


def test_no_search_performed_by_admissibility_verification():
    # Structural confirmation, not merely behavioural: verify_admissibility_cuts's
    # own module performs no graph traversal -- see test_pce_import_boundary.py
    # for the mechanical AST-level version of this claim.
    import inspect

    import proof_carrying_exactness.provenance as provenance_module

    source = inspect.getsource(provenance_module)
    assert "def reachable_set" not in source
    assert "def _bfs" not in source
