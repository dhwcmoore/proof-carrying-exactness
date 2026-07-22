"""
tests/pce_fixtures.py

Certificate fixtures for the proof_carrying_exactness production test
suite, expressed directly against the production schema/digest API --
NOT by importing or executing the untracked spike_certificates/
generator. Every witness value below (u, M, x, k, y, cuts, the
ancestry path) is a concrete rational already independently verified
against this project's own inherited R21 solver during the spike
passes recorded in docs/design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_
SPEC.md -- hardcoded here rather than re-derived, so this test module
itself needs no solving/search machinery at all.
"""

import json

from proof_carrying_exactness.digests import compute_input_digest, compute_policy_digest
from proof_carrying_exactness.schemas import ENVELOPE_SCHEMA


def _frac_matrix(rows):
    return [[str(x) for x in row] for row in rows]


def _envelope(verdict, D, r, L, provenance, policy, row_evidence_ids, claim_metadata, witness):
    from fractions import Fraction

    D_frac = [[Fraction(x) for x in row] for row in D] if D is not None else None
    r_frac = [Fraction(x) for x in r] if r is not None else None
    L_frac = [[Fraction(x) for x in row] for row in L] if L is not None else None

    instance = {"provenance": provenance, "policy": policy, "row_evidence_ids": row_evidence_ids}
    if D is not None:
        instance["D"] = D
        instance["r"] = r
    if L is not None:
        instance["L"] = L
    if claim_metadata is not None:
        instance["claim_metadata"] = claim_metadata

    return {
        "schema": ENVELOPE_SCHEMA,
        "verdict": verdict,
        "input_digest": compute_input_digest(D_frac, r_frac, L_frac, provenance, row_evidence_ids, claim_metadata),
        "policy_digest": compute_policy_digest(policy),
        "instance": instance,
        "witness": witness,
    }


def exact_certificate() -> dict:
    """D = [[-1,1,0],[0,-1,1]], r = (3,2), L = [-1,0,1] (claim: u3-u1).
    ker(D) = span{(1,1,1)}; L annihilates it. u = (-5,-2,0), M = [1,1],
    x = M r = (5)."""
    D = [["-1", "1", "0"], ["0", "-1", "1"]]
    r = ["3", "2"]
    L = [["-1", "0", "1"]]
    provenance = {"vertices": ["row-0", "row-1"], "edges": []}
    policy = {"independent_pairs": [["row-0", "row-1"]], "policy_version": "pce-policy/v1"}
    row_evidence_ids = {"0": "row-0", "1": "row-1"}
    witness = {
        "repair_witness": ["-5", "-2", "0"],
        "factorisation_witness": [["1", "1"]],
        "claimed_value": ["5"],
        "admissibility_witness": {
            "cuts": [{"pair": ["row-0", "row-1"], "left_not_reaches_right": ["row-0"], "right_not_reaches_left": ["row-1"]}]
        },
    }
    return _envelope("EXACT", D, r, L, provenance, policy, row_evidence_ids, None, witness)


def underdetermined_certificate() -> dict:
    """Identical D, r to exact_certificate(); claim map L = [0,0,1]
    (claim: u3 alone) does NOT annihilate ker(D). u = (-5,-2,0),
    k = (1,1,1) (D k = 0, L k = (1) != 0)."""
    D = [["-1", "1", "0"], ["0", "-1", "1"]]
    r = ["3", "2"]
    L = [["0", "0", "1"]]
    provenance = {"vertices": ["row-0", "row-1"], "edges": []}
    policy = {"independent_pairs": [["row-0", "row-1"]], "policy_version": "pce-policy/v1"}
    row_evidence_ids = {"0": "row-0", "1": "row-1"}
    witness = {
        "repair_witness": ["-5", "-2", "0"],
        "gauge_witness": ["1", "1", "1"],
        "admissibility_witness": {
            "cuts": [{"pair": ["row-0", "row-1"], "left_not_reaches_right": ["row-0"], "right_not_reaches_left": ["row-1"]}]
        },
    }
    return _envelope("UNDERDETERMINED", D, r, L, provenance, policy, row_evidence_ids, None, witness)


def obstructed_certificate() -> dict:
    """The repository's own canonical four-cycle obstruction:
    D (4x4), r = (1,1,1,-2), y = (1/5,1/5,1/5,-1/5)."""
    D = [["-1", "1", "0", "0"], ["0", "-1", "1", "0"], ["0", "0", "-1", "1"], ["-1", "0", "0", "1"]]
    r = ["1", "1", "1", "-2"]
    provenance = {"vertices": ["edge-e12", "edge-e23", "edge-e34", "edge-e14"], "edges": []}
    policy = {"independent_pairs": [], "policy_version": "pce-policy/v1"}
    row_evidence_ids = {"0": "edge-e12", "1": "edge-e23", "2": "edge-e34", "3": "edge-e14"}
    witness = {
        "separator": ["1/5", "1/5", "1/5", "-1/5"],
        "admissibility_witness": {"cuts": []},
    }
    return _envelope("OBSTRUCTED", D, r, None, provenance, policy, row_evidence_ids,
                      "global coherent assignment of four regional values", witness)


def inadmissible_certificate() -> dict:
    """row-1 derived_from derived-intermediate derived_from row-0 --
    row-0 is a genuine, directly verified ancestor of row-1."""
    provenance = {
        "vertices": ["row-0", "row-1", "derived-intermediate"],
        "edges": [["row-1", "derived-intermediate"], ["derived-intermediate", "row-0"]],
    }
    policy = {"independent_pairs": [["row-0", "row-1"]], "policy_version": "pce-policy/v1"}
    row_evidence_ids = {"0": "row-0", "1": "row-1"}
    witness = {
        "rule_id": "independent_rows_no_ancestry_relation",
        "left_evidence": "row-0",
        "right_evidence": "row-1",
        "direction": "right_to_left",
        "ancestry_path": ["row-1", "derived-intermediate", "row-0"],
    }
    return _envelope("INADMISSIBLE", None, None, None, provenance, policy, row_evidence_ids, None, witness)


def exact_common_ancestor_certificate() -> dict:
    """Identical algebra to exact_certificate(), but provenance is
    a<-c->b: row-a/row-b share a common ancestor (common-c), so they
    lie in the same weakly connected component, yet neither is a
    directed ancestor of the other -- the completeness case a
    component-labelling witness could never certify, but a
    reachability-cut witness certifies correctly."""
    D = [["-1", "1", "0"], ["0", "-1", "1"]]
    r = ["3", "2"]
    L = [["-1", "0", "1"]]
    provenance = {"vertices": ["row-a", "row-b", "common-c"], "edges": [["common-c", "row-a"], ["common-c", "row-b"]]}
    policy = {"independent_pairs": [["row-a", "row-b"]], "policy_version": "pce-policy/v1"}
    row_evidence_ids = {"0": "row-a", "1": "row-b"}
    witness = {
        "repair_witness": ["-5", "-2", "0"],
        "factorisation_witness": [["1", "1"]],
        "claimed_value": ["5"],
        "admissibility_witness": {
            "cuts": [{"pair": ["row-a", "row-b"], "left_not_reaches_right": ["row-a"], "right_not_reaches_left": ["row-b"]}]
        },
    }
    return _envelope("EXACT", D, r, L, provenance, policy, row_evidence_ids, None, witness)


def to_bytes(cert: dict) -> bytes:
    return json.dumps(cert).encode("utf-8")
