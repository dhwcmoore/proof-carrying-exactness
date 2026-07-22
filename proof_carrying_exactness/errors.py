"""
proof_carrying_exactness.errors

`CertificateRejected` is raised for every ANTICIPATED validation
failure -- a malformed field, a failed equation, an unknown key, a
resource limit exceeded -- and caught at the single public boundary
(`verifier.verify_certificate_bytes`), which converts it into a
`VerificationResult(accepted=False, reason=str(e))`. It is never raised
for a genuine internal bug; an unanticipated exception of any other
type is caught separately and reported as a generic internal failure,
never leaked to the caller and never confused with a specific,
informative rejection reason.
"""


class CertificateRejected(Exception):
    """An anticipated certificate-verification failure, with a specific,
    caller-facing reason. Not a bug -- this is the normal way `verify_
    certificate_bytes` reports REJECT with a reason attached."""
