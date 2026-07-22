"""
proof_carrying_exactness_generator

An untrusted, four-verdict certificate GENERATOR for the affine
rational class covered by docs/design/PROOF_CARRYING_EXACTNESS_
CERTIFICATE_SPEC.md, deliberately packaged separately from `proof_
carrying_exactness/` (the production verifier):

    from proof_carrying_exactness_generator import generate_certificate
    certificate_bytes = generate_certificate(instance)

`generate_certificate` never returns a certificate the production
verifier has not independently accepted -- see `generator.py`'s own
docstring for the full control flow and the fail-closed contract.
"""

from .generator import CertificateGenerationFailed, generate_certificate

__all__ = ["CertificateGenerationFailed", "generate_certificate"]
