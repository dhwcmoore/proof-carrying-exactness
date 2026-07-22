# Proof-Carrying Exactness

**Status: a pure certificate verifier exists, an untrusted four-verdict
certificate generator exists alongside it as a library API, and a
generic end-to-end assessment interface (library function and CLI)
now composes the two.** See
[`docs/design/PROOF_CARRYING_EXACTNESS_PROPOSAL.md`](docs/design/PROOF_CARRYING_EXACTNESS_PROPOSAL.md)
for the full, unreviewed founding proposal;
[`docs/design/PROOF_CARRYING_EXACTNESS_SPEC.md`](docs/design/PROOF_CARRYING_EXACTNESS_SPEC.md)
for the semantic specification (the `EXACT`/`UNDERDETERMINED`/
`OBSTRUCTED`/`INADMISSIBLE` distinction); and
[`docs/design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md`](docs/design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md)
for the certificate boundary the `proof_carrying_exactness/` package
below implements.

The `proof_carrying_exactness/` package is a pure VERIFIER only: it
checks an already-produced certificate and never produces one.
`proof_carrying_exactness_generator/` is a separate, UNTRUSTED package
that discovers a witness for all four verdicts -- solving, searching,
and factorising freely, none of which the verifier is permitted to do
-- but it sits entirely outside the trusted computing base:
`generate_certificate` releases certificate bytes only after
independently resubmitting them to `proof_carrying_exactness.verify_
certificate_bytes` and confirming ACCEPT, raising an exception and
releasing nothing otherwise. `proof_carrying_exactness_assess/`
composes both packages into one generic pipeline -- parse and validate
an instance, generate a certificate, independently verify it AGAIN at
this layer (never merely trusting that the generator already did), and
render only what the verified certificate proves -- exposed as both
`assess_instance(instance_bytes: bytes) -> AssessmentResult` and the
small `pce-assess` CLI (`python3 pce_assess.py instance.json
--certificate-out verdict.json`). It carries no region-specific
semantics of its own. `docs/PCE_END_TO_END_DEMONSTRATION.md` records a
reproducible, fresh-clone run of all four verdicts through this generic
pipeline, including a tampered-certificate rejection and a simulated
malicious-generator rejection. There is still no region-native adapter
and no tracking/sensor-fusion adapter -- no demonstration over real
regional evidence exists yet, only the generic affine-rational one
above -- those remain future work, tracked in the design documents
above, not implemented here.

## What this repository is

An investigation of a single question: when is an exact computational
object genuinely constituted by distributed, regional evidence, rather
than merely asserted by a system? The answer combines Whitehead's
theory of extensive abstraction with a finite, exact rational
obstruction calculus. The central, spike-established distinction is
that repairability of a regional system does not imply that a claimed
output is exactly constituted by it: a coherent global reconciliation
can exist while the claimed value still varies across every equally
valid reconciliation. The specification defines four independently
checkable verdicts for a claimed exact object: `EXACT`,
`UNDERDETERMINED`, `OBSTRUCTED`, or `INADMISSIBLE`.

## Provenance

This repository was seeded from `regional-obstruction-calculus`'s
technical and proof content — `rocq/` (37 machine-checked modules),
`ocaml/`, the R1-R24 diagnostic and refinement-witness Python modules,
the R21 exact-rational repair-or-separator certificate pipeline, and
the tracking-adapter / Stone Soup applied layer — kept here as
foundation and reference material, not as a finished part of this
project. It is a fresh, independent git history with no shared commits
with that repository; that repository's own narrative documentation
(its README, STATUS, RESULTS, PROJECT_MAP, CHANGELOG, CITATION,
CONTRIBUTING) was deliberately not carried over, since it describes a
different project's own identity and release history.

## What exists here right now

- `proof_carrying_exactness/`: the production certificate VERIFIER --
  `verify_certificate_bytes(data: bytes) -> VerificationResult`. Checks
  all four verdicts (`EXACT`, `UNDERDETERMINED`, `OBSTRUCTED`,
  `INADMISSIBLE`) against the closed schemas and digest boundary
  `docs/design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md` defines,
  with no discovery/search dependency of its own (mechanically checked
  by `tests/test_pce_import_boundary.py`). See
  `docs/PCE_VERIFIER_TRACEABILITY.md` for the full mapping from
  specification requirements to tests.
- `proof_carrying_exactness_generator/`: an UNTRUSTED four-verdict
  certificate GENERATOR --
  `generate_certificate(instance: Mapping[str, object]) -> bytes`. Free
  to solve, search, and factorise (unlike the verifier), for the affine
  rational class the certificate spec currently covers. It sits outside
  the trusted computing base: it never returns certificate bytes the
  production verifier has not independently accepted first, raising
  `CertificateGenerationFailed` (releasing nothing) if verification
  fails. See `docs/PCE_GENERATOR_TRACEABILITY.md` for the full mapping
  from generator obligations to tests, and `tests/test_generator_import_
  boundary.py` for the mechanical proof that the verifier never
  imports it back.
- `proof_carrying_exactness_assess/` (launched via the root-level
  `pce_assess.py`): the generic, region-agnostic end-to-end assessment
  boundary -- `assess_instance(instance_bytes: bytes) ->
  AssessmentResult` and the small `pce-assess` CLI (`python3
  pce_assess.py instance.json --certificate-out verdict.json`). Parses
  and shallowly validates the instance, calls the generator, calls the
  production verifier a SECOND time itself (never merely trusting the
  generator's own internal gate), and renders only what the verified
  certificate proves. Fails closed with a distinct exit code for a
  malformed instance, a generation failure, a verifier rejection, or an
  unwritable certificate output path; never writes a certificate file
  except after ACCEPT. No region-specific semantics live here yet. See
  `docs/PCE_ASSESS_TRACEABILITY.md` for the full mapping from this
  layer's obligations to tests.
- `rocq/`, `ocaml/`: the inherited proof and certificate-checking
  infrastructure, unmodified.
- Root-level `.py` files, excluding `pce_assess.py` (this project's own
  CLI launcher, above): the inherited R1-R24 diagnostic, refinement-
  witness, R21 certificate, and tracking-adapter/Stone-Soup Python
  modules, unmodified -- reference material this project's own
  verifier and generator reuse primitives from, not a finished part of
  this project's own applied layer.
- `docs/`: the inherited design documents for that existing work, plus
  this project's own founding proposal and both specifications above.
- `examples/`, `tests/`: the inherited fixtures and test suite,
  unmodified, plus this project's own `tests/test_pce_*.py` production
  test suite, `tests/test_inherited_foundation_inventory.py` (an
  inventory check over the inherited Rocq foundation and upstream
  provenance record, replacing an earlier test that encoded
  `regional-obstruction-calculus`'s own documentation identity rather
  than this repository's), and `examples/pce_assess/` (the four
  instance fixtures `docs/PCE_END_TO_END_DEMONSTRATION.md` and
  `tests/test_pce_assess_demonstration.py` both exercise).

Not yet built: no region-native adapter and no tracking/sensor-fusion
adapter exist; no end-to-end demonstration over real regional evidence
exists yet (only the generic affine-rational pipeline above); and the
formal Rocq objects the proposal describes (`AdmissibilityPolicy`,
`RegionalEvidenceState`, `ExactnessJudgement`, and so on) do not exist
either.

## Licence

This repository is licensed under the GNU Affero General Public
License v3.0 or later. It contains an unmodified reference foundation
imported from `dhwcmoore/regional-obstruction-calculus`, together with
new work specific to proof-carrying exactness. See
[`NOTICE`](NOTICE) and [`docs/UPSTREAM_PROVENANCE.md`](docs/UPSTREAM_PROVENANCE.md)
for provenance and attribution details.
