"""
proof_carrying_exactness.matrix

Vector/matrix parsing and PURE (non-solving) exact-rational linear
algebra, reused directly from the inherited foundation. This module,
together with `rational.py`, is the ENTIRE algebraic surface the
production verifier is allowed to touch -- confirmed mechanically by
`tests/test_pce_import_boundary.py`, which asserts the verifier package
never imports `r21_repair_or_separator` or `rational_linear_algebra.
{nullspace_over_Q, solve_over_Q}` (all three perform Gauss-Jordan
elimination -- discovery, not verification).

`mat_vec`, `mat_mat`, `row_vec_mat`, `dot`, and `is_zero` are direct
evaluations of an already-fully-specified product -- never an
elimination, search, or "find x such that" operation -- so reusing them
here does not weaken the discovery/verification boundary this package
exists to enforce.
"""

from fractions import Fraction
from typing import List

from rational_linear_algebra import dot, is_zero, mat_mat, mat_vec, row_vec_mat

from .errors import CertificateRejected
from .limits import MAX_MATRIX_COLS, MAX_MATRIX_ROWS, MAX_VECTOR_LENGTH
from .rational import parse_rational


def parse_vector(xs) -> List[Fraction]:
    if not isinstance(xs, list):
        raise CertificateRejected(f"expected a list of rationals, got {type(xs).__name__}")
    if len(xs) > MAX_VECTOR_LENGTH:
        raise CertificateRejected(f"vector length {len(xs)} exceeds MAX_VECTOR_LENGTH={MAX_VECTOR_LENGTH}")
    return [parse_rational(x) for x in xs]


def parse_matrix(rows) -> List[List[Fraction]]:
    if not isinstance(rows, list):
        raise CertificateRejected(f"expected a matrix (list of rows), got {type(rows).__name__}")
    if len(rows) > MAX_MATRIX_ROWS:
        raise CertificateRejected(f"matrix row count {len(rows)} exceeds MAX_MATRIX_ROWS={MAX_MATRIX_ROWS}")
    parsed = [parse_vector(row) for row in rows]
    if parsed:
        n = len(parsed[0])
        if any(len(row) != n for row in parsed):
            raise CertificateRejected("matrix is not rectangular: rows have differing lengths")
        if n > MAX_MATRIX_COLS:
            raise CertificateRejected(f"matrix column count {n} exceeds MAX_MATRIX_COLS={MAX_MATRIX_COLS}")
    return parsed


__all__ = ["parse_vector", "parse_matrix", "mat_vec", "mat_mat", "row_vec_mat", "dot", "is_zero"]
