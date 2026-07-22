# Proof-Carrying Exactness Generator: Traceability Manifest

Maps every obligation of the untrusted certificate GENERATOR
(`proof_carrying_exactness_generator/`) to at least one production test
in `tests/test_generator_*.py`, the same discipline
[`docs/PCE_VERIFIER_TRACEABILITY.md`](PCE_VERIFIER_TRACEABILITY.md)
already establishes for the verifier.

## The generator is not trusted for soundness

Nothing in this document certifies that the generator is *correct*.
Its own correctness is explicitly **not** part of the trusted computing
base: `proof_carrying_exactness/` (the verifier) is the only component
whose acceptance means anything. A bug in the generator can at most
produce a spurious `CertificateGenerationFailed` (a missed opportunity
to certify something true); it can never produce a false `ACCEPT`,
because `generate_certificate` never returns bytes the production
verifier has not independently re-checked first.

The generator's obligations are therefore exactly four, in this order:

1. find a valid witness when possible (solving, searching, and
   factorising freely -- discovery the verifier itself is forbidden
   from doing);
2. serialise the resulting certificate deterministically;
3. submit the serialised certificate to the production verifier
   (`proof_carrying_exactness.verify_certificate_bytes`);
4. release nothing -- raise `CertificateGenerationFailed` instead of
   returning bytes -- if that submission does not come back `ACCEPT`.

## Obligation -> test mapping

### INADMISSIBLE path discovery

Finding a genuine ancestry path between a declared independent pair,
and emitting the INADMISSIBLE verdict instead of attempting the
algebraic branch at all.

| Requirement | Test |
|---|---|
| Generates an INADMISSIBLE certificate the production verifier accepts | `tests/test_generator_certificates.py::test_generates_a_certificate_the_production_verifier_accepts[INADMISSIBLE]` |
| Admissibility is checked BEFORE the algebraic branch | `tests/test_generator_certificates.py::test_generates_a_certificate_the_production_verifier_accepts[INADMISSIBLE]` (instance supplies no `D`/`r` at all) |
| INADMISSIBLE witness has the correct shape (`rule_id`, both evidence identifiers, `direction`, `ancestry_path`) | `tests/test_generator_certificates.py::test_inadmissible_witness_shape` |

### OBSTRUCTED separator generation

Running `repair_or_separate` and, when it returns a separator, emitting
the OBSTRUCTED verdict with that separator as the witness.

| Requirement | Test |
|---|---|
| Generates an OBSTRUCTED certificate the production verifier accepts | `tests/test_generator_certificates.py::test_generates_a_certificate_the_production_verifier_accepts[OBSTRUCTED]` |
| OBSTRUCTED witness has the correct shape (`separator`, `admissibility_witness`) | `tests/test_generator_certificates.py::test_obstructed_witness_shape` |
| A corrupted separator is never released | `tests/test_generator_fail_closed.py::test_corrupted_obstructed_separator_is_never_released` |

### UNDERDETERMINED repair and gauge witness

Running `repair_or_separate` to a repair, then testing whether any
basis vector of `ker(D)` changes `L`'s value; if one does, emitting
UNDERDETERMINED with that repair and gauge direction.

| Requirement | Test |
|---|---|
| Generates an UNDERDETERMINED certificate the production verifier accepts | `tests/test_generator_certificates.py::test_generates_a_certificate_the_production_verifier_accepts[UNDERDETERMINED]` |
| UNDERDETERMINED witness has the correct shape (`repair_witness`, `gauge_witness`, `admissibility_witness`) | `tests/test_generator_certificates.py::test_underdetermined_witness_shape` |

### EXACT factorisation construction

When no basis vector of `ker(D)` changes `L`'s value, solving for `M`
with `M D = L` and emitting EXACT with the repair, the factorisation,
and the claimed value `M r`.

| Requirement | Test |
|---|---|
| Generates an EXACT certificate the production verifier accepts | `tests/test_generator_certificates.py::test_generates_a_certificate_the_production_verifier_accepts[EXACT]` |
| EXACT witness has the correct shape (`repair_witness`, `factorisation_witness`, `claimed_value`, `admissibility_witness`) | `tests/test_generator_certificates.py::test_exact_witness_shape` |
| A corrupted claimed value is never released | `tests/test_generator_fail_closed.py::test_corrupted_exact_witness_is_never_released` |

### Deterministic certificate bytes

The same instance must serialise to identical bytes on every call --
required for the verifier's digest recomputation to be meaningful and
for reproducible release artefacts.

| Requirement | Test |
|---|---|
| Repeated generation over the same instance produces identical bytes, for all four verdicts | `tests/test_generator_certificates.py::test_certificate_bytes_are_deterministic` (parametrized over `EXACT`, `UNDERDETERMINED`, `OBSTRUCTED`, `INADMISSIBLE`) |

### Verifier-gated release

The fail-closed contract: `generate_certificate` must never return
bytes the production verifier itself would reject, regardless of
which internal step produced the corruption.

| Requirement | Test |
|---|---|
| Corrupted EXACT witness never released | `tests/test_generator_fail_closed.py::test_corrupted_exact_witness_is_never_released` |
| Corrupted OBSTRUCTED separator never released | `tests/test_generator_fail_closed.py::test_corrupted_obstructed_separator_is_never_released` |
| Corrupted digest at the serialisation step never released | `tests/test_generator_fail_closed.py::test_tampered_input_digest_after_serialisation_is_never_released` |
| A certificate tampered with AFTER a successful generation is still rejected by the verifier (the generator's own gate is not the only line of defence) | `tests/test_generator_certificates.py::test_tampering_after_generation_is_rejected` (parametrized over all four verdicts) |

### One-way dependency boundary

The generator may depend on the verifier (to gate its own release);
the verifier must never depend on the generator, in either direction,
statically or dynamically -- the same AST-scan discipline
`tests/test_pce_import_boundary.py` already established for the
verifier's boundary against solver/search machinery, applied here to
the boundary's other side.

| Requirement | Test |
|---|---|
| Generator package exists and is nonempty | `tests/test_generator_import_boundary.py::test_generator_package_exists_and_is_nonempty` |
| No file in `proof_carrying_exactness/` statically imports the generator package | `tests/test_generator_import_boundary.py::test_verifier_never_imports_the_generator_package` |
| No file in `proof_carrying_exactness/` dynamically imports the generator package | `tests/test_generator_import_boundary.py::test_verifier_never_dynamically_imports_the_generator_package` |
| Importing the verifier package does not transitively pull in the generator package | `tests/test_generator_import_boundary.py::test_importing_the_verifier_does_not_pull_in_the_generator_package` |
