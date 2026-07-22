"""
proof_carrying_exactness.canonical

Strict, byte-oriented JSON loading: the certificate verifier's public
API accepts raw bytes, not an already-parsed Python object, because
duplicate JSON keys can only be reliably rejected during parsing --
`json.loads`'s own default behaviour silently keeps the LAST value for
a repeated key, exactly the ambiguity a certificate format must not
tolerate (a certificate with a repeated field is not canonical input,
regardless of which value a lenient parser happened to keep).

Reuses `r21_certificate_format.reject_duplicate_keys` directly (the
same `object_pairs_hook`, unmodified) rather than reimplementing
duplicate-key detection -- this is JSON hygiene, not solver logic, the
same narrow, deliberate sharing that module's own docstring already
describes between R21's emitter and checker.
"""

import json
from typing import Any

from r21_certificate_format import reject_duplicate_keys

from .errors import CertificateRejected
from .limits import MAX_CERTIFICATE_BYTES, MAX_JSON_DEPTH


def _depth(obj: Any, current: int = 0) -> int:
    if current > MAX_JSON_DEPTH:
        # Bail out early rather than recursing arbitrarily deep over an
        # attacker-controlled structure -- the caller treats any depth
        # beyond the limit as a rejection regardless of the exact value
        # returned here.
        return current
    if isinstance(obj, dict):
        return max((_depth(v, current + 1) for v in obj.values()), default=current)
    if isinstance(obj, list):
        return max((_depth(v, current + 1) for v in obj), default=current)
    return current


def strict_json_loads(data: bytes) -> Any:
    """Parses `data` (raw bytes) into a Python object, fail-closed:
    rejects oversized input before decoding, malformed UTF-8, duplicate
    keys at ANY nesting level (the `object_pairs_hook` applies uniformly
    to every JSON object `json.loads` encounters, not just the top
    level), invalid JSON syntax, and excessive nesting depth."""
    if not isinstance(data, (bytes, bytearray)):
        raise CertificateRejected(f"certificate input must be bytes, got {type(data).__name__}")
    if len(data) > MAX_CERTIFICATE_BYTES:
        raise CertificateRejected(f"certificate is {len(data)} bytes, exceeding MAX_CERTIFICATE_BYTES={MAX_CERTIFICATE_BYTES}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise CertificateRejected(f"certificate is not valid UTF-8: {e}") from e
    try:
        obj = json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except ValueError as e:
        raise CertificateRejected(f"certificate is not well-formed JSON: {e}") from e
    if _depth(obj) > MAX_JSON_DEPTH:
        raise CertificateRejected(f"certificate JSON nesting exceeds MAX_JSON_DEPTH={MAX_JSON_DEPTH}")
    return obj


def canonical_dumps(obj: Any) -> str:
    """Fixed, deterministic serialisation for hashing -- sorted keys,
    compact separators -- of an already-parsed, already-validated
    Python structure. Never used on raw untrusted input directly (that
    goes through `strict_json_loads` first); this is for RE-hashing
    canonicalised, semantically meaningful values, matching the
    inherited foundation's own established digest style (e.g.
    `tracking_adapter_certificate.py`'s `_canonical_dump`)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))
