"""
proof_carrying_exactness_assess.assess

The generic end-to-end assessment pipeline:

    instance JSON bytes
        -> parse and validate (closed, shallow instance schema)
        -> generate_certificate (the untrusted generator)
        -> verify_certificate_bytes (the production verifier -- called
           HERE explicitly, never merely assumed because the generator
           already gates its own release; see `tests/test_pce_assess_
           fail_closed.py` for the test that proves this layer does not
           just trust the generator's own word)
        -> render a human-readable verdict

Trust boundary, stated precisely: this module and `cli.py` are
untrusted coordinators, exactly like `run_tracking_adapter_pipeline.py`
already is for the inherited tracking-adapter pipeline. Neither
computes any matrix, residue, or admissibility judgement of its own --
every accept/reject decision is made by `proof_carrying_exactness.
verify_certificate_bytes`, the one component in this whole pipeline
that is actually trusted.

`assess_instance` never raises for an anticipated failure -- the same
discipline `verify_certificate_bytes` itself establishes -- it always
returns a populated `AssessmentResult`. `reason` is always either the
literal string `"ACCEPT"` or one of the three `STAGE_*` tags below
followed by `": "` and a detail message, so a caller (`cli.py`) can
dispatch on the STAGE tag for its exit code without re-parsing prose.
"""

from dataclasses import dataclass
from typing import Optional

from proof_carrying_exactness import VerificationResult, verify_certificate_bytes
from proof_carrying_exactness.canonical import strict_json_loads
from proof_carrying_exactness.errors import CertificateRejected
from proof_carrying_exactness_generator import CertificateGenerationFailed, generate_certificate

from .renderer import render_summary

STAGE_MALFORMED_INSTANCE = "malformed_instance"
STAGE_GENERATION_FAILED = "generation_failed"
STAGE_VERIFICATION_REJECTED = "verification_rejected"

# Closed top-level instance schema -- deliberately the same shape
# `proof_carrying_exactness_generator.generator._parse_instance`
# already accepts, checked shallowly here (object, known keys, roughly
# correct shapes) BEFORE the generator ever attempts to solve, search,
# or factorise anything.
INSTANCE_KEYS = frozenset({"D", "r", "L", "provenance", "policy", "row_evidence_ids", "claim_metadata"})


@dataclass(frozen=True)
class AssessmentResult:
    accepted: bool
    verdict: Optional[str]
    certificate_bytes: Optional[bytes]
    summary: str
    reason: str


def _require_list(name: str, value) -> None:
    if value is not None and not isinstance(value, list):
        raise ValueError(f"instance field {name!r} must be a list")


def _require_matrix(name: str, value) -> None:
    if value is not None and not (isinstance(value, list) and all(isinstance(row, list) for row in value)):
        raise ValueError(f"instance field {name!r} must be a matrix (a list of lists)")


def _require_object(name: str, value) -> None:
    if value is not None and not isinstance(value, dict):
        raise ValueError(f"instance field {name!r} must be a JSON object")


def _validate_instance_schema(obj) -> dict:
    if not isinstance(obj, dict):
        raise ValueError(f"instance is not a JSON object: {obj!r}")
    extra = set(obj.keys()) - INSTANCE_KEYS
    if extra:
        raise ValueError(f"instance has unrecognized field(s): {sorted(extra)}")
    _require_matrix("D", obj.get("D"))
    _require_list("r", obj.get("r"))
    _require_matrix("L", obj.get("L"))
    _require_object("provenance", obj.get("provenance"))
    _require_object("policy", obj.get("policy"))
    _require_object("row_evidence_ids", obj.get("row_evidence_ids"))
    return obj


def _rejected(stage: str, detail: str, summary: str) -> AssessmentResult:
    return AssessmentResult(
        accepted=False,
        verdict=None,
        certificate_bytes=None,
        summary=summary,
        reason=f"{stage}: {detail}",
    )


def assess_instance(instance_bytes: bytes) -> AssessmentResult:
    """Runs the complete pipeline and never raises: any anticipated
    failure at any stage becomes an `AssessmentResult(accepted=False,
    ...)` with a stage-tagged `reason`, exactly as `verify_certificate_
    bytes` itself never raises for an anticipated certificate
    rejection."""
    try:
        obj = strict_json_loads(instance_bytes)
        instance = _validate_instance_schema(obj)
    except (CertificateRejected, ValueError) as e:
        return _rejected(STAGE_MALFORMED_INSTANCE, str(e), "The instance is malformed and could not be assessed.")
    except Exception:
        return _rejected(STAGE_MALFORMED_INSTANCE, "internal parsing failure", "The instance is malformed and could not be assessed.")

    try:
        certificate_bytes = generate_certificate(instance)
    except CertificateGenerationFailed as e:
        return _rejected(STAGE_GENERATION_FAILED, str(e), "No certificate could be generated for this instance.")
    except Exception as e:
        return _rejected(STAGE_GENERATION_FAILED, str(e), "No certificate could be generated for this instance.")

    # Explicit, independent re-verification -- deliberately not just
    # trusting that `generate_certificate` already gated itself. If the
    # generator were ever buggy or bypassed, this is the second, and
    # actually decisive, gate.
    verification: VerificationResult = verify_certificate_bytes(certificate_bytes)
    if not verification.accepted:
        return _rejected(
            STAGE_VERIFICATION_REJECTED,
            verification.reason,
            "The generated certificate was rejected by independent verification.",
        )

    return AssessmentResult(
        accepted=True,
        verdict=verification.verdict,
        certificate_bytes=certificate_bytes,
        summary=render_summary(verification.verdict),
        reason="ACCEPT",
    )
