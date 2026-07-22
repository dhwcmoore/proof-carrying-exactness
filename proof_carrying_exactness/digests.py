"""
proof_carrying_exactness.digests

Domain-separated digest computation, per
docs/design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md SS4.

`input_digest` binds the evidence instance -- both algebraic (D, r, L)
and evidentiary (provenance vertices/edges, evidence-to-row alignment,
claim metadata). `policy_digest` binds ONLY the judgement rules (rule
identifiers, independent-pair declarations, policy version, rule
parameters) -- reusable across many evidence packages. Provenance is
deliberately NOT part of `policy_digest`: it is a fact about the
evidence, not a judgement rule.

Both digests are computed by REBUILDING canonical structures from
ALREADY-PARSED values (exact `Fraction`s, already-validated dicts), not
by hashing the caller's original JSON substring -- insignificant JSON
formatting (key order, whitespace) must never change the digest.

Both prepend an explicit domain-separation tag before hashing, so the
same canonical bytes can never be confused across the two digest
domains.
"""

import hashlib
from fractions import Fraction
from typing import Dict, List, Optional

from r21_certificate_format import canonical_input_digest

from .canonical import canonical_dumps

INPUT_DIGEST_DOMAIN = "pce-input-v1"
POLICY_DIGEST_DOMAIN = "pce-policy-v1"


def _canonical_matrix_lines(label: str, M: Optional[List[List[Fraction]]]) -> List[str]:
    if M is None:
        return [f"{label}:none"]
    m = len(M)
    n = len(M[0]) if M else 0
    lines = [f"{label}:{m}x{n}"]
    lines.extend(",".join(str(x) for x in row) for row in M)
    return lines


def _canonical_provenance_lines(provenance: Optional[dict]) -> List[str]:
    provenance = provenance or {"vertices": [], "edges": []}
    vertices = sorted(provenance.get("vertices", []))
    edges = sorted((str(a), str(b)) for a, b in provenance.get("edges", []))
    lines = [f"provenance:vertices:{len(vertices)}"]
    lines.extend(vertices)
    lines.append(f"provenance:edges:{len(edges)}")
    lines.extend(f"{a}->{b}" for a, b in edges)
    return lines


def _canonical_row_evidence_lines(row_evidence_ids: Optional[dict]) -> List[str]:
    row_evidence_ids = row_evidence_ids or {}
    items = sorted(row_evidence_ids.items(), key=lambda kv: kv[0])
    return [f"row_evidence_ids:{len(items)}"] + [f"{k}={v}" for k, v in items]


def compute_input_digest(
    D: Optional[List[List[Fraction]]],
    r: Optional[List[Fraction]],
    L: Optional[List[List[Fraction]]],
    provenance: Optional[dict],
    row_evidence_ids: Optional[dict],
    claim_metadata: Optional[str],
) -> str:
    lines = [canonical_input_digest(D, r)] if (D is not None and r is not None) else ["D:absent", "r:absent"]
    lines.extend(_canonical_matrix_lines("L", L))
    lines.extend(_canonical_provenance_lines(provenance))
    lines.extend(_canonical_row_evidence_lines(row_evidence_ids))
    lines.append(f"claim_metadata:{claim_metadata}" if claim_metadata is not None else "claim_metadata:none")
    canonical = "\n".join(lines)
    domain_separated = f"{INPUT_DIGEST_DOMAIN}||{canonical}"
    return "sha256:" + hashlib.sha256(domain_separated.encode("utf-8")).hexdigest()


def compute_policy_digest(policy: Dict) -> str:
    canonical = canonical_dumps(policy or {})
    domain_separated = f"{POLICY_DIGEST_DOMAIN}||{canonical}"
    return "sha256:" + hashlib.sha256(domain_separated.encode("utf-8")).hexdigest()
