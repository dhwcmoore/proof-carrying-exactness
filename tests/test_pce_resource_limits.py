"""
Resource-limit tests (SPEC SS16). Traceability: docs/PCE_VERIFIER_TRACEABILITY.md.
"""

import pytest

from proof_carrying_exactness import verify_certificate_bytes
from proof_carrying_exactness.errors import CertificateRejected
from proof_carrying_exactness.limits import (
    MAX_CERTIFICATE_BYTES,
    MAX_JSON_DEPTH,
    MAX_MATRIX_COLS,
    MAX_MATRIX_ROWS,
    MAX_PROVENANCE_PATH_LENGTH,
    MAX_RATIONAL_CHARS,
    MAX_VECTOR_LENGTH,
)

from pce_fixtures import inadmissible_certificate, to_bytes


def test_oversized_certificate_rejected_before_parsing():
    from proof_carrying_exactness.canonical import strict_json_loads

    oversized = b"{" + b" " * (MAX_CERTIFICATE_BYTES + 1) + b"}"
    with pytest.raises(CertificateRejected):
        strict_json_loads(oversized)


def test_oversized_certificate_via_public_api_fails_closed():
    oversized = b"{" + b" " * (MAX_CERTIFICATE_BYTES + 1) + b"}"
    result = verify_certificate_bytes(oversized)
    assert not result.accepted


def test_excessive_json_nesting_rejected():
    from proof_carrying_exactness.canonical import strict_json_loads

    nested = b"[" * (MAX_JSON_DEPTH + 5) + b"]" * (MAX_JSON_DEPTH + 5)
    with pytest.raises(CertificateRejected):
        strict_json_loads(nested)


def test_oversized_rational_string_rejected():
    from proof_carrying_exactness.rational import parse_rational

    huge = "1" * (MAX_RATIONAL_CHARS + 1)
    with pytest.raises(CertificateRejected):
        parse_rational(huge)


def test_oversized_vector_rejected():
    from proof_carrying_exactness.matrix import parse_vector

    with pytest.raises(CertificateRejected):
        parse_vector(["1"] * (MAX_VECTOR_LENGTH + 1))


def test_oversized_matrix_rows_rejected():
    from proof_carrying_exactness.matrix import parse_matrix

    with pytest.raises(CertificateRejected):
        parse_matrix([["1"]] * (MAX_MATRIX_ROWS + 1))


def test_oversized_matrix_cols_rejected():
    from proof_carrying_exactness.matrix import parse_matrix

    with pytest.raises(CertificateRejected):
        parse_matrix([["1"] * (MAX_MATRIX_COLS + 1)])


def test_oversized_ancestry_path_rejected():
    cert = inadmissible_certificate()
    # A path longer than MAX_PROVENANCE_PATH_LENGTH -- built from
    # distinct vertex names so it does not also trip the simple-path
    # (no repeated vertex) check, isolating the length limit itself.
    long_path = [f"v{i}" for i in range(MAX_PROVENANCE_PATH_LENGTH + 5)]
    cert["instance"]["provenance"]["vertices"].extend(long_path)
    cert["witness"]["ancestry_path"] = long_path
    result = verify_certificate_bytes(to_bytes(cert))
    assert not result.accepted


def test_non_bytes_input_is_an_anticipated_rejection_not_a_crash():
    result = verify_certificate_bytes(None)  # type: ignore[arg-type]
    assert not result.accepted
    assert result.verdict is None
    assert "bytes" in result.reason


def test_unexpected_internal_error_reported_generically_not_leaked(monkeypatch):
    # Confirms the outer boundary distinguishes anticipated rejections
    # (CertificateRejected, specific reasons, tested throughout this
    # suite) from genuinely unexpected exceptions, which must never
    # crash the caller and must never leak an internal traceback as the
    # reason string.
    import proof_carrying_exactness.verifier as verifier_module

    def _boom(_cert):
        raise RuntimeError("a genuine internal bug, not a certificate defect")

    monkeypatch.setattr(verifier_module, "_verify_parsed", _boom)
    result = verify_certificate_bytes(to_bytes(inadmissible_certificate()))
    assert not result.accepted
    assert result.verdict is None
    assert result.reason == "internal verification failure"
