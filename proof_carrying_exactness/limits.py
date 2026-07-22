"""
proof_carrying_exactness.limits

Named resource-limit constants for the production certificate
verifier, independent of mathematical soundness -- the same discipline
`r21_certificate_format.py`'s own `MAX_DIMENSION`/`MAX_TOTAL_ENTRIES`/
`MAX_RATIONAL_CHARS`/`MAX_INPUT_BYTES` already establish (a bug here
could at most cause a spurious REJECT of a well-formed certificate,
never a false ACCEPT of an unsound one). Every limit below is checked
BEFORE the corresponding structure is used for any large allocation or
arithmetic.

Conservative to start; raise later only with concrete evidence a limit
is too tight for a genuine use case, not speculatively.
"""

MAX_CERTIFICATE_BYTES = 1_000_000
MAX_RATIONAL_CHARS = 1_000
MAX_MATRIX_ROWS = 1_000
MAX_MATRIX_COLS = 1_000
MAX_VECTOR_LENGTH = 1_000
MAX_EVIDENCE_ITEMS = 1_000
MAX_PROVENANCE_VERTICES = 1_000
MAX_PROVENANCE_EDGES = 5_000
MAX_PROVENANCE_PATH_LENGTH = 1_000
MAX_INDEPENDENT_PAIRS = 1_000
MAX_JSON_DEPTH = 20
