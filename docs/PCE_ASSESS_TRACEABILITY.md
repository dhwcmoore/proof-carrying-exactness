# Proof-Carrying Exactness Assess: Traceability Manifest

Maps every obligation of the generic end-to-end assessment boundary
(`proof_carrying_exactness_assess/`, launched via the root-level
`pce_assess.py`) to at least one production test in `tests/test_pce_
assess_*.py`, the same discipline
[`docs/PCE_VERIFIER_TRACEABILITY.md`](PCE_VERIFIER_TRACEABILITY.md) and
[`docs/PCE_GENERATOR_TRACEABILITY.md`](PCE_GENERATOR_TRACEABILITY.md)
already establish for the verifier and the generator.

## What this layer is not trusted for

This layer computes no matrix, residue, or admissibility judgement of
its own -- it is an untrusted coordinator, exactly like `run_tracking_
adapter_pipeline.py` already is for the inherited tracking-adapter
pipeline. Its correctness is not part of why a certificate is sound;
`proof_carrying_exactness.verify_certificate_bytes` is the only
component whose ACCEPT means anything. Concretely, this layer calls
that verifier a SECOND time, itself, after the generator has already
returned bytes -- never merely trusting that the generator's own
internal gate (`docs/PCE_GENERATOR_TRACEABILITY.md`'s "verifier-gated
release" obligation) already ran. A bug in this layer can at most
produce a spurious REJECT or a missing certificate file; it can never
turn a REJECT from the production verifier into an ACCEPT the caller
sees.

Its obligations are therefore exactly these, in pipeline order:

1. parse the instance bytes and validate their shallow schema;
2. invoke the untrusted generator;
3. independently re-verify whatever the generator returns;
4. render only what the verified certificate proves;
5. report a distinct exit code per failure stage;
6. never leave a certificate file behind except after ACCEPT.

## Obligation -> test mapping

### Parsing and validation

Strict JSON parsing (reusing `proof_carrying_exactness.canonical.
strict_json_loads`) followed by a shallow, closed instance schema
check, both BEFORE the generator is ever invoked.

| Requirement | Test |
|---|---|
| Malformed JSON rejected before generation is attempted | `tests/test_pce_assess_cli.py::test_malformed_json_exits_nonzero_and_writes_no_certificate` |
| Malformed instance schema (wrong field shape) rejected | `tests/test_pce_assess_cli.py::test_malformed_instance_schema_exits_nonzero_and_writes_no_certificate` |
| Unrecognized top-level instance field rejected (closed schema) | `tests/test_pce_assess_cli.py::test_unrecognized_instance_field_is_a_malformed_schema_rejection` |
| Unreadable/missing instance file rejected | `tests/test_pce_assess_cli.py::test_missing_instance_file_exits_nonzero` |

### Generator invocation

Calling `proof_carrying_exactness_generator.generate_certificate` over
the validated instance, and reporting distinctly when it cannot
produce a certificate at all.

| Requirement | Test |
|---|---|
| A schema-valid but unresolvable instance (no admissibility violation, no algebraic system) fails at this stage, not silently | `tests/test_pce_assess_cli.py::test_generator_failure_exits_nonzero_and_writes_no_certificate` |
| Generation-failure exit code (2) is distinct from malformed-instance (1) and verifier-rejection (3) | `tests/test_pce_assess_cli.py::test_exit_code_contract` |

### Independent re-verification

The load-bearing result of this milestone: `assess_instance` calls
`verify_certificate_bytes` itself, a second time, rather than trusting
that `generate_certificate` already gated its own release.

| Requirement | Test |
|---|---|
| A certificate that a (simulated) ungated generator hands back is still rejected by this layer's own verification call | `tests/test_pce_assess_fail_closed.py::test_verification_rejection_is_reported_distinctly` |
| `assess_instance` never reaches `accepted=True` when the generator itself is faked out | `tests/test_pce_assess_fail_closed.py::test_assess_instance_never_bypasses_the_verifier_even_if_the_generator_does` |
| **The CLI cannot bypass verification**, end to end, including exit code and certificate-file behaviour | `tests/test_pce_assess_fail_closed.py::test_cli_never_bypasses_the_verifier` |

### Verdict rendering

Human-readable text describing only what the verified certificate
proves, one sentence per verdict, with no inferred cause or
recommendation.

| Requirement | Test |
|---|---|
| Correct, verdict-specific wording for all four verdicts | `tests/test_pce_assess_cli.py::test_human_readable_wording_for_each_verdict` (parametrized over `EXACT`, `UNDERDETERMINED`, `OBSTRUCTED`, `INADMISSIBLE`) |
| `ACCEPT <verdict>` plus the independent-verification confirmation line appears for every accepted verdict | `tests/test_pce_assess_cli.py::test_cli_complete_run_for_each_verdict` |

### Exit codes

| Exit code | Meaning | Test |
|---|---|---|
| `0` | ACCEPT | `tests/test_pce_assess_cli.py::test_exit_code_contract` |
| `1` | malformed instance (bad JSON, schema violation, or unreadable file) | `tests/test_pce_assess_cli.py::test_exit_code_contract`, `::test_malformed_json_exits_nonzero_and_writes_no_certificate`, `::test_missing_instance_file_exits_nonzero` |
| `2` | certificate generation failed | `tests/test_pce_assess_cli.py::test_exit_code_contract`, `::test_generator_failure_exits_nonzero_and_writes_no_certificate` |
| `3` | the generated certificate was rejected by independent verification | `tests/test_pce_assess_fail_closed.py::test_cli_never_bypasses_the_verifier` |
| `4` | ACCEPT, but the certificate could not be written to `--certificate-out` | `tests/test_pce_assess_cli.py::test_exit_code_contract`, `::test_unwritable_output_path_exits_nonzero` |

### Deterministic certificate output

The same instance must produce byte-identical certificates across
separate CLI invocations, not just separate calls to the generator
in-process (`tests/test_generator_certificates.py::test_certificate_
bytes_are_deterministic` already covers the library layer).

| Requirement | Test |
|---|---|
| Two separate `pce_assess.py` subprocess runs over the same instance produce byte-identical certificate files | `tests/test_pce_assess_cli.py::test_certificate_bytes_are_deterministic_across_separate_cli_runs` |

### Atomic / no-leftover failure behaviour

No certificate file is ever written except after ACCEPT; a failed
write never leaves a partial file, and no earlier pipeline failure
ever reaches the write step at all.

| Requirement | Test |
|---|---|
| No certificate file after malformed JSON | `tests/test_pce_assess_cli.py::test_malformed_json_exits_nonzero_and_writes_no_certificate` |
| No certificate file after malformed schema | `tests/test_pce_assess_cli.py::test_malformed_instance_schema_exits_nonzero_and_writes_no_certificate` |
| No certificate file after generation failure | `tests/test_pce_assess_cli.py::test_generator_failure_exits_nonzero_and_writes_no_certificate` |
| An unwritable `--certificate-out` path is never created (the parent directory does not exist either) | `tests/test_pce_assess_cli.py::test_unwritable_output_path_exits_nonzero` |
| No certificate file after a verifier-rejected (simulated ungated generator) run | `tests/test_pce_assess_fail_closed.py::test_cli_never_bypasses_the_verifier` |
