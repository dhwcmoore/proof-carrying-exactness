"""
proof_carrying_exactness_generator fail-closed contract: no matter how
a certificate is assembled internally, `generate_certificate` only ever
returns bytes the production verifier has independently accepted.
These tests monkeypatch the certificate_builder step to inject a
corrupted witness and confirm the corrupted bytes are never released.
"""

import pytest

import proof_carrying_exactness_generator.generator as generator_module
from proof_carrying_exactness_generator import CertificateGenerationFailed

from generator_fixtures import ALL_INSTANCES


def test_corrupted_exact_witness_is_never_released(monkeypatch):
    real_build_exact = generator_module.build_exact

    def corrupting_build_exact(D, r, L, provenance, policy, row_evidence_ids, u, M, x):
        cert = real_build_exact(D, r, L, provenance, policy, row_evidence_ids, u, M, x)
        cert["witness"]["claimed_value"] = [str(int(v) + 999) for v in cert["witness"]["claimed_value"]]
        return cert

    monkeypatch.setattr(generator_module, "build_exact", corrupting_build_exact)

    with pytest.raises(CertificateGenerationFailed):
        generator_module.generate_certificate(ALL_INSTANCES["EXACT"])


def test_corrupted_obstructed_separator_is_never_released(monkeypatch):
    real_build_obstructed = generator_module.build_obstructed

    def corrupting_build_obstructed(D, r, provenance, policy, row_evidence_ids, claim_metadata, y):
        cert = real_build_obstructed(D, r, provenance, policy, row_evidence_ids, claim_metadata, y)
        cert["witness"]["separator"] = ["0" for _ in cert["witness"]["separator"]]  # y^T r == 0
        return cert

    monkeypatch.setattr(generator_module, "build_obstructed", corrupting_build_obstructed)

    with pytest.raises(CertificateGenerationFailed):
        generator_module.generate_certificate(ALL_INSTANCES["OBSTRUCTED"])


def test_tampered_input_digest_after_serialisation_is_never_released(monkeypatch):
    real_serialise = generator_module.serialise_certificate

    def corrupting_serialise(cert):
        cert = dict(cert)
        cert["input_digest"] = "sha256:" + "0" * 64
        return real_serialise(cert)

    monkeypatch.setattr(generator_module, "serialise_certificate", corrupting_serialise)

    with pytest.raises(CertificateGenerationFailed):
        generator_module.generate_certificate(ALL_INSTANCES["EXACT"])
