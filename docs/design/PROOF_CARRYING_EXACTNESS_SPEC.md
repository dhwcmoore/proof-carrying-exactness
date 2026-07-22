# Proof-Carrying Exactness: Specification

## 1. Status and scope

**Status (2026-07-22): first architectural specification. No
production implementation exists yet.** This document is derived
directly from a successful untracked semantic spike
(`spike/pce_semantics.py`, `spike/cases/*.json`, not committed to this
repository) that exercised every claim below against small, exact
rational examples before this document was written — every formula in
§2 and the design-audit subsection of §7 quotes the spike's own actual
computed output, not a hand-derived or hoped-for value.

Explicitly, as of this document:

- No `docs/design/*` file describing the inherited proof
  infrastructure has been rewritten, and no `rocq/*.v`, `ocaml/*.ml`,
  or root-level `*.py` file has been modified. The inherited R1-R24
  and R21 machinery (`rocq/`, `ocaml/`, `r21_*.py`,
  `rational_linear_algebra.py`, `tracking_adapter_*.py`, and the tests
  and examples exercising them) remains exactly what it was when this
  repository was seeded: reference material and a reusable foundation,
  not yet adapted to this project's own vocabulary.
- No `pce_*.py` production module, certificate schema, or independent
  verifier exists. `spike/pce_semantics.py` is a throwaway
  demonstration script, not a generator or verifier in the sense this
  document defines them.
- The initial theory is deliberately restricted to the finite-
  dimensional, rational, linear case: `D`, `L`, `r`, `x` are all
  rational matrices/vectors of fixed finite dimension, and the claim
  map `L` is linear. Nonlinear claim maps, infinite-dimensional
  evidence spaces, and non-rational (e.g. real- or interval-valued)
  quantities are out of scope for this document and are not assumed
  to generalise trivially.
- "Exactness" is always relative to an explicit evidence boundary
  (`E`), an explicit admissibility policy (`A`), an explicit permitted-
  adjustment map (`D`), and an explicit claim map (`L`). This document
  does not define, and does not claim to define, exactness as an
  intrinsic property of a value in isolation from those four things.

## 2. Motivating distinction

The founding technical observation of this repository, established by
the spike, is:

    Repairable(D, r)  does NOT imply  Exact(D, r, L).

Concretely: the spike's `cases/exact_invariant.json` and
`cases/repairable_ambiguous.json` share the IDENTICAL

    D = [[-1, 1, 0],
         [ 0,-1, 1]]
    r = [3, 2]

(a three-track chain: `u2 - u1 = 3`, `u3 - u2 = 2`). Both are
repairable — `ker(D) = span{(1,1,1)}` is one-dimensional (the familiar
absolute-position gauge freedom already documented elsewhere in this
repository's inherited fixtures), and a particular repair is
`u = (-5, -2, 0)`.

For the claim map `L(u) = u3 - u1`, i.e. `L = [-1, 0, 1]`:

    L @ (1,1,1) = -1 + 0 + 1 = 0

so `L` annihilates the kernel. The spike verified this algebraically
(over the full computed kernel basis, not by sampling) and additionally
exhibited a factorisation witness `M = [1, 1]` with `M @ D = L` exactly
(`M @ D = [-1, 0, 1] = L`, checked by direct recomputation). The
claimed value `L @ u = 5` is therefore the SAME for every repair in the
fibre — verdict `EXACT`.

For the different claim map `L'(u) = u3`, i.e. `L' = [0, 0, 1]`:

    L' @ (1,1,1) = 1  (non-zero)

so `L'` does NOT annihilate the kernel. The spike confirmed no
factorisation `M` exists with `M @ D = L'` (solving `D^T m = L'`
directly fails), and exhibited two concrete repairs, `u = (-5,-2,0)`
and `u' = u + (1,1,1) = (-4,-1,1)`, both satisfying `D u = D u' = r`,
with `L' @ u = 0` and `L' @ u' = 1` — two DIFFERENT claimed values from
two equally valid repairs. Verdict `UNDERDETERMINED`.

The evidence is identical in both cases. The repairability verdict is
identical in both cases. Only the declared claim map differs, and it
alone determines whether the system has actually constituted the
claimed exact object or merely shown that SOME reconciliation exists.
This is the gap the R21 repair-or-separator dichotomy alone does not
express, and is the reason this project is not simply a renaming of
that existing result.

## 3. Core objects

    D in Q^(m x n)     permitted regional adjustment map
    r in Q^m           observed compatibility residue
    u in Q^n           a permitted global reconciliation ("repair")
    L in Q^(p x n)     claim map
    x in Q^p           claimed presentation-independent output
    A                  admissibility policy
    E, Pi, T           evidence, provenance, and declared transformations

The repair fibre:

    Sol(D, r) = { u in Q^n : D u = r }

`D`, `r`, and `L` are the objects the linear-algebra machinery
(inherited, unmodified: `r21_repair_or_separator.repair_or_separate`,
`rational_linear_algebra.{nullspace_over_Q, solve_over_Q, mat_vec,
mat_mat, transpose}`) actually operates on. `E`, `Pi`, `T`, and `A` are
the evidentiary layer this document adds on top — analogous to, but
not yet built from, `tracking_adapter_provenance.py`'s existing
ancestry-graph machinery in the inherited foundation, which this
project's own `INADMISSIBLE` verdict is expected to eventually reuse or
closely mirror rather than reinvent.

## 4. Relative exact constitution

The central definition:

    Exact_A(E, Pi, T, D, r, L, x)

holds exactly when:

1. the evidence package is admissible under `A`;
2. the repair fibre is non-empty;
3. the claim map is constant on the repair fibre;
4. its common value is `x`.

Formally:

    Admissible_A(E, Pi, T)
    and exists u, D u = r
    and forall u1, u2: (D u1 = r and D u2 = r) implies (L u1 = L u2 = x)

For linear `L`, the equivalent kernel form:

    Admissible_A
    and exists u, D u = r
    and L u = x
    and ker(D) subseteq ker(L)

And the certificate-oriented factorisation form, proved equivalent to
the kernel form in finite-dimensional linear algebra and used for the
production certificate (§7):

    Admissible_A
    and exists u, M:  D u = r  and  L u = x  and  L = M D

`ker(D) subseteq ker(L)` and `exists M, L = M D` are the SAME
mathematical fact stated two ways; §7's design-audit subsection records
why the certificate uses the second form.

## 5. The four verdicts

### `INADMISSIBLE`

    not Admissible_A(E, Pi, T)

The constitution calculus (§6, steps 4 onward) is never evaluated —
this is a hard gate, not merely an early-exit optimisation. Evidence
that fails this check must not acquire apparent warrant by
coincidentally passing a downstream algebraic test (a real risk: the
spike's `cases/inadmissible.json` shares an IDENTICAL, otherwise-EXACT
`D`/`r`/`L` with `cases/exact_invariant.json` — the numbers alone would
say `EXACT`; only the declared, violated provenance rule says
otherwise).

### `OBSTRUCTED`

    Admissible_A  and  r not in im(D)

Certificate (unchanged from the inherited R21 form):

    y^T D = 0   and   y^T r != 0

### `UNDERDETERMINED`

    Admissible_A  and  r in im(D)  and  ker(D) not subseteq ker(L)

Certificate:

    D u = r   and   D k = 0   and   L k != 0

### `EXACT`

    Admissible_A  and  r in im(D)  and  ker(D) subseteq ker(L)

Certificate:

    D u = r   and   L = M D   and   L u = x

## 6. Decision order

This order is semantic, not merely procedural — reordering it would
change what a verdict means, not just how fast it is computed:

    1. Validate structure and bind the input (evidence digest, policy digest).
    2. Check admissibility.
    3. If inadmissible, emit INADMISSIBLE and stop.
    4. Solve or separate D u = r (the inherited repair-or-separator solver).
    5. If separated, emit OBSTRUCTED.
    6. If repaired, test claim invariance (kernel basis for discovery;
       see §7's design audit for why the CERTIFICATE uses factorisation
       instead).
    7. If a gauge direction changes the claim, emit UNDERDETERMINED.
    8. Otherwise emit EXACT.
    9. Verify the emitted certificate before release.

Step 3's hard stop is the load-bearing property: an admissibility
failure is never "overridden" by the evidence coincidentally being
numerically coherent, matching this repository's own inherited
governing distinction between R21's repairability question and
`tracking_adapter_provenance.py`'s separate evidentiary-admissibility
question (that file's own docstring: "R21 is never used to detect data
incest").

## 7. Certificate obligations

Every certificate is minimal: it supplies exactly the witnesses an
independent verifier needs to recompute the relevant equalities, never
more, and never a free-text substitute for a checkable value.

### Exact certificate

Required fields: evidence digest; policy digest; `D`, `r`, `L`, `x`;
repair witness `u`; factorisation witness `M`; the admissibility
result; schema and checker versions.

Checks: `D u = r`, `L = M D`, `L u = x`.

### Underdetermined certificate

Required fields: `D`, `r`, `L`; repair witness `u`; gauge witness `k`;
base value `L u`; the admissibility result.

Checks: `D u = r`, `D k = 0`, `L k != 0`.

The alternate repair `u' = u + k` and its claimed value `L u'` are NOT
independent certificate fields — they are derivable by the verifier
(`D u' = D u + D k = r + 0 = r`; `L u' = L u + L k != L u` since
`L k != 0`) and should appear only in the human-readable diagnostic,
not as machine-checked primitives.

### Obstruction certificate

Unchanged from the inherited R21 form: `y^T D = 0`, `y^T r != 0`. Claim-
map metadata may be attached to identify which attempted object was
blocked, but is not part of the obstruction check itself — obstruction
concerns solvability of `D u = r`, a question prior to and independent
of claim invariance.

### Inadmissibility certificate

Required fields: policy rule identifier; implicated evidence
identifiers; implicated provenance or transformation edges; evidence
digest; policy digest; a witness check specific to the violated rule
(e.g., for shared ancestry: the common root ancestor, computed, not
merely asserted — matching the spike's own `check_admissibility`,
which reports the actual shared root, not just "yes/no").

This certificate must never be a free-text reason. A rule identifier
plus a recomputable witness is required, the same discipline
`tracking_adapter_provenance.py`'s `ProvenanceResult` already applies
(`UNDECLARED_SHARED_ANCESTRY` plus the actual shared `source_record`
set, not a prose explanation alone).

### Design audit: why the production positive certificate uses `M`, not a supplied kernel basis

`ker(D) subseteq ker(L)` and `exists M, L = M D` are mathematically
equivalent, but they impose different obligations on a checker.

A kernel-basis certificate would need to supply vectors `k_1, ..., k_j`
and have the verifier check `D k_i = 0` and `L k_i = 0` for each — but
that only proves each SUPPLIED vector lies in `ker(D) cap ker(L)`. To
conclude `ker(D) subseteq ker(L)` in general, the verifier would
ADDITIONALLY have to confirm the supplied vectors actually SPAN the
entire kernel of `D` — a completeness obligation with no shortcut
weaker than recomputing the kernel itself (e.g. via
`nullspace_over_Q`), at which point the "independent" verifier is no
longer just checking a witness, it is re-deriving one from scratch and
comparing bases, a much heavier and more error-prone check (basis
comparison up to change of basis, not a single matrix equality).

The factorisation form sidesteps this entirely: `L = M D` is a single
matrix equality, checkable by one matrix multiplication and one
elementwise comparison, with no separate spanning/completeness
obligation — `M` is not claimed to be anything other than a matrix
that happens to satisfy this equation, and the equation itself is the
complete proof that `ker(D) subseteq ker(L)` (if `D v = 0` then
`L v = M D v = M 0 = 0`).

This was checked, not merely asserted, against the spike's own two
contrasting cases (§2): for `exact_invariant.json` (`D`, `L` with
`ker(D) subseteq ker(L)`), solving `D^T m = L^T` directly succeeded,
returning `M = [1, 1]`, and `M @ D` recomputed to exactly `L`. For
`repairable_ambiguous.json` (identical `D`, different `L'` with
`ker(D) not subseteq ker(L')`), the identical solve attempt (`D^T m =
L'^T`) failed outright — confirming the two formulations agree exactly
on both the positive and negative case, not merely on the positive one.

The GENERATOR may still use `nullspace_over_Q` freely for discovery and
for constructing the human-readable `UNDERDETERMINED` diagnostic (the
gauge witness `k` used in that certificate is exactly a kernel-basis
vector) — only the `EXACT` certificate's own witness is required to be
the factorisation `M`, not a kernel basis.

## 8. Soundness theorems (stated, not yet proved)

    VerifyExact(C) = ACCEPT  implies  Exact_A(C)

    VerifyUnderdetermined(C) = ACCEPT
        implies  Repairable(D, r)  and  not ClaimInvariant(D, L)

    VerifyObstructed(C) = ACCEPT  implies  r not in im(D)

    VerifyInadmissible(C) = ACCEPT  implies  not Admissible_A

Also required: pairwise verdict exclusivity under well-formed input and
a deterministic admissibility policy — no well-formed instance may
accept certificates for two different verdicts. None of these four
theorems, nor exclusivity, has been proved (in Rocq or otherwise) as of
this document; they are stated here as the target for the next phase
of work, in the same spirit as R21's own soundness theorem
(`compute_repair_or_separator_correct`) that they extend.

## 9. Completeness boundary

For a well-formed finite rational instance with decidable
admissibility, the intended classification is complete and mutually
exclusive:

    INADMISSIBLE  or  OBSTRUCTED  or  UNDERDETERMINED  or  EXACT

The algebraic partition after admissibility is:

    r not in im(D)
    or (r in im(D) and ker(D) not subseteq ker(L))
    or (r in im(D) and ker(D) subseteq ker(L))

This is the intended four-way classification theorem; like §8, it is
stated here, not yet proved. It follows the same shape as R21's own
completeness theorem (`compute_repair_or_separator_correct`'s
dichotomy) with one additional binary split (`ker(D) subseteq ker(L)`
or not) inserted after the repairable branch, gated by admissibility
before either branch is reached at all.

## 10. Whiteheadian interpretation

- The repair fibre `Sol(D, r)` is the plurality of admissible routes of
  reconciliation.
- Gauge differences (`ker(D)`) represent variations that do not alter
  regional compatibility.
- The claim map `L` selects the feature asserted as the exact object.
- Exactness occurs when that feature is invariant across the whole
  fibre.
- Underdetermination occurs when a coherent reconciliation exists but
  no presentation-independent claimed value has been constituted.
- Obstruction occurs when no coherent global reconciliation exists at
  all.
- Inadmissibility occurs when the purported routes were not legitimate
  routes of determination in the first place.

> An exact object is not a selected repair. It is a claim invariant
> over the entire admissible repair fibre.

## 11. Non-claims

This specification does not claim, and no implementation of it should
claim, that the system proves:

- correspondence with the external world;
- correctness of the admissibility policy itself (only that the
  policy, whatever it is, was applied and checked consistently);
- sensor accuracy;
- statistical independence, unless separately evidenced by a
  provenance/ancestry check specific to that claim (matching
  `tracking_adapter_provenance.py`'s own explicit non-claim: a
  `PROVENANCE ACCEPT` verdict means no shared sensor-record ancestor,
  not statistical independence of estimators);
- uniqueness of the full repair state `u` (only invariance of `L u`
  across the fibre is claimed for `EXACT`);
- universal exactness independent of the declared model, evidence
  boundary, and claim map — exactness is always relative to `A`, `D`,
  and `L` as declared, never absolute;
- completeness beyond the finite-dimensional rational linear setting
  stated in §1.

The precise relative claim this specification licenses:

> Under this evidence boundary, admissibility policy, regional
> adjustment model, and claim map, the claimed value is or is not
> invariant across every permitted global reconciliation.
