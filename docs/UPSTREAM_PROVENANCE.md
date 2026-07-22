# Upstream provenance

This document records, precisely, how this repository's inherited
foundation was imported. Written as part of a 2026-07-22 authorship
and licensing audit, performed before pushing this repository's second
commit (`825804d`, the proof-carrying-exactness specification).

```text
Upstream repository:
    dhwcmoore/regional-obstruction-calculus

Exact upstream commit:
    a9d68c34dbed7546d1cfb4e797d72e3af4c73278

Verification:
    Confirmed directly, not assumed from a timestamp or tag: the
    working tree copied into this repository was diffed byte-for-byte
    against `git show a9d68c34dbed7546d1cfb4e797d72e3af4c73278:<path>`
    for a representative sample of both Rocq and Python files
    (rocq/CertificateTransport.v, tracking_adapter_stonesoup_
    trackfusion_emitter.py, r21_repair_or_separator.py, LICENSE) --
    all byte-identical. The upstream working tree was clean (no
    uncommitted changes) at the moment of import, so the snapshot
    reflects exactly one upstream commit, not an uncommitted or mixed
    state.

Import repository commit (this repository):
    75661d6 -- "Seed repository: inherit proof/certificate
    infrastructure, fresh identity"

Import relationship:
    Snapshot import (plain filesystem copy, `cp -a`) with NO shared
    git history. This repository's git history starts fresh at
    75661d6; it does not contain, and cannot be merged with, any
    commit from dhwcmoore/regional-obstruction-calculus.

Upstream copyright holder:
    Duston Moore, Independent Researcher (per that repository's own
    CITATION.cff `authors:` field and its README's own sign-off; this
    repository's own author, so no attribution conflict arises).
```

## Inherited paths (unmodified, imported as reference material)

```text
rocq/                                    37 Rocq modules (proof/certificate infrastructure)
ocaml/                                   OCaml certificate checkers and parity mirrors
docs/design/                             design documents for the inherited proof work
docs/diagnostics/                        diagnostic-rule design documents
docs/theory/                             theorem-concordance and related documents
docs/archive/                            archived design material
docs/R21_END_TO_END_DEMONSTRATION.md
docs/TRACKING_ADAPTER_END_TO_END_DEMONSTRATION.md
docs/STONESOUP_THIRD_PARTY_NOTICE.md     Stone Soup's own third-party licence/copyright notice
examples/                                tracked fixtures (four-cycle, tracking-adapter scenarios)
tests/                                   the full inherited pytest suite (50 files)
associator_residue.py, boolean_crossing_diagnostic.py,
candidate_discipline_diagnostic.py, carrier_matrix_infrastructure.py,
certificate_emitter.py, conflict_diagnostic_completeness_probe.py,
conflict_resolution_lower_bound_probe.py,
conflict_resolution_trilemma_probe.py, coupled_realisability_diagnostic.py,
finite_algebra.py, first_order_certificate_checker.py,
lattice_ie_diagnostic.py, r21_certificate_checker.py,
r21_certificate_emitter.py, r21_certificate_format.py,
r21_repair_or_separator.py, rational_linear_algebra.py,
realisability_diagnostic.py, refinement_checker.py,
refinement_witness_a4_e0_counterexample_search.py,
refinement_witness_composition_boundary_search.py,
refinement_witness_composition_probe.py,
refinement_witness_coupled_a4_cancellation_probe.py,
refinement_witness_coupled_parallel_probe.py, refinement_witnesses.py,
refinement_witness_parallel_disjoint_probe.py, regional_composition.py,
repair_solver.py, repeated_triple_support_diagnostic.py,
residue_classifier.py, run_associator_obstruction.py,
run_tracking_adapter_pipeline.py, tracking_adapter_canon.py,
tracking_adapter_certificate.py, tracking_adapter_format.py,
tracking_adapter_generator.py, tracking_adapter_provenance.py,
tracking_adapter_stonesoup_emitter.py,
tracking_adapter_stonesoup_provenance.py,
tracking_adapter_stonesoup_trackfusion_emitter.py,
tracking_adapter_stonesoup_trackfusion.py, tracking_adapter_verifier.py
requirements.txt, requirements-stonesoup.txt
Makefile, Dockerfile, .dockerignore, .gitignore
.github/workflows/formal-verification.yml
LICENSE                                  byte-identical to upstream (verified: cmp reported no difference)
```

## Removed during import

```text
Old project-identity documents:
    README.md, STATUS.md, RESULTS.md, PROJECT_MAP.md, CHANGELOG.md,
    CITATION.cff, CONTRIBUTING.md, REPRODUCIBILITY.md
    (describe regional-obstruction-calculus's own identity, release
    history, and R1-R24 narrative -- not carried over; this
    repository's own README/NOTICE/UPSTREAM_PROVENANCE.md are written
    fresh instead)
Build artefacts:
    assembly_checker, associator_contribution_checker,
    refinement_checker_ocaml, roc-solve-extracted, roc-verify-ocaml
    (compiled binaries, regenerable by `make`, never source)
Caches:
    __pycache__/, .pytest_cache/, .lia.cache
Previous virtual environment:
    .venv/
```

## Modified inherited implementation files

```text
None. Every inherited rocq/*.v, ocaml/*.ml, and root-level *.py file
is byte-identical to the upstream commit above (spot-checked directly,
see "Verification" above; no file in this list has been edited since
import).
```

## New proof-carrying-exactness material (not inherited)

```text
README.md                                          written fresh for this project
NOTICE                                              this project's own licensing/attribution notice
docs/UPSTREAM_PROVENANCE.md                         this document
docs/design/PROOF_CARRYING_EXACTNESS_PROPOSAL.md    founding proposal, verbatim, unreviewed
docs/design/PROOF_CARRYING_EXACTNESS_SPEC.md        first architectural specification
```

## Licence

`AGPL-3.0-or-later`, repository-wide, covering both the inherited
foundation (already so licensed upstream, confirmed byte-identical
`LICENSE`) and the new proof-carrying-exactness material above. No
separate licence regime (e.g. a Creative Commons licence for the
design documents) has been introduced. No proprietary or permissive
relicensing is promised for any inherited contribution pending a
determination of whether every inherited contribution is solely
authored by this repository's own copyright holder -- per the upstream
repository's own `CITATION.cff` and README sign-off, it is, but that
determination rests on the upstream repository's own records, not on
anything re-derived here.
