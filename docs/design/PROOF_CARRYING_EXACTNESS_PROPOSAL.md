# Proof-Carrying Exactness: Founding Proposal (2026-07-21, unreviewed)

**Status: raw founding material, not yet a reviewed design spec.** This
document is the verbatim project proposal that founded this repository,
preserved as written rather than summarized, plus the author's own
follow-up elaboration on what to build first. Nothing below has been
implemented, reviewed against this repository's own engineering
discipline (bounded spikes before architecture, independent verifiers,
hand-authored fixtures with reasoning spelled out inline), or converted
into a proper specification. Treat every "would"/"should"/"the project
should" sentence as proposed, not decided.

**Provenance**: this repository began as a copy of
`regional-obstruction-calculus`'s technical/proof content (`rocq/`,
`ocaml/`, the R1-R24 diagnostic and refinement-witness Python modules,
the R21 certificate pipeline, and the tracking-adapter/Stone-Soup
applied layer), with that project's own narrative documentation
(README, STATUS, RESULTS, PROJECT_MAP, CHANGELOG, CITATION, CONTRIBUTING)
deliberately NOT carried over, since those describe a different
project's own identity and release history. The proof/certificate
infrastructure is kept as foundation and reference material; this
repository's own README, status, and design documents are written fresh.

---

## Part 1: the original proposal

## **Proof-Carrying Exactness: Regional Constitution, Admissible Refinement, and Obstruction Certificates**

The project would investigate a single question:

> **When is an exact computational object genuinely constituted by distributed, regional evidence, rather than merely asserted by a system?**

The answer would combine Whitehead's theory of extensive abstraction with the regional obstruction calculus.

The basic claim would be:

> An output is exact only when it is invariant across admissible routes of regional determination.

A system making an exact claim must therefore produce one of two results:

    EXACT(x, w)

where `x` is the global determination and `w` is a checkable certificate that it has been legitimately constituted, or:

    OBSTRUCTED(o)

where `o` is a checkable certificate showing that no such global determination follows from the available evidence under the declared rules.

This would not be a project about making numerical outputs more precise. It would be about determining whether a precise output is warranted at all.

### 1. The conceptual foundation

Whitehead's non-pointal geometry would provide the philosophical starting point.

A point is not treated as an extensionless constituent buried beneath extended regions. It is constituted through an organised system of regional approximations. Different routes of approximation determine the same point when their differences can legitimately be factored out.

The project would generalise this structure:

    regional determinations -> admissible refinement routes -> equivalence classes -> exact invariant.

A computational object would therefore be exact relative to a declared admissibility structure, not exact in isolation.

For example, a fused track would not fundamentally be a point moving through space. It would be an invariant extracted from: sensor observations; coordinate transformations; temporal windows; association decisions; uncertainty regions; provenance histories; permissible corrections.

The exact track would be the result that remains invariant across every admissible route through this evidence.

This would produce a precise philosophical thesis:

> **Exactness is a mode of successful constitution, not an intrinsic property of a value.**

A rational coordinate may be arithmetically exact while still failing to constitute an exact location. A fused estimate may be numerically stable while relying on duplicated evidence. A deterministic classifier may return the same label repeatedly while failing under a semantically legitimate change of presentation.

The project would distinguish these cases formally.

### 2. The formal object of study

The project should begin with a finite rational model rather than attempting a universal theory immediately.

An instance would contain `I = (E, A, D, r, Pi, T)`, where: `E` is the structured regional evidence; `A` is the admissibility specification; `D` represents the permitted local adjustments or coboundaries; `r` is the observed compatibility residue; `Pi` is the provenance structure; `T` is the declared family of transformations and refinements.

The admissibility specification would state: (1) which evidence items may be combined; (2) which transformations preserve the meaning of the claim; (3) which sources count as independent; (4) which corrections are permitted; (5) which distinctions may be factored out; (6) which background assumptions bound the certificate.

The local-to-global problem would initially be represented by `D u = r`.

If there exists `u` such that `D u = r`, the local residue can be absorbed by permitted adjustments.

If there exists `y` such that `y^T D = 0` and `y^T r != 0`, then no permitted adjustment can eliminate the residue.

The two cases would receive a new semantic interpretation.

**Positive case** — `D u = r` means: the regional determinations can be assembled into a globally coherent determination under the declared admissibility structure.

**Negative case** — `y^T D = 0, y^T r != 0` means: the proposed exact object has not been constituted by this evidence under the declared admissibility structure.

The second result is not merely an inconsistency report. It is a certificate that the local determinations cannot descend to the claimed global invariant.

### 3. The central definition

Let `R` be the set of admissible routes of determination. Let `rho1 ~_A rho2` mean that two routes are equivalent under the admissibility specification `A` — possessing a common admissible refinement, or having differences generated entirely by permitted transformations. Let `pi_A : R -> R/~_A` be the quotient map.

Suppose the computational process produces a value `v : R -> X`. The output would be exact relative to `A` when there exists a presentation-independent map `v_bar : R/~_A -> X` such that `v = v_bar . pi_A`.

In plain language: the output must depend only on the admissible equivalence class of the route, not on accidental features of the route by which it was obtained.

**Proof-carrying exactness**: a claim `x` possesses proof-carrying exactness relative to `A` when the system returns a certificate establishing that (1) the evidence is admissible; (2) the routes used are provenance-valid; (3) the candidate value is invariant under the declared refinements; (4) the value descends to the admissible quotient; (5) an independent verifier can check these facts.

This is stronger than numerical exactness, confidence, consistency, or robustness.

### 4. The main theorem package

- **Theorem 1 (positive certificate soundness)**: if the verifier accepts a repair certificate `u`, then `D u = r`. Every accepted positive certificate proves that the regional residue is generated by permitted local adjustments.
- **Theorem 2 (obstruction certificate soundness)**: if the verifier accepts `y` satisfying `y^T D = 0` and `y^T r != 0`, then `r` is not in `im(D)`. Every accepted obstruction certificate proves that no permitted repair constitutes the claimed global object.
- **Theorem 3 (finite rational completeness)**: for every well-formed finite rational instance, either `exists u, D u = r`, or `exists y, y^T D = 0 and y^T r != 0`. The system can return either a repair certificate or an obstruction certificate — genuinely two-sided and complete, unlike some cohomological obstruction methods.
- **Theorem 4 (verdict exclusivity)**: no well-formed instance can possess both an accepted repair certificate and an accepted obstruction certificate.
- **Theorem 5 (admissible refinement invariance)**: if an instance `I'` is an admissible refinement of `I`, the exactness verdict must be preserved under stated conditions — distinguishing preservation of repairability, obstruction, certificate meaning, provenance validity, and output identity. Not every refinement preserves every verdict; the contribution is stating exactly which do.
- **Theorem 6 (provenance non-duplication)**: evidence that shares prohibited ancestry must not be counted as independent corroboration. Splitting one evidence item into several derived copies cannot strengthen an exactness claim when the provenance policy declares those copies dependent.
- **Theorem 7 (compositionality)**: `Exact(A, w_A) and Exact(B, w_B) and Compatible(A, B, c)` implies `Exact(A union B, w_{A union B})`. If compatibility fails, the system should preserve the failure rather than conceal it through aggregation.

### 5. The certificate architecture

Each output would carry a certificate envelope — a positive certificate (`exactness/positive/v1`: claim, evidence boundary, provenance, transformations, regional problem `D`/`r`, witness `u`, verification) or a negative/obstruction certificate (`exactness/obstruction/v1`: claim, evidence boundary, regional problem, obstruction `y` with support, diagnostic of implicated regions/transformations/provenance edges, verification). The support of `y` identifies which regional observations participate in the obstruction, giving the negative result operational value: not only that global constitution failed, but where.

### 6. The verified implementation

Three deliberately separated layers: an untrusted **generator** (parses evidence, constructs `D`/`r`, computes repair or separator, assembles the certificate); **independent verifiers** (at least two — Python and OCaml, exact rational arithmetic, closed schemas, duplicate-key rejection, digest recomputation, resource limits, fail-closed handling); a **formal proof layer** (Rocq) establishing that acceptance by the checker implies the relevant mathematical conclusion, verifying the boundary between an untrusted generator and a small trusted checker, not the whole sensor-fusion stack.

### 7. The principal demonstrator

A provenance-sensitive tracking/sensor-fusion scenario with cases producing superficially similar numerical outputs but different exactness statuses: clean constitution (`EXACT`); repairable disagreement (`EXACT` with an explicit repair witness); hidden common ancestry (`INADMISSIBLE`, even with unchanged numerical output); non-repairable cyclic disagreement (`OBSTRUCTED`, with the responsible cycle identified); tampered certificate (rejected by both independent verifiers).

This gives the project a necessary three-stage logic: admissibility -> constitution -> exactness verdict. An inadmissible instance should not be passed into the exactness calculus as though it were a valid evidential system.

### 8. The human-facing diagnostic

Each verdict should come with both a machine certificate and a human-readable explanation naming the specific policy, sensors, cycle, or shared ancestor responsible for the verdict — not just a bare accept/reject.

### 9. Relationship to existing work

`regional-obstruction-calculus` already supplies repair-versus-obstruction, exact rational separation, cycle certificates, quotient reasoning, refinement-invariance results, sequential/parallel composition, shared-seam compatibility, typed diagnostics, non-lossy conflict results, certificate generation and independent verification, plus (in the applied layer) proof-carrying pairwise/global certificates, fail-closed verification, provenance gates, tracking adapters, Stone Soup integration, data-incest examples, and independent Python/OCaml verifiers end to end.

The project would not begin by inventing a new system. It would give the existing system a new formal interpretation: repairable -> exactly constitutable; obstructed -> failed exact-object constitution; provenance admissible -> legitimate route structure; refinement invariant -> presentation-independent exactness. The new work concerns the missing bridge between those concepts.

### 10. Work packages

1. **Whiteheadian reconstruction** — a formal philosophical paper distinguishing concrete regions from exact abstractions, routes of determination from terminal objects, numerical precision from exact constitution, equivalence from admissibility, abstraction from arbitrary omission, objective invariance from naive realism.
2. **Formal exactness calculus** — regional evidence states, admissibility structures, refinement relations, route equivalence, descent, exactness judgements, repair/obstruction certificates, kept finite/rational/linear initially.
3. **Provenance-sensitive admissibility** — common ancestry, statistical dependence, duplicated evidence, permissible derived evidence, prohibited corroboration, evidence identity, independence claims.
4. **Compositional assurance** — when exactness certificates compose across sequential pipelines, parallel sensors, shared interfaces, fused subsystems, refinement stages, evidence-append operations, and when composition fails.
5. **Verified certificate boundary** — schemas, emitters, independent checkers, digest binding, tamper tests, rational arithmetic, resource limits, reproducibility tests (much of this already exists and would be adapted, not rebuilt).
6. **Sensor-fusion evaluation** — comparing ordinary point estimates, confidence-based fusion, provenance-aware fusion, and proof-carrying exactness; the key question is not accuracy improvement but *which outputs conventional systems produce without being able to evidence that those outputs are legitimately constituted*.

### 11. Publication structure

Three papers: (1) philosophical foundations connecting extensive abstraction, non-pointal geometry, quotient construction, local-to-global constitution, and computational objecthood; (2) formal theory defining the calculus and proving soundness, completeness, exclusivity, refinement invariance, compositional results, and checker correctness; (3) applied assurance presenting the tracking adapter, provenance-sensitive admissibility, repairable/obstructed examples, independent checkers, tamper rejection, and performance/certificate-size results.

### 12. Repository structure (proposed, not yet built)

```text
proof-carrying-exactness/
├── README.md
├── PHILOSOPHICAL_FOUNDATIONS.md
├── FORMAL_MODEL.md
├── ADMISSIBILITY_SPEC.md
├── CERTIFICATE_SPEC.md
├── THREAT_MODEL.md
├── LIMITATIONS.md
├── rocq/ (RegionalEvidence.v, Admissibility.v, Refinement.v, RouteEquivalence.v,
│         ExactnessJudgement.v, RepairCertificate.v, ObstructionCertificate.v,
│         RationalCompleteness.v, ProvenanceAdmissibility.v, RefinementInvariance.v,
│         CompositionalExactness.v)
├── python/ (pce_format.py, pce_emitter.py, pce_verifier.py, provenance_checker.py,
│           diagnostic_renderer.py)
├── ocaml/ (pce_format.ml, pce_verifier.ml, exact_rational.ml)
├── adapters/ (tracking/, sensor_fusion/, generic_linear/)
├── demonstrations/ (exact_clean/, repairable/, provenance_rejected/, obstructed_cycle/,
│                    tampered_certificate/)
└── tests/ (test_certificate_parity.py, test_provenance.py, test_refinement_invariance.py,
           test_tampering.py, test_end_to_end.py)
```

"The project could also be developed as a semantic and documentation layer over your existing repositories rather than creating a fourth independent codebase immediately. That may be the better approach initially."

### 13. The minimum viable project

Five things: (1) define relative exactness formally; (2) reinterpret the linear repair-or-separator theorem (repair witnesses certify successful regional constitution, separator witnesses certify failed constitution); (3) connect provenance to admissible routes (duplicated ancestry can invalidate a claim of exact constitution without changing the numerical output); (4) two independent certificate checkers (reuse the existing Python/OCaml boundary); (5) demonstrate three distinct outcomes: `EXACT`, `OBSTRUCTED`, `INADMISSIBLE`.

That three-way distinction is likely the clearest immediate contribution — it avoids the false assumption that every failure is either inconsistency or uncertainty.

### 14. What the project should not become

Not a general history of point-free geometry (the history is necessary, but the contribution must be a formal assurance method). Not the most abstract possible mathematics first (no need to begin with higher categories, general topoi, or arbitrary non-linear descent — the finite rational theory is already strong because it is complete, executable, and independently checkable). Not a claim to certify reality itself (the system certifies constitution relative to an evidence boundary, a model, a provenance policy, a transformation structure, a correction space — it does not prove the world conforms perfectly to the model). Not treating Whitehead as ornamental (regions are primitive, points are outputs, routes matter, equivalence is constructed, exactness is higher-order, no terminal exact constituent is assumed). Not reducing the contribution to "better confidence" (a system can be highly confident in an output assembled from inadmissible or globally obstructed evidence).

### 15. The deepest research contribution

Conventional assurance asks "is this output correct?" Robustness asks "does this output remain stable under perturbation?" Provenance asks "where did this output come from?" Consistency checking asks "do the contributing data agree?" Proof-carrying exactness asks:

> **Do these regional determinations, transformations, and provenance relations legitimately constitute one exact object, and can that fact be independently verified?**

Compressed into one sentence:

> **Do not certify merely that a calculation was performed correctly. Certify that the object asserted by the calculation was legitimately constituted from the evidence.**

---

## Part 2: follow-up — what to build first

What needs to be made is a small assurance system that takes regional evidence and returns one of three independently checkable verdicts: `EXACT`, `OBSTRUCTED`, `INADMISSIBLE`. Most of the mathematical and verification machinery already exists; the job is to assemble it around this new semantic claim.

**1. The exactness judgement.** A formal spec defining each verdict: `EXACT` (evidence admissible, local determinations assemble globally, output invariant under permitted corrections/refinements; certificate includes `D u = r`); `OBSTRUCTED` (evidence admissible, but no permitted correction assembles the local determinations into the claimed global object; certificate includes `y^T D = 0, y^T r != 0`); `INADMISSIBLE` (evidence cannot legitimately enter the calculation — duplicated evidence, hidden common ancestry, invalid coordinate conversion, prohibited reuse, missing provenance, unsupported independence claim). First document: `PROOF_CARRYING_EXACTNESS_SPEC.md`, defining inputs, verdicts, certificate obligations, and non-claims.

**2. A unified evidence package** — one canonical input schema (`proof-carrying-exactness/input/v1`) binding claim, evidence, provenance, transformations, admissibility policy, and the regional `D`/`r` problem, digest-bound so the certificate proves something about exactly this package.

**3. A proof-carrying exactness certificate** — one envelope per verdict (`exactness/positive/v1` with input digest, admissibility policy digest, provenance verdict, transformation verdicts, `D`/`r`, repair witness `u`; `exactness/obstruction/v1` with `D`/`r`, separator `y`, its support, the implicated cycle/interface, `y^T r`; `exactness/inadmissible/v1` with the violated rule, implicated evidence/provenance edges, a machine-checkable explanation).

**4. One unified command** — `pce-assess case.json --out certificate.json`, running parse/validate -> bind digest -> check provenance -> check transformation admissibility -> construct/validate `D`/`r` -> attempt repair -> on failure construct separator -> emit exactly one verdict -> verify the emitted certificate -> fail closed on verification failure.

**5. An obstruction-capable demonstrator** — the most important missing technical artefact. The existing two-track, one-edge Stone Soup topology is necessarily repairable (`rank(D) = dim(C^1)`) and cannot exhibit the negative result. A new example needs a genuine cycle — a four-region cycle `R1 -> R2 -> R3 -> R4 -> R1` is sufficient, constructed so every local comparison looks plausible but the total cycle fails to close (`r1+r2+r3+r4 != 0`), with the separator identifying the cycle directly.

**6. A contrastive three-case evaluation** — Case A (exact: provenance-valid and globally repairable), Case B (inadmissible: same or similar numerical output, but two observations share prohibited ancestry), Case C (obstructed: provenance-valid, but the regional determinations do not assemble globally) — chosen so the numerical outputs look nearly identical across all three, showing this is not merely another estimator or confidence model.

**7. A human-readable diagnostic report** per assessment: claimed object, evidence boundary, admissibility result, constitution result, certificate, implicated components, and remediation (what would need to change for a different verdict).

**8. The Whiteheadian formal bridge** — a short document proving the reinterpretation is not merely new terminology, culminating in: `ConstitutesExact(D, r) <-> r in im(D)`, and `r not in im(D) <-> exists y in ker(D^T), y^T r != 0`.

**9. Formalisation work** — likely new Rocq objects: `AdmissibilityPolicy`, `RegionalEvidenceState`, `ExactnessClaim`, `ExactnessVerdict`, `Constitutes`, `PositiveExactnessCertificate`, `ObstructionExactnessCertificate`, `InadmissibilityCertificate`; theorem names such as `accepted_positive_implies_constitutes`, `accepted_obstruction_implies_not_constitutes`, `accepted_inadmissibility_implies_policy_violation`, `positive_and_obstruction_disjoint`, `admissibility_precedes_constitution`, `refinement_preserves_exactness_under_conditions`, `provenance_duplication_does_not_add_support`. Much of the underlying algebra already exists; the new work is largely semantic typing, integration, and connecting theorems to the certificate boundary.

**10. An assurance-boundary audit package** — packaging the method as an audit of one selected decision path from a real system (evidence/provenance map, transformation inventory, admissibility policy, regional compatibility model, exactness verdict, certificate, independent checker results, failure localisation, remediation recommendations, explicit non-claims), framed around "what does this output actually evidence, and where does the system cease to be able to justify it?"

**11. A concise live demonstration** — three `pce-assess` runs (clean/shared-ancestry/cyclic-obstruction) producing `EXACT`/`INADMISSIBLE`/`OBSTRUCTED` with both verifiers agreeing, plus one tampered-certificate run producing a digest-mismatch `REJECT`.

**What NOT to build**: another general-purpose sensor-fusion engine; another ML model; a Stone Soup replacement; a complete formalisation of all Whiteheadian geometry; a universal theory of exactness; a new theorem prover; a new programming language; a large visual dashboard; a fourth large repository built all at once.

**The smallest credible package**, restated: (1) `PROOF_CARRYING_EXACTNESS_SPEC.md`; (2) a unified input/certificate schema; (3) `pce-assess`; (4) an obstruction-capable cyclic demonstrator; (5) a three-case `EXACT`/`INADMISSIBLE`/`OBSTRUCTED` evaluation; (6) a paper proving the semantic connection to admissible regional constitution.

> The single most important thing to make: a demonstrator in which an ordinary system produces a precise-looking fused result, while this system distinguishes whether that result is exactly constituted, structurally obstructed, or evidentially inadmissible, and independently certifies the distinction. Without that, the project remains an interpretation. With that, it becomes a capability.
