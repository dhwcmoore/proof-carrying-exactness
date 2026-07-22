"""
proof_carrying_exactness_generator.certificate_builder

Assembles the parsed-Python-dict form of a certificate for each of the
four verdicts, and serialises an already-built certificate to
canonical bytes. Reuses `proof_carrying_exactness.schemas` (the closed
key sets and verdict/schema constants) and `proof_carrying_exactness.
digests` (the same digest functions the production verifier
recomputes) directly -- schema and digest definitions are shared
between generator and verifier by design, the same narrow sharing
`r21_certificate_format` already establishes between R21's own emitter
and checker; this is canonicalisation, not solver logic, so sharing it
does not weaken the discovery/verification boundary.

Every builder here takes already-discovered witnesses (a repair, a
separator, a gauge direction, a factorisation, an ancestry path) as
arguments -- discovery itself lives in `admissibility.py` and
`factorisation.py`, orchestrated by `generator.py`.
"""

from fractions import Fraction
from typing import List, Optional

from proof_carrying_exactness.canonical import canonical_dumps
from proof_carrying_exactness.digests import compute_input_digest, compute_policy_digest
from proof_carrying_exactness.schemas import (
    ENVELOPE_SCHEMA,
    VERDICT_EXACT,
    VERDICT_INADMISSIBLE,
    VERDICT_OBSTRUCTED,
    VERDICT_UNDERDETERMINED,
)

from .admissibility import build_admissibility_witness


def str_mat(M: Optional[List[List[Fraction]]]):
    if M is None:
        return None
    return [[str(x) for x in row] for row in M]


def str_vec(v: List[Fraction]) -> List[str]:
    return [str(x) for x in v]


def build_envelope(verdict: str, D, r, L, provenance: dict, policy: dict, row_evidence_ids: dict,
                    claim_metadata: Optional[str], witness: dict) -> dict:
    instance = {"provenance": provenance, "policy": policy, "row_evidence_ids": row_evidence_ids}
    if D is not None:
        instance["D"] = str_mat(D)
        instance["r"] = str_vec(r)
    if L is not None:
        instance["L"] = str_mat(L)
    if claim_metadata is not None:
        instance["claim_metadata"] = claim_metadata

    return {
        "schema": ENVELOPE_SCHEMA,
        "verdict": verdict,
        "input_digest": compute_input_digest(D, r, L, provenance, row_evidence_ids, claim_metadata),
        "policy_digest": compute_policy_digest(policy),
        "instance": instance,
        "witness": witness,
    }


def build_exact(D, r, L, provenance: dict, policy: dict, row_evidence_ids: dict,
                 u: List[Fraction], M: List[List[Fraction]], x: List[Fraction]) -> dict:
    witness = {
        "repair_witness": str_vec(u),
        "factorisation_witness": str_mat(M),
        "claimed_value": str_vec(x),
        "admissibility_witness": build_admissibility_witness(provenance, policy),
    }
    return build_envelope(VERDICT_EXACT, D, r, L, provenance, policy, row_evidence_ids, None, witness)


def build_underdetermined(D, r, L, provenance: dict, policy: dict, row_evidence_ids: dict,
                           u: List[Fraction], gauge_k: List[Fraction]) -> dict:
    witness = {
        "repair_witness": str_vec(u),
        "gauge_witness": str_vec(gauge_k),
        "admissibility_witness": build_admissibility_witness(provenance, policy),
    }
    return build_envelope(VERDICT_UNDERDETERMINED, D, r, L, provenance, policy, row_evidence_ids, None, witness)


def build_obstructed(D, r, provenance: dict, policy: dict, row_evidence_ids: dict,
                      claim_metadata: Optional[str], y: List[Fraction]) -> dict:
    witness = {
        "separator": str_vec(y),
        "admissibility_witness": build_admissibility_witness(provenance, policy),
    }
    return build_envelope(VERDICT_OBSTRUCTED, D, r, None, provenance, policy, row_evidence_ids, claim_metadata, witness)


def build_inadmissible(provenance: dict, policy: dict, row_evidence_ids: dict,
                        left: str, right: str, direction: str, path: List[str]) -> dict:
    witness = {
        "rule_id": "independent_rows_no_ancestry_relation",
        "left_evidence": left,
        "right_evidence": right,
        "direction": direction,
        "ancestry_path": path,
    }
    return build_envelope(VERDICT_INADMISSIBLE, None, None, None, provenance, policy, row_evidence_ids, None, witness)


def serialise_certificate(cert: dict) -> bytes:
    """Deterministic byte encoding of an already-built certificate:
    sorted keys, compact separators, UTF-8 -- the same canonical form
    `proof_carrying_exactness.canonical.canonical_dumps` already uses
    for re-hashing, reused here so two calls over the same instance
    always produce identical bytes."""
    return canonical_dumps(cert).encode("utf-8")
