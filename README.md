# Proof-Carrying Exactness

**Status: founding proposal only. No implementation yet.** See
[`docs/design/PROOF_CARRYING_EXACTNESS_PROPOSAL.md`](docs/design/PROOF_CARRYING_EXACTNESS_PROPOSAL.md)
for the full, unreviewed founding proposal and the author's own
follow-up on what to build first. Nothing in this repository currently
implements that proposal.

## What this repository is

An investigation of a single question: when is an exact computational
object genuinely constituted by distributed, regional evidence, rather
than merely asserted by a system? The proposed answer combines
Whitehead's theory of extensive abstraction with a finite, exact
rational obstruction calculus, aiming at a system that returns one of
three independently checkable verdicts for a claimed exact object:
`EXACT`, `OBSTRUCTED`, or `INADMISSIBLE`.

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

- `rocq/`, `ocaml/`: the inherited proof and certificate-checking
  infrastructure, unmodified.
- Root-level `.py` files: the inherited R1-R24 diagnostic, refinement-
  witness, R21 certificate, and tracking-adapter/Stone-Soup Python
  modules, unmodified.
- `docs/`: the inherited design documents for that existing work, plus
  this project's own founding proposal
  (`docs/design/PROOF_CARRYING_EXACTNESS_PROPOSAL.md`).
- `examples/`, `tests/`: the inherited fixtures and test suite for the
  above, unmodified.

None of this yet reflects a proof-carrying-exactness-specific design.
The `EXACT`/`OBSTRUCTED`/`INADMISSIBLE` verdict system, the unified
certificate schema, the obstruction-capable demonstrator, and the
formal Rocq objects the proposal describes (`AdmissibilityPolicy`,
`RegionalEvidenceState`, `ExactnessJudgement`, and so on) do not exist
yet.

## Licence

Not yet decided for this repository specifically. The inherited
`LICENSE` file is AGPL-3.0-or-later, carried over from
`regional-obstruction-calculus`; confirm this is the intended licence
for this project before treating it as final.
