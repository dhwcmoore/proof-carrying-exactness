"""
proof_carrying_exactness.rational

Exact rational parsing, reused directly from the inherited R21
certificate format rather than reimplemented: canonical reduced form,
positive denominators, no decimal notation, no floating point, ASCII-
digit-only grammar. Wrapped here (not imported directly by `verifier.
py`) so this package owns its own import surface and the inherited
module is never modified for this project's convenience.
"""

from fractions import Fraction

from r21_certificate_format import parse_rational as _parse_rational

from .errors import CertificateRejected
from .limits import MAX_RATIONAL_CHARS


def parse_rational(value) -> Fraction:
    """Strict canonical exact-rational parser -- delegates to the
    inherited, already-audited `r21_certificate_format.parse_rational`,
    converting its `ValueError` into this package's own `Certificate
    Rejected` so every rejection reason in this package has one
    consistent exception type at the verifier boundary."""
    try:
        return _parse_rational(value)
    except ValueError as e:
        raise CertificateRejected(f"malformed rational value: {e}") from e


__all__ = ["parse_rational", "MAX_RATIONAL_CHARS"]
