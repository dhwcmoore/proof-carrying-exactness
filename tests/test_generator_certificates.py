"""
proof_carrying_exactness_generator milestone tests: one valid
production certificate per verdict, generator-to-verifier round trips,
deterministic certificate bytes, and tamper rejection after
generation.
"""

import json

import pytest

from proof_carrying_exactness import verify_certificate_bytes
from proof_carrying_exactness_generator import generate_certificate

from generator_fixtures import ALL_INSTANCES


@pytest.mark.parametrize("verdict", sorted(ALL_INSTANCES))
def test_generates_a_certificate_the_production_verifier_accepts(verdict):
    data = generate_certificate(ALL_INSTANCES[verdict])
    result = verify_certificate_bytes(data)
    assert result.accepted, result.reason
    assert result.verdict == verdict


@pytest.mark.parametrize("verdict", sorted(ALL_INSTANCES))
def test_certificate_bytes_are_deterministic(verdict):
    data1 = generate_certificate(ALL_INSTANCES[verdict])
    data2 = generate_certificate(ALL_INSTANCES[verdict])
    assert data1 == data2


@pytest.mark.parametrize("verdict", sorted(ALL_INSTANCES))
def test_tampering_after_generation_is_rejected(verdict):
    data = generate_certificate(ALL_INSTANCES[verdict])
    cert = json.loads(data)
    cert["input_digest"] = "sha256:" + "0" * 64
    tampered = json.dumps(cert).encode("utf-8")
    result = verify_certificate_bytes(tampered)
    assert not result.accepted


def test_exact_witness_shape():
    data = generate_certificate(ALL_INSTANCES["EXACT"])
    cert = json.loads(data)
    witness = cert["witness"]
    assert set(witness) == {
        "repair_witness", "factorisation_witness", "claimed_value", "admissibility_witness",
    }


def test_underdetermined_witness_shape():
    data = generate_certificate(ALL_INSTANCES["UNDERDETERMINED"])
    cert = json.loads(data)
    witness = cert["witness"]
    assert set(witness) == {"repair_witness", "gauge_witness", "admissibility_witness"}


def test_obstructed_witness_shape():
    data = generate_certificate(ALL_INSTANCES["OBSTRUCTED"])
    cert = json.loads(data)
    witness = cert["witness"]
    assert set(witness) == {"separator", "admissibility_witness"}


def test_inadmissible_witness_shape():
    data = generate_certificate(ALL_INSTANCES["INADMISSIBLE"])
    cert = json.loads(data)
    witness = cert["witness"]
    assert set(witness) == {"rule_id", "left_evidence", "right_evidence", "direction", "ancestry_path"}
