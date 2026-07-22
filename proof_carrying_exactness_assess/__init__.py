"""
proof_carrying_exactness_assess

The generic, region-agnostic end-to-end assessment boundary:

    from proof_carrying_exactness_assess import assess_instance
    result = assess_instance(instance_json_bytes)
    result.accepted, result.verdict, result.certificate_bytes, result.summary, result.reason

`assess_instance` never releases a verdict or certificate the
production verifier (`proof_carrying_exactness.verify_certificate_
bytes`) has not independently accepted -- see `assess.py`'s own
docstring for the full pipeline and trust boundary. `cli.py` (launched
via the root-level `pce_assess.py` script) is a thin, untrusted
coordinator around this same function; it computes nothing of its own.

No region-specific semantics live here -- this package only implements
the generic affine-rational instance -> certificate -> verdict pipeline
already covered by the certificate specification.
"""

from .assess import AssessmentResult, assess_instance

__all__ = ["AssessmentResult", "assess_instance"]
