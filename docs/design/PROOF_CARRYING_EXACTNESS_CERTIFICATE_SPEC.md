# Proof-Carrying Exactness: Certificate Specification

## 1. Status

**Status (2026-07-22): architecture only. No production certificate
implementation exists.** This document follows a successful, 23-check
certificate feasibility spike (`spike_certificates/`, untracked and
non-normative -- kept untracked while this document is checked line by
line against it, per this repository's own established discipline).
The prior semantic spike (`spike/`, also untracked) established the
underlying `EXACT`/`UNDERDETERMINED`/`OBSTRUCTED`/`INADMISSIBLE`
distinction (`docs/design/PROOF_CARRYING_EXACTNESS_SPEC.md`); this
document specifies the CERTIFICATE boundary for that distinction --
what a generator may compute freely, and the small, independently
checkable witness a verifier accepts instead of repeating that
computation.

The inherited R21 certificate system (`r21_certificate_format.py`,
`r21_certificate_emitter.py`, `r21_certificate_checker.py`,
`rational_linear_algebra.py`) is reference machinery: reused directly
for canonical rational parsing and the `D`/`r` component of the digest,
never modified, and never itself the source of a soundness claim this
document makes on its own behalf.

This document defines the PROPOSED production boundary. No `pce_*.py`
production module exists yet; `spike_certificates/pce_certificate_
spike.py` and `verifier.py` are throwaway demonstrations, not the
production generator/verifier this specification describes, though
the production verifier should differ from the spike's only in
robustness (resource limits, more careful error messages), not in
which equations it checks.

## 2. Certificate objective

The certificate generator may perform expensive discovery:

- solve `D u = r`;
- compute nullspaces;
- find factorisations;
- search provenance graphs;
- construct separators;
- construct reachability cuts proving non-reachability (SS10).

The verifier must not repeat discovery. It checks a supplied witness
using local, exact operations.

    untrusted discovery + small, independently checkable witness

This is the same architectural principle R21's own generator/checker
split already establishes (`r21_repair_or_separator.py` is untrusted;
`r21_certificate_checker.py` recomputes `D b` or `D^T y`/`y . r`
directly); this document extends it to four verdicts and a claim map,
not a new principle.

## 3. Common envelope

One closed top-level schema for all four verdicts:

```json
{
  "schema": "proof-carrying-exactness/certificate/v1",
  "verdict": "EXACT",
  "input_digest": "...",
  "policy_digest": "...",
  "instance": {},
  "witness": {}
}
```

(The spike used `proof-carrying-exactness/certificate-spike/v1` as its
own schema tag, deliberately distinct, so a spike-produced certificate
can never be mistaken for a production one; the production schema
above is a NEW, separate tag.)

Rules, all confirmed by the spike's own `verify_certificate` (`grep`-
auditable: `validate_closed_keys` is called on the envelope, the
instance, and the witness, in that order, before any arithmetic runs):

- unknown top-level keys are rejected (`validate_closed_keys(cert,
  ENVELOPE_KEYS, ...)`);
- duplicate JSON keys are rejected (inherited from `r21_certificate_
  format.strict_json_load`'s `reject_duplicate_keys` object-pairs
  hook -- the spike's own harness passes Python dicts directly and so
  did not exercise this path itself; the production verifier's file-
  loading entry point must use `strict_json_load`, not plain
  `json.load`, to inherit it);
- missing required top-level keys are rejected;
- verdict-specific witness schemas are CLOSED (`WITNESS_KEYS[verdict]`,
  one frozenset per verdict, pairwise non-identical);
- the declared `verdict` field selects EXACTLY one witness variant --
  there is no witness field valid under two different verdicts'
  closed sets simultaneously except `repair_witness`, which appears in
  both `EXACT` and `UNDERDETERMINED` but is never sufficient alone
  under either (both also require at least one further field);
- values are parsed (`parse_rational`/`parse_vector`/`parse_matrix`,
  inherited, unmodified) before any arithmetic is attempted;
- malformed input fails closed -- `verify_certificate`'s own top-level
  `try/except Exception` converts ANY unexpected error, including a
  malformed structure this document did not anticipate, into a
  rejection, never an unhandled crash a caller could mistake for "no
  verdict" rather than REJECT (the same discipline `tracking_adapter_
  verifier.verify_snapshot_doc` and `r21_certificate_checker.check_
  certificate` already establish).

## 4. Digest model

**Revised (hardening pass, 2026-07-22).** An earlier draft of this
section recommended folding `provenance` into `policy_digest`. That
recommendation was ITSELF wrong, corrected before any production code
was written from it: provenance is a fact about the evidence instance
(it describes what evidence exists and how it is related), while
policy determines how that provenance is JUDGED (which pairs must be
independent, under which rule). The same policy should be reusable
across many different evidence packages; folding provenance into the
policy digest would mean changing the evidence (e.g. adding one more
provenance edge) silently produces what LOOKS LIKE a new policy, which
is the wrong entity to blame for the change. The corrected boundary,
now implemented and verified in `spike_certificates/`:

### Input digest

Binds everything constitutive of the evidence instance -- both
algebraic and evidentiary:

- `D`, `r` (rendered as an explicit `"D:absent"`/`"r:absent"` marker,
  not silently omitted, for `INADMISSIBLE`, which forbids them
  entirely -- SS11);
- `L`, when present (forbidden, not merely absent, for `OBSTRUCTED`/
  `INADMISSIBLE` -- SS8, SS9);
- the provenance graph: vertices AND edges (`provenance.vertices`,
  `provenance.edges`), sorted before hashing for a canonical, order-
  independent serialisation;
- evidence-to-row alignment (`row_evidence_ids`);
- claim metadata (`claim_metadata`, optional, `OBSTRUCTED`-only in the
  current schema -- a descriptive label, still digest-bound so it
  cannot be swapped post hoc even though it is never checked
  mathematically);
- transformation metadata used by the assessment, when a future
  revision of this project's evidence model introduces declared
  transformations distinct from `L` itself (not present in the spike;
  flagged here so the digest model does not need revisiting when that
  happens).

Claimed value `x` remains part of the WITNESS, not the input digest --
it is a claim the certificate makes and the verifier checks against
the instance, not part of the evidence boundary the instance itself
fixes. Confirmed by inspection: `certificate_types.compute_input_
digest`'s own signature (`D, r, L, provenance, row_evidence_ids,
claim_metadata`) never takes `x` as an argument.

### Policy digest

Binds ONLY the judgement rules, reusable across many evidence
packages:

- rule identifiers (`SUPPORTED_RULE_IDS`, currently one member,
  `independent_rows_no_ancestry_relation` -- see SS9);
- independent-row declarations (`policy.independent_pairs`);
- policy version (`policy.policy_version`, matching `tracking_adapter_
  provenance.py`'s existing convention, e.g.
  `"tracking-adapter-independence-policy/v1"`-shaped strings -- now a
  required field, confirmed present in every one of the spike's five
  case files);
- any rule parameters (none exist for the one currently supported
  rule, which takes no parameters beyond the pair itself).

**The provenance graph is deliberately NOT part of `policy_digest`.**
Confirmed directly: `compute_policy_digest` takes only a `policy` dict
and never reads `provenance` at all; `compute_input_digest` is the one
function that reads `provenance`. A dedicated test (`spike_
certificates/pce_certificate_spike.py`'s "provenance-edge mutation
after digest creation is caught by input_digest" case) confirms
mutating `instance.provenance.edges` after certificate construction is
caught -- by `input_digest`, specifically, not `policy_digest`.

### Domain separation

Both digest functions prepend an explicit domain tag before hashing,
so the same canonical bytes can never be confused across digest
domains:

    pce-input-v1  || canonical_input_bytes
    pce-policy-v1 || canonical_policy_bytes

Implemented and verified directly: a dedicated spike test hashes the
SAME literal payload string under both domain prefixes and confirms
the two resulting digests differ, and the "swapped input_digest and
policy_digest values" tamper test confirms a certificate with its two
digest fields exchanged is rejected (both digests are independently
recomputed and compared against the correct field, so a swap is caught
regardless of domain separation in that specific case -- but domain
separation is what guarantees no ACCIDENTAL collision could ever make
a swap, or a genuinely different canonical payload, verify by chance).

Rational and matrix encoding is reused from R21 outright (`parse_
rational`, `parse_vector`, `parse_matrix`, and `canonical_input_
digest`'s own canonical line format for `D`/`r`); the two genuine
extensions are `L`'s own canonical serialisation (never part of `roc-
input/v1`) and the provenance/row-evidence/claim-metadata
canonicalisation this document's own corrected boundary requires.

## 5. Rational and matrix representation

Carried forward from the inherited R21 format, unchanged:

- integers are exact rationals (`"3"`, not `"3.0"`);
- fractions in canonical reduced form (`str(Fraction(...))`, e.g.
  `"1/5"`, never `"2/10"`);
- positive denominators (`parse_rational` rejects a negative or zero
  denominator string outright);
- no floating-point values anywhere;
- rectangular matrices only (`parse_matrix` rejects a ragged matrix);
- explicit dimension compatibility (`r`'s length must match `D`'s row
  count; `M`'s shape must match `D`'s row count and `L`'s row count;
  `u`/`k`'s length must match `D`'s column count);
- empty dimensions: a `0`-row or `0`-column matrix is not exercised by
  the spike's own four cases and is not given a defined meaning by this
  document -- treated as forbidden until a concrete need justifies
  defining it, rather than left as an unspecified edge case a future
  implementation could interpret inconsistently on the generator and
  verifier sides;
- maximum dimensions and rational-string lengths: reuse `r21_
  certificate_format.MAX_DIMENSION`, `MAX_TOTAL_ENTRIES`, `MAX_
  RATIONAL_CHARS`, `MAX_INPUT_BYTES` directly, rather than inventing
  parallel limits this project would then have to keep in sync;
- exact equality throughout -- every check in SS6-9 below is a literal
  equality or inequality of exactly-parsed `Fraction` values or vectors
  of them, never a tolerance-based or floating-point comparison.

Certificate verification must never depend on a decimal approximation
at any stage.

## 6. EXACT

### Semantic claim

The evidence is admissible, the repair fibre is non-empty, and `L` is
constant over that fibre.

### Witness

    u, M, x, admissibility_witness

### Required checks

    D u = r
    M D = L
    M r = x

From `M D = L`, every `k` in `ker(D)` satisfies `L k = M D k = 0`,
so `L` is constant on `Sol(D, r) = u + ker(D)` -- the algebraic content
of `EXACT` follows from these three equalities alone, with no kernel
computation anywhere in the verifier.

### Minimality note and the normative check

`L u = x` and `M r = x` are algebraically equivalent GIVEN `M D = L`
and `D u = r` (`L u = M D u = M r`), so the specification adopts:

    NORMATIVE: D u = r,  M D = L,  M r = x
    PERMITTED, redundant: L u = x

`M r = x` is preferred as normative because it computes the claimed
value directly from the residue `r` alone, without needing `u` for
that specific step -- cleanly separating what each witness proves:
`u` proves the repair fibre is non-empty; `M` proves claim invariance;
`M r` computes the invariant value directly. The spike's own `verifier.
_verify_exact` checks BOTH equalities (`M @ r == x` and, in addition,
`L @ u == x` as a redundant consistency confirmation) and confirmed
directly, on the chain example, that both agree (`M = [[1, 1]]`,
`r = (3, 2)`, `M @ r = (5,)`, matching `L @ u = (5,)` for the
independently computed repair `u = (-5, -2, 0)`) -- this document's
recommendation is therefore checked, not merely argued algebraically.
A production verifier MAY keep both checks (as the spike does) or drop
the redundant one; either is sound, since the redundant check can only
ever additionally REJECT (if the two ever disagreed, that would itself
indicate a certificate-construction bug), never additionally ACCEPT
something the normative check alone would have rejected.

### Required dimensions

Given `D` in `Q^(m x n)` and `L` in `Q^(p x n)`:

    u in Q^n,  r in Q^m,  M in Q^(p x m),  x in Q^p

### Admissibility binding

Per SS14, `EXACT` additionally requires `admissibility_witness` (SS10)
and its reachability-cut checks to pass BEFORE the three equalities
above are even evaluated -- confirmed directly in the spike
(`_verify_exact` calls `_verify_admissibility_cuts` first and returns
early on failure).

## 7. UNDERDETERMINED

### Semantic claim

The instance is repairable, but the claimed value is not invariant
over the repair fibre.

### Witness

    u, k, admissibility_witness

### Required checks

    D u = r
    D k = 0
    L k != 0

The verifier DERIVES, but does not require as a separate certified
input:

    u' = u + k
    D u' = D u + D k = r + 0 = r
    L u' = L u + L k != L u   (since L k != 0)

Only `u` and `k` are primitive machine witnesses; `u'`, `L u`, and
`L u'` are recomputed by the verifier purely to populate the human-
readable diagnostic (SS "Diagnostic fields" below) and, in the spike,
as an internal `assert` -- confirmed directly: `verifier._verify_
underdetermined` derives `u'` and asserts `D u' == r` and `L u' != L u`
AFTER the three primitive checks already passed, never as a substitute
for them.

### Diagnostic fields

The human-readable report may display `u`, `u'`, `L u`, `L u'`, `L k`
-- confirmed directly in the spike's own printed output for the chain
example: base repair `(-5, -2, 0)`, alternate repair `(-4, -1, 1)`,
base claim `(0)`, alternate claim `(1)`, claim difference `(1)`.

### Vector inequality

For vector-valued claims (`p > 1`), `L k != 0` means AT LEAST ONE
component of the vector `L k` is non-zero (`rational_linear_algebra.
is_zero` returning `False`, i.e. `not all(v == 0 for v in L k)`) --
not an undefined generic vector inequality. The spike's own claim maps
happen to have `p = 1` throughout, so this clause is stated here as a
specification requirement for the general `p > 1` case, not something
the spike's own four cases exercised.

### Admissibility binding

Same as `EXACT` (SS6's admissibility-binding note applies identically;
confirmed directly in `verifier._verify_underdetermined`).

## 8. OBSTRUCTED

### Semantic claim

The admissible regional system has no repair: `r` is not in `im(D)`.

### Witness

    y, admissibility_witness

(`attempted_claim_metadata` may also be present, per SS3/SS4 -- purely
descriptive, digest-bound, never checked mathematically.)

### Required checks

    y^T D = 0
    y^T r != 0

Reused, unchanged, from the inherited R21 separator semantics
(`r21_repair_or_separator.repair_or_separate`'s own `RESULT_SEPARATOR`
branch); the spike's own `verifier._verify_obstructed` computes
`y^T D` via `row_vec_mat(y, D)` and `y . r` via `dot(y, r)`, both
imported directly from `rational_linear_algebra.py`, unmodified.

### Claim-map boundary

The obstruction test does NOT require `L`. The system is blocked before
any claim-invariance question can arise -- the spike's own `instance.L`
is `None` for the `obstructed.json` case, and `_verify_obstructed`
never reads `L` at all. `attempted_claim_metadata`, when present,
identifies which attempted object was being assessed for diagnostic
purposes only; it is not, and must never be presented as, part of the
mathematical proof that `r` is not in `im(D)`.

### Admissibility binding

Same mechanism as `EXACT`/`UNDERDETERMINED` (confirmed directly in
`verifier._verify_obstructed`), even though `OBSTRUCTED`'s own
mathematical content (SS "Required checks" above) does not itself
depend on admissibility in any way -- the binding exists so that an
`OBSTRUCTED` certificate cannot be presented for an instance that was
never actually checked for admissibility at all (SS14).

## 9. INADMISSIBLE

### Initial normative rule

    independent_rows_no_ancestry_relation

Renamed from an earlier, overclaiming `independent_rows_no_shared_
ancestry`: the witness this rule verifies is ONE DIRECTED path between
two implicated rows (`e1` reaches `e2`, or `e2` reaches `e1`) -- an
ANCESTRY RELATION, not the strictly broader claim that two rows share
a common ancestor via two separately converging paths. A later,
genuinely broader rule, `independent_rows_no_common_ancestor`, would
need a different witness shape entirely (one common ancestor identifier
plus two independently verified paths, one from each implicated row to
that ancestor) and is explicitly NOT attempted by this specification or
the spike it is audited against.

The policy identifies a pair of evidence rows required to be
provenance-independent (`policy.independent_pairs`, a list of
`[left, right]` pairs).

### Witness

    rule_id, left_evidence, right_evidence, direction, ancestry_path

`direction` is one of `left_to_right` (`left_evidence` is shown to be a
transitive descendant of `right_evidence`, i.e. `ancestry_path` starts
at `left_evidence` and ends at `right_evidence`, each consecutive pair
a committed `[descendant, ancestor]` edge in that exact order) or
`right_to_left` (the same claim with the two endpoints exchanged).

### Required checks

The verifier confirms, in order (all confirmed directly against the
spike's own `verifier._verify_inadmissible`):

1. `rule_id` is a recognised rule (`SUPPORTED_RULE_IDS`);
2. `direction` is one of the two recognised values;
3. `ancestry_path` has at least 2 entries;
4. `ancestry_path`'s two endpoints match `left_evidence`/`right_
   evidence`, ordered according to the declared `direction`;
5. every consecutive pair `(path[i], path[i+1])` exists in the
   committed, DIRECTED provenance graph (`input_digest`-bound, per
   SS4's corrected boundary) in EXACTLY that order -- not reversed,
   since a directed `[descendant, ancestor]` edge does not license
   traversing it backwards as evidence of the opposite ancestry
   relation;
6. the policy (also `policy_digest`-bound) declares `{left_evidence,
   right_evidence}` as a pair required to be independent.

Confirmed directly on the spike's own worked example: `left_evidence =
row-0`, `right_evidence = row-1`, committed edges `[["row-1",
"derived-intermediate"], ["derived-intermediate", "row-0"]]` (row-1
derived from an intermediate step itself derived from row-0), direction
`right_to_left`, path `["row-1", "derived-intermediate", "row-0"]` --
`row-0` is a genuine, directly verified ancestor of `row-1`, not a
sibling sharing some third, unshown common ancestor.

The verdict is then `not Admissible_A`.

### Explicit limitation

This first rule does not yet certify: statistical dependence; general
common ancestry (two rows converging on a shared ancestor via separate
paths, neither being the other's own ancestor); probabilistic
correlation; semantic duplication; invalid transformations; missing
provenance. Each of those requires its own separate rule identifier and
witness schema, added to `SUPPORTED_RULE_IDS` one at a time, each with
its own spike, exactly as this one rule was.

## 10. Admissibility witness for the algebraic verdicts

**Revised (hardening pass, 2026-07-22).** An earlier draft of this
section specified a component-labelling witness. That witness was
SOUND -- a certified pair could never actually share an ancestry
relation -- but INCOMPLETE: it proves the two evidence items lie in
different WEAKLY connected components, which is strictly stronger than
"no directed path connects them either way". Counterexample, found
before any production code was written from the earlier draft:

    a <- c -> b

There is no directed path `a ⇝ b` or `b ⇝ a` -- `independent_rows_no_
ancestry_relation` should ACCEPT this pair as admissible -- but `a` and
`b` share one weakly connected component (via `c`), so a labelling
witness could never certify it, wrongly forcing `INADMISSIBLE` (or no
verdict at all) on a genuinely admissible instance. This is a real
completeness gap, not a hypothetical one: the initial ancestry rule is
supposed to classify every finite rational instance, and a common-
ancestor shape is an ordinary, unremarkable provenance pattern (e.g.
two sensor readings both calibrated from one shared reference
measurement, without either reading being derived from the other).

### Reachability-cut witness

Per `EXACT`/`UNDERDETERMINED`/`OBSTRUCTED`, `admissibility_witness` now
carries, for every policy-declared independent pair `(left, right)`, a
PAIR of cuts:

    {
      "cuts": [
        {
          "pair": [left, right],
          "left_not_reaches_right": [<vertex>, ...],
          "right_not_reaches_left": [<vertex>, ...]
        },
        ...
      ]
    }

A cut `S` proving `left` cannot reach `right` must satisfy:

    left in S
    right not in S
    forall (u, v) in edges: u in S implies v in S      (forward closure)

If such an `S` exists, no directed path can ever leave `S`, so no
directed path from `left` reaches `right` -- and this is COMPLETE, not
merely sound: whenever `right` really is unreachable from `left`, the
generator can always choose `S` to be exactly the set of vertices
reachable from `left` (which is, by construction, forward-closed, and
excludes `right` precisely because `right` is unreachable). Symmetric
for `right_not_reaches_left`. On the counterexample above: reachable-
from-`a` is `{a}` (no outgoing edges), reachable-from-`b` is `{b}` --
both valid, minimal cuts, confirmed directly in the spike (`cases/
exact_common_ancestor.json`, `EXACT (common ancestor a<-c->b, no
ancestry relation): accepted`).

### Required checks (per cut, no search)

1. no duplicate vertex identifiers within the supplied set;
2. every supplied vertex identifier is a known provenance vertex
   (`provenance.vertices`);
3. the set contains the required "reaches-from" endpoint;
4. the set excludes the opposite endpoint;
5. forward closure: for every committed edge `(u, v)`, if `u` is in the
   set, `v` must be too.

All five are local: membership tests and one pass over the committed
edge list, exactly the same non-search discipline as every other
verifier-side check in this document. Confirmed directly by the
spike's own tamper battery: a direct edge `a -> b` and a longer path
`a -> c -> b` both defeat a falsely claimed cut (closure fails at the
first edge that would force the excluded endpoint into the set); a cut
omitting the required vertex itself is rejected (check 3); a cut
improperly including the excluded endpoint is rejected (check 4).

This mechanism and `INADMISSIBLE`'s own explicit-path witness (SS9) are
the positive and negative sides of the SAME underlying connectivity
fact (reachability, not weak connectivity), verified via two DIFFERENT,
independently checkable witness shapes -- deliberately not unified into
one mechanism, since a positive non-reachability proof (a cut) and a
negative reachability proof (a path) have genuinely different
verification shapes, and conflating them would make either check
harder to audit in isolation.

The (now superseded) component-labelling witness MAY still be offered
as an OPTIONAL, additional, stronger certificate in a future revision
(it proves something strictly stronger -- full disconnection, not
merely non-reachability in one specific rule's sense -- which some
callers might want for other purposes), but it must never again be the
ONLY normative admissibility witness, since it cannot certify every
admissible instance the ancestry rule itself is supposed to accept.

## 11. Closed witness variants

```text
EXACT:
  repair_witness
  factorisation_witness
  claimed_value
  admissibility_witness

UNDERDETERMINED:
  repair_witness
  gauge_witness
  admissibility_witness

OBSTRUCTED:
  separator
  admissibility_witness
  attempted_claim_metadata            (optional)

INADMISSIBLE:
  rule_id
  left_evidence
  right_evidence
  direction
  ancestry_path
```

A witness carrying keys belonging to another verdict is rejected --
confirmed directly by all 5 of the spike's own cross-verdict
substitution tests (an `EXACT` witness presented as `OBSTRUCTED`; an
obstruction witness presented as `EXACT`; a repair witness presented as
`UNDERDETERMINED` without a gauge direction; an inadmissibility path
presented as an obstruction; an `EXACT` certificate missing its
factorisation witness).

### Instance schema: verdict-specific, inside one common envelope

**Implemented (hardening pass, 2026-07-22).** An earlier draft of this
document recommended, but did not implement, closed, verdict-specific
instance schemas. This is now implemented and verified:

    EXACT / UNDERDETERMINED required: D, r, L, provenance, policy, row_evidence_ids
    OBSTRUCTED required:               D, r,    provenance, policy, row_evidence_ids
    OBSTRUCTED optional:               claim_metadata
    INADMISSIBLE required:                      provenance, policy, row_evidence_ids

`D`/`r`/`L` are entirely FORBIDDEN (not merely absent or null) for
`INADMISSIBLE` -- confirmed by a dedicated tamper test ("extra instance
field (D) rejected under INADMISSIBLE"); `L` is forbidden for
`OBSTRUCTED` (test: "extra instance field (L) rejected under
OBSTRUCTED"); `claim_metadata` is forbidden for `EXACT`/
`UNDERDETERMINED` (tests: "extra instance field (claim_metadata)
rejected under EXACT"/"...under UNDERDETERMINED"). `provenance` and
`policy` are each themselves closed sub-schemas (`PROVENANCE_KEYS =
{vertices, edges}`, `POLICY_KEYS = {independent_pairs, policy_
version}`), so an extra or missing field inside either is also
rejected, not merely at the top level.

## 12. Verification API

    verify_certificate(certificate_bytes) -> ACCEPT | REJECT

1. parse strictly (`strict_json_load`, duplicate-key rejection, size
   limit before parsing);
2. validate the envelope (closed keys, schema tag, recognised verdict);
3. select the closed, verdict-specific witness (and, per SS11's
   correction, instance) schema;
4. recompute `input_digest` and `policy_digest` (the latter now
   covering `provenance` too, per SS4's correction);
5. validate dimensions and resource limits (SS5);
6. perform only the verdict-specific local checks (SS6-10);
7. return one final verdict -- ACCEPT only if every check above
   passed, REJECT (with reasons) otherwise.

No exception may escape step 1-6 uncaught; the spike's own `verify_
certificate` wraps the entire body in `try/except Exception`, converting
any unanticipated failure into `REJECT`, confirmed directly (this is
exactly the fail-closed discipline `r21_certificate_checker.check_
certificate` and `tracking_adapter_verifier.verify_snapshot_doc`
already establish, reused here rather than reinvented).

## 13. Generator and verifier separation

| Operation                          | Generator |  Verifier |
| ----------------------------------- | --------: | --------: |
| Solve `D u = r`                     | permitted | forbidden |
| Compute `ker(D)`                    | permitted | forbidden |
| Find `M`                            | permitted | forbidden |
| Find separator `y`                  | permitted | forbidden |
| Search provenance graph (path)      | permitted | forbidden |
| Search provenance graph (reachability cut) | permitted | forbidden |
| Check `D u = r`                     | permitted |  required |
| Check `M D = L`                     | permitted |  required |
| Check `M r = x`                     | permitted |  required |
| Check `D k = 0`                     | permitted |  required |
| Check `L k != 0`                    | permitted |  required |
| Check `y^T D = 0`                   | permitted |  required |
| Check `y^T r != 0`                  | permitted |  required |
| Validate supplied path edges (directed, simple) | permitted |  required |
| Validate supplied reachability cut (membership + closure) | permitted |  required |
| Recompute digests (domain-separated)   | permitted |  required |

Confirmed, not merely asserted: `grep -nE "^from|^import" verifier.py`
lists only `dataclasses`, `fractions`, `typing`, `certificate_types`,
`r21_certificate_format` (strict parsing only), and `rational_linear_
algebra.{dot, is_zero, mat_mat, mat_vec, row_vec_mat}` (pure products,
never `nullspace_over_Q`/`solve_over_Q`) -- and `pce_certificate_spike.
py` (the generator) is the only spike file that imports `r21_repair_or_
separator` at all.

## 14. Soundness obligations

    VerifyExact(C) = ACCEPT
        implies Sol(D, r) != {} and forall u1, u2 in Sol(D, r): L u1 = L u2 = x

    VerifyUnder(C) = ACCEPT
        implies there exist two valid repairs with different claims

    VerifyObstruction(C) = ACCEPT
        implies r not in im(D)

    VerifyInadmissible(C) = ACCEPT
        implies the named rule is violated by the supplied provenance path

None of these four theorems is proved (in Rocq or otherwise) as of this
document -- each is the algebraic content of SS6-9's own equalities,
demonstrated on concrete rational examples by the spike, not yet
formally proved for arbitrary `D`, `r`, `L`. The `INADMISSIBLE` theorem
is RULE-RELATIVE and must never be stated as a proof of every possible
form of inadmissibility -- only that the ONE named, currently-supported
rule (`independent_rows_no_ancestry_relation`) was genuinely violated.

### Verdict exclusivity, and its precise limit

For a well-formed instance under a deterministic policy, the intended
verdicts are mutually exclusive. The algebraic branches, AFTER
admissibility, are:

    r not in im(D)
    or (r in im(D) and ker(D) not subseteq ker(L))
    or (r in im(D) and ker(D) subseteq ker(L))

An accepted `EXACT` certificate mathematically excludes `UNDERDETERMINED`
and `OBSTRUCTED` (the three branches above are mutually exclusive by
construction); an accepted `OBSTRUCTED` certificate excludes both
repairable branches. But the relationship with `INADMISSIBLE` depends
entirely on the ASSESSMENT PROTOCOL: an algebraically exact instance
could still be inadmissible if admissibility was simply never checked
for it. **Therefore every algebraic certificate must include or bind an
accepted admissibility result** -- otherwise the four verdicts are not
genuinely exclusive at the certificate level, merely at the level of
one particular generator's own internal decision order.

This is why SS10's `admissibility_witness` is REQUIRED, not optional,
on `EXACT`/`UNDERDETERMINED`/`OBSTRUCTED` -- confirmed directly: the
spike's own `WITNESS_REQUIRED_KEYS` includes `admissibility_witness`
for all three, and `_verify_exact`/`_verify_underdetermined`/`_verify_
obstructed` each call `_verify_admissibility_cuts` and return early
(REJECT propagates) if it fails, BEFORE any of SS6-8's own algebraic
checks run.

## 15. Tamper and threat model

The spike's own successful test classes (all confirmed by running
`pce_certificate_spike.py`, 35/35 as of this document):

- witness mutation (a single entry of `u`, `M`, `k`, or `y`);
- claimed-value mutation (`x`);
- digest mismatch (residue mutated in `instance` after the certificate
  was built, so `input_digest` no longer matches);
- provenance-edge mutation after digest creation (now caught by
  `input_digest`, per SS4's corrected boundary);
- path-edge mutation (a nonexistent node spliced into `ancestry_path`);
- endpoint mutation (`ancestry_path`'s own endpoint no longer matching
  the declared `left_evidence`/`right_evidence`);
- direction mutation (`direction` declared as the opposite of what the
  supplied path actually establishes);
- repeated-vertex mutation (`ancestry_path` no longer a simple path);
- policy mutation (the declared independent pair no longer matching the
  implicated evidence);
- reachability-cut mutation (four distinct sub-cases, SS10: a direct
  edge defeating a falsely claimed cut; a longer path defeating a
  falsely claimed cut; a cut omitting the required vertex itself; a cut
  improperly including the excluded endpoint);
- swapped `input_digest`/`policy_digest` values;
- extra, verdict-irrelevant instance fields (four sub-cases, one per
  verdict, SS11);
- cross-verdict substitution (5 cases, SS11);
- missing and extra witness keys (structural, via `validate_closed_
  keys` and the required-keys check);
- domain-separation confirmation (identical canonical bytes hash
  differently under the two digest domains -- a positive check, not a
  rejection, but confirming the mechanism SS4 depends on).

The production threat model additionally includes an untrusted
generator attempting to: fabricate a witness (covered by the tamper
classes above); substitute another instance or another policy (digest
mismatch, per SS4's now-implemented boundary); relabel the verdict
(cross-verdict substitution); exploit parsing ambiguity (non-canonical
rational strings, duplicate JSON keys -- both already rejected by the
inherited `r21_certificate_format` primitives this document reuses);
exploit malformed dimensions (ragged matrices, mismatched row/column
counts -- rejected by `parse_matrix`/explicit length checks); cause
verifier resource exhaustion (SS16).

## 16. Resource limits

Carried over from the inherited verifier discipline (`r21_certificate_
format.py`'s own `MAX_DIMENSION`, `MAX_TOTAL_ENTRIES`, `MAX_RATIONAL_
CHARS`, `MAX_INPUT_BYTES`), reused directly rather than reinvented:

- bounded dimensions and rational-string lengths (inherited constants);
- bounded evidence and provenance-graph size (a new limit this document
  introduces, since the inherited constants have no notion of a
  provenance graph at all -- e.g. `MAX_PROVENANCE_EDGES`, a resource
  limit, not yet chosen or spike-tested);
- bounded provenance-path length (likewise new; the spike's own paths
  are 2-3 nodes, exercising no meaningful length limit at all);
- bounded nesting depth (the envelope/instance/witness structure is
  fixed and shallow by construction -- no untrusted recursive nesting
  exists anywhere in this schema);
- explicit rejection before large allocation (`check_file_size`,
  inherited, checked before the file is even opened);
- no uncontrolled recursion over untrusted structures -- the verifier's
  own path/edge/labelling checks are all plain loops (`for i in
  range(len(path) - 1)`, `for e in edges`), never recursive descent
  over attacker-controlled depth.

**Implemented (hardening pass, 2026-07-22).** The provenance path is
now REQUIRED to be a simple path (no repeated vertices) -- confirmed
directly: `verifier._verify_inadmissible` rejects `ancestry_path` if
`len(set(path)) != len(path)`, and the "repeated vertex in ancestry_
path (not a simple path)" tamper test confirms a path revisiting an
already-used vertex is rejected. A supplied ancestry path never needs a
cycle to establish an ancestry relation, and disallowing repeats bounds
path length by the graph's own vertex count for free.

## 17. Spike traceability (non-normative)

Recorded here for provenance, not as production code:

- 35/35 spike checks passed (`spike_certificates/pce_certificate_
  spike.py`'s own final summary, up from 21/21 after the first
  certificate-feasibility pass and 23/23 after this document's own
  first draft);
- five valid certificates accepted: one per verdict, plus the NEW
  `exact_common_ancestor` case (`a <- c -> b`, identical algebra to
  `exact.json`, accepted as `EXACT` despite `row-a`/`row-b` sharing a
  weakly connected component -- the completeness gap SS10 closes);
- a domain-separation confirmation (identical canonical bytes hash
  differently under the two digest domains);
- 22 tamper cases rejected (SS15's full list);
- 5 cross-verdict substitutions rejected;
- no solver, nullspace, or graph-search dependency in the verifier,
  confirmed by direct `grep` of its own imports, not merely its
  docstring's claim;
- the exact factorisation witness `M = [[1, 1]]` for the chain example
  (`D = [[-1,1,0],[0,-1,1]]`, `L = [-1,0,1]`), confirmed to satisfy
  both `M D = L` and `M r = L u = (5)`;
- the initial provenance rule implemented and then RENAMED, from
  `independent_rows_no_shared_ancestry` to `independent_rows_no_
  ancestry_relation`, with an added `direction` field and directed
  (not undirected) edge checking;
- the admissibility witness implemented, found INCOMPLETE (component
  labelling), and REPLACED with reachability cuts -- SS10's own
  correction, made before any production code was written from the
  incomplete version;
- the provenance-digest boundary implemented, found WRONG in this
  document's own first draft (folding provenance into `policy_digest`),
  and CORRECTED to bind provenance under `input_digest` instead -- SS4's
  own correction;
- the fact that `spike/` and `spike_certificates/` both remain
  untracked as of this document.

This document records two architectural corrections made to its own
FIRST DRAFT before any production code was written from it (SS4's
digest-boundary reversal, SS10's labelling-to-cuts replacement), plus
confirmation that two other corrections flagged as pending in that
first draft (verdict-specific closed instance schemas, SS11; the
simple-path requirement, SS16) are now implemented and verified. None
of these five corrections was accepted as "close enough" once a
concrete counterexample or a concrete implementation gap was found --
each was either fixed in the spike and re-verified, or (for the two
genuinely new architectural corrections) fixed in this document AND
the spike together, in the same pass.

The executable spike is not preserved as production code merely to
keep this evidence; this document records the observed result, and the
spike itself remains outside committed architecture.
