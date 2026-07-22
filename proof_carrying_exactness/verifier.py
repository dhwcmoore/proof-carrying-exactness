"""
proof_carrying_exactness.verifier

THE production certificate verifier. Contract:

    untrusted certificate bytes
            |
            v
    strict parser (canonical.strict_json_loads)
            |
            v
    closed verdict-specific schema (schemas.py)
            |
            v
    digest recomputation (digests.py)
            |
            v
    local exact witness checks (matrix.py, provenance.py)
            |
            v
    ACCEPT or REJECT

This module -- together with `rational.py`, `matrix.py`,
`provenance.py`, `canonical.py`, `digests.py`, `schemas.py`,
`limits.py`, `errors.py` -- is the ENTIRE verifier package. It imports
NO discovery/search machinery: no `r21_repair_or_separator`, no
`rational_linear_algebra.{nullspace_over_Q, solve_over_Q}`, no
certificate generator, no graph-search library. `tests/test_pce_
import_boundary.py` checks this mechanically (AST scan), not merely by
docstring claim, the same discipline this repository's own inherited
`tests/test_stonesoup_import_boundary.py` already establishes.

There is no generator, solver, or CLI in this package. A certificate
must already exist; this package only ever CHECKS one.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

from .canonical import strict_json_loads
from .digests import compute_input_digest, compute_policy_digest
from .errors import CertificateRejected
from .matrix import dot, is_zero, mat_mat, mat_vec, parse_matrix, parse_vector, row_vec_mat
from .provenance import verify_admissibility_cuts, verify_inadmissible_path
from .schemas import (
    ENVELOPE_KEYS,
    ENVELOPE_SCHEMA,
    INSTANCE_KEYS,
    INSTANCE_REQUIRED_KEYS,
    POLICY_KEYS,
    PROVENANCE_KEYS,
    VERDICT_EXACT,
    VERDICT_INADMISSIBLE,
    VERDICT_OBSTRUCTED,
    VERDICT_UNDERDETERMINED,
    VERDICTS,
    WITNESS_KEYS,
    WITNESS_REQUIRED_KEYS,
)


@dataclass(frozen=True)
class VerificationResult:
    accepted: bool
    verdict: Optional[str]
    reason: str


def _require_closed(obj, allowed: frozenset, required: frozenset, label: str) -> None:
    if not isinstance(obj, dict):
        raise CertificateRejected(f"{label} is not a JSON object: {obj!r}")
    extra = set(obj.keys()) - allowed
    if extra:
        raise CertificateRejected(f"{label} has unrecognized field(s): {sorted(extra)}")
    missing = required - set(obj.keys())
    if missing:
        raise CertificateRejected(f"{label} missing required field(s): {sorted(missing)}")


def _verify_parsed(cert) -> str:
    """Returns the accepted verdict string, or raises CertificateRejected."""
    if not isinstance(cert, dict):
        raise CertificateRejected(f"certificate is not a JSON object: {cert!r}")
    _require_closed(cert, ENVELOPE_KEYS, ENVELOPE_KEYS, "certificate envelope")

    if cert["schema"] != ENVELOPE_SCHEMA:
        raise CertificateRejected(f"unrecognized schema: {cert['schema']!r}")
    verdict = cert["verdict"]
    if verdict not in VERDICTS:
        raise CertificateRejected(f"unrecognized verdict: {verdict!r}")

    instance = cert["instance"]
    _require_closed(instance, INSTANCE_KEYS[verdict], INSTANCE_REQUIRED_KEYS[verdict], f"{verdict} instance")

    witness = cert["witness"]
    _require_closed(witness, WITNESS_KEYS[verdict], WITNESS_REQUIRED_KEYS[verdict], f"{verdict} witness")

    D = parse_matrix(instance["D"]) if "D" in instance else None
    r = parse_vector(instance["r"]) if "r" in instance else None
    L = parse_matrix(instance["L"]) if instance.get("L") is not None else None
    if D is not None and r is not None and len(r) != len(D):
        raise CertificateRejected(f"D has {len(D)} rows but r has length {len(r)}")

    provenance = instance.get("provenance") or {}
    _require_closed(provenance, PROVENANCE_KEYS, PROVENANCE_KEYS, "provenance")

    policy = instance.get("policy") or {}
    _require_closed(policy, POLICY_KEYS, POLICY_KEYS, "policy")

    row_evidence_ids = instance.get("row_evidence_ids") or {}
    claim_metadata = instance.get("claim_metadata")

    expected_input_digest = compute_input_digest(D, r, L, provenance, row_evidence_ids, claim_metadata)
    if cert["input_digest"] != expected_input_digest:
        raise CertificateRejected(
            f"input_digest mismatch: certificate declares {cert['input_digest']!r}, "
            f"recomputed {expected_input_digest!r}"
        )
    expected_policy_digest = compute_policy_digest(policy)
    if cert["policy_digest"] != expected_policy_digest:
        raise CertificateRejected(
            f"policy_digest mismatch: certificate declares {cert['policy_digest']!r}, "
            f"recomputed {expected_policy_digest!r}"
        )

    if verdict == VERDICT_EXACT:
        _verify_exact(provenance, policy, D, r, L, witness)
    elif verdict == VERDICT_UNDERDETERMINED:
        _verify_underdetermined(provenance, policy, D, r, L, witness)
    elif verdict == VERDICT_OBSTRUCTED:
        _verify_obstructed(provenance, policy, D, r, witness)
    elif verdict == VERDICT_INADMISSIBLE:
        verify_inadmissible_path(provenance, policy, witness)

    return verdict


def _verify_exact(provenance, policy, D, r, L, witness: dict) -> None:
    u = parse_vector(witness["repair_witness"])
    M = parse_matrix(witness["factorisation_witness"])
    x = parse_vector(witness["claimed_value"])

    verify_admissibility_cuts(provenance, policy, witness["admissibility_witness"])

    if mat_vec(D, u) != r:
        raise CertificateRejected("D @ u != r")
    if mat_mat(M, D) != L:
        raise CertificateRejected("M @ D != L -- the claim map does not factor through D as claimed")
    # Normative: x = M r, computed directly from the residue (SS6).
    if mat_vec(M, r) != x:
        raise CertificateRejected("M @ r != claimed_value -- the claim map's value does not follow from the residue alone")
    # Permitted, redundant consistency check.
    if mat_vec(L, u) != x:
        raise CertificateRejected("L @ u != claimed_value (redundant consistency check)")


def _verify_underdetermined(provenance, policy, D, r, L, witness: dict) -> None:
    u = parse_vector(witness["repair_witness"])
    k = parse_vector(witness["gauge_witness"])

    verify_admissibility_cuts(provenance, policy, witness["admissibility_witness"])

    if mat_vec(D, u) != r:
        raise CertificateRejected("D @ u != r")
    if not is_zero(mat_vec(D, k)):
        raise CertificateRejected("D @ k != 0 -- k is not a gauge direction of D")
    if is_zero(mat_vec(L, k)):
        raise CertificateRejected("L @ k == 0 -- k does not change the claim, so this is not underdetermination")
    # Derived, not certified: confirms the alternate repair exists and
    # differs, matching the human-facing diagnostic, never a required
    # certificate field.
    u_prime = [u[i] + k[i] for i in range(len(u))]
    assert mat_vec(D, u_prime) == r
    assert mat_vec(L, u_prime) != mat_vec(L, u)


def _verify_obstructed(provenance, policy, D, r, witness: dict) -> None:
    y = parse_vector(witness["separator"])

    verify_admissibility_cuts(provenance, policy, witness["admissibility_witness"])

    if len(y) != len(D):
        raise CertificateRejected(f"separator length {len(y)} does not match D's row count {len(D)}")
    if not is_zero(row_vec_mat(y, D)):
        raise CertificateRejected("y^T @ D != 0")
    if dot(y, r) == 0:
        raise CertificateRejected("y^T @ r == 0 -- not a genuine obstruction")


def verify_certificate_bytes(data: bytes) -> VerificationResult:
    """The single public entry point. Never raises: any anticipated
    validation failure (CertificateRejected) becomes a REJECT with its
    specific reason; any genuinely unanticipated exception becomes a
    REJECT with a generic internal-failure reason, never leaked to the
    caller as a crash."""
    try:
        cert = strict_json_loads(data)
        verdict = _verify_parsed(cert)
        return VerificationResult(accepted=True, verdict=verdict, reason="ACCEPT")
    except CertificateRejected as e:
        return VerificationResult(accepted=False, verdict=None, reason=str(e))
    except Exception:
        return VerificationResult(accepted=False, verdict=None, reason="internal verification failure")
