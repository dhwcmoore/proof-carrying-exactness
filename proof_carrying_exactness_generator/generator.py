"""
proof_carrying_exactness_generator.generator

THE untrusted, four-verdict certificate generator for the affine
rational class already covered by docs/design/PROOF_CARRYING_
EXACTNESS_CERTIFICATE_SPEC.md. "Untrusted" is load-bearing, not a
hedge, the same discipline `r21_repair_or_separator.py`'s own
docstring establishes for its solver: a bug here is a bug in this
package only, because `generate_certificate` never returns a
certificate the production verifier (`proof_carrying_exactness.
verify_certificate_bytes`) has not independently accepted first.

Control flow:

    parse instance
        -> find INADMISSIBLE witness if policy fails
        -> otherwise solve or separate D u = r
        -> if separated, emit OBSTRUCTED
        -> if repaired, test whether L changes along ker(D)
            -> if yes, emit UNDERDETERMINED
            -> otherwise construct M with M D = L and emit EXACT
        -> call verify_certificate_bytes
        -> release only if verifier returns ACCEPT

This module (together with `admissibility.py`, `factorisation.py`,
`certificate_builder.py`) is free to import solvers, nullspace
computation, graph search, and factorisation routines -- exactly the
discovery machinery `proof_carrying_exactness/` (the verifier package)
is forbidden from importing. The import boundary is symmetric: the
verifier must never import this package either, checked mechanically
by `tests/test_generator_import_boundary.py`.
"""

from fractions import Fraction
from typing import List, Mapping, Optional

from r21_repair_or_separator import RESULT_SEPARATOR, repair_or_separate
from rational_linear_algebra import mat_vec, nullspace_over_Q

from proof_carrying_exactness import verify_certificate_bytes

from .admissibility import find_ancestry_path
from .certificate_builder import (
    build_exact,
    build_inadmissible,
    build_obstructed,
    build_underdetermined,
    serialise_certificate,
)
from .factorisation import find_factorisation


class CertificateGenerationFailed(Exception):
    """Raised whenever this generator cannot produce a certificate the
    production verifier accepts -- either because the instance is
    malformed, a discovery step failed, or (fail-closed) the assembled
    certificate was itself rejected by `verify_certificate_bytes`. No
    certificate bytes are ever returned in this case."""


def _frac(x) -> Fraction:
    return Fraction(x)


def _mat(rows) -> Optional[List[List[Fraction]]]:
    if rows is None:
        return None
    return [[_frac(x) for x in row] for row in rows]


def _vec(xs) -> Optional[List[Fraction]]:
    if xs is None:
        return None
    return [_frac(x) for x in xs]


def _parse_instance(instance: Mapping[str, object]):
    D = _mat(instance.get("D"))
    r = _vec(instance.get("r"))
    L = _mat(instance.get("L"))
    claim_metadata = instance.get("claim_metadata")
    provenance = instance.get("provenance") or {"vertices": [], "edges": []}
    policy = instance.get("policy") or {"independent_pairs": [], "policy_version": "pce-policy/v1"}
    row_evidence_ids = instance.get("row_evidence_ids") or {}
    return D, r, L, claim_metadata, provenance, policy, row_evidence_ids


def _find_inadmissible(provenance: dict, policy: dict, row_evidence_ids: dict) -> Optional[dict]:
    """Checked BEFORE the algebraic branch: admissibility is a
    precondition on the evidence, not a consequence of the algebra."""
    for left, right in policy.get("independent_pairs", []):
        direction, path = find_ancestry_path(provenance.get("edges", []), left, right)
        if path is not None:
            return build_inadmissible(provenance, policy, row_evidence_ids, left, right, direction, path)
    return None


def generate_certificate(instance: Mapping[str, object]) -> bytes:
    """Generate a certificate and release it only after production
    verification.

    Raises `CertificateGenerationFailed` -- and returns no bytes at all
    -- if the instance is malformed, no witness can be discovered, or
    the assembled certificate fails independent verification.
    """
    D, r, L, claim_metadata, provenance, policy, row_evidence_ids = _parse_instance(instance)

    cert = _find_inadmissible(provenance, policy, row_evidence_ids)

    if cert is None:
        if D is None or r is None:
            raise CertificateGenerationFailed(
                "instance declares no admissibility violation and supplies no algebraic system (D, r)"
            )
        result = repair_or_separate(D, r)
        if result.result == RESULT_SEPARATOR:
            cert = build_obstructed(D, r, provenance, policy, row_evidence_ids, claim_metadata, result.separator)
        else:
            if L is None:
                raise CertificateGenerationFailed("residue is repairable but no claim map L was supplied")
            u = result.repair
            kernel_basis = nullspace_over_Q(D)
            gauge_k = next((k for k in kernel_basis if any(v != 0 for v in mat_vec(L, k))), None)
            if gauge_k is not None:
                cert = build_underdetermined(D, r, L, provenance, policy, row_evidence_ids, u, gauge_k)
            else:
                factorisable, M = find_factorisation(D, L)
                if not factorisable:
                    raise CertificateGenerationFailed("claim map L does not factor through D (M D = L unsolvable)")
                x = mat_vec(L, u)
                cert = build_exact(D, r, L, provenance, policy, row_evidence_ids, u, M, x)

    data = serialise_certificate(cert)
    result = verify_certificate_bytes(data)
    if not result.accepted:
        raise CertificateGenerationFailed(
            f"generated certificate was rejected by the production verifier: {result.reason}"
        )
    return data
