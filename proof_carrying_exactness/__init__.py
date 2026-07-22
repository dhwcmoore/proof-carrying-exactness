"""
proof_carrying_exactness

A pure certificate verifier for the four proof-carrying-exactness
verdicts (EXACT, UNDERDETERMINED, OBSTRUCTED, INADMISSIBLE), per
docs/design/PROOF_CARRYING_EXACTNESS_SPEC.md and docs/design/
PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md.

    from proof_carrying_exactness import verify_certificate_bytes
    result = verify_certificate_bytes(certificate_json_bytes)
    result.accepted, result.verdict, result.reason

No generator, solver, or command-line assessment pipeline exists in
this package -- it only ever CHECKS an already-produced certificate.
See `verifier.py`'s own docstring for the exact contract and the
import boundary this package enforces.
"""

from .verifier import VerificationResult, verify_certificate_bytes

__all__ = ["VerificationResult", "verify_certificate_bytes"]
