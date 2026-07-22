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
- construct a component labelling proving non-connectivity.

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

### Input digest

Binds everything constitutive of the algebraic instance and attempted
claim:

- `D`;
- `r`;
- `L`, when relevant (`null` for `OBSTRUCTED`, where no claim map
  enters the mathematical obstruction test at all -- see SS8);
- evidence identifiers and evidence-to-row alignment (`row_evidence_
  ids`);
- attempted-claim metadata (a descriptive label, still digest-bound so
  it cannot be swapped post hoc even though it is never checked
  mathematically);
- transformation metadata used by the assessment, when a future
  revision of this project's evidence model introduces declared
  transformations distinct from `L` itself (not present in the spike;
  flagged here so the digest model does not need revisiting when that
  happens).

Claimed value `x` is deliberately NOT part of the input digest: it is
part of the WITNESS (a claim the certificate makes and the verifier
checks), not part of the evidence boundary the input digest fixes. The
spike's own `compute_instance_digest(D, r, L)` matches this: it never
reads `x`.

### Policy digest

Binds:

- rule identifiers (`SUPPORTED_RULE_IDS`, currently one member,
  `independent_rows_no_ancestry_relation` -- see SS9);
- independent-row declarations (`policy.independent_pairs`);
- the provenance graph (`provenance.edges`) -- committed at digest
  time, so a supplied ancestry path or component labelling is checked
  against a FIXED graph, never one the generator could quietly
  substitute after the fact;
- transformation admissibility rules, when they exist (not yet present
  in the spike -- flagged for the same reason as above);
- policy version (a `policy_version` string field, matching `tracking_
  adapter_provenance.py`'s existing convention, e.g.
  `"tracking-adapter-independence-policy/v1"` -- the spike's own
  `policy` dict did not include one; the production schema should add
  it, since a policy is exactly the kind of object whose OWN evolution
  needs a version tag independent of the certificate envelope's);
- any rule parameters (none exist for the one currently supported
  rule, which takes no parameters beyond the pair itself).

No verifier-consumed field may sit outside the appropriate digest
boundary -- concretely: `provenance` and `policy` (both consumed by
`_verify_admissibility_labelling` and `_verify_inadmissible`) must be
covered by `policy_digest`, not `input_digest`; `D`, `r`, `L` must be
covered by `input_digest`, not `policy_digest`. The spike currently
computes `policy_digest` from `instance.get("policy") or {}` ALONE,
NOT `provenance` -- this is a genuine gap this document corrects: the
provenance graph is exactly as security-critical as the policy that
interprets it (a generator that could silently swap `provenance.edges`
after computing `policy_digest` could fabricate or erase an ancestry
relation without invalidating anything), so the production `policy_
digest` must bind BOTH `policy` and `provenance` together, not `policy`
alone. This is a specification correction found by auditing the spike
against this document's own SS4 requirement, not a spike defect that
was silently accepted.

### Domain separation

Use explicit domain-separated prefixes before hashing, so the same
byte sequence can never be confused across digest domains:

    pce-input-v1 || canonical_input_bytes
    pce-policy-v1 || canonical_policy_and_provenance_bytes

The spike's `compute_instance_digest`/`compute_policy_digest` do NOT
yet prefix their canonical bytes this way (they reuse `canonical_
input_digest`'s own line-based canonical form, and a bare `json.dumps`
respectively) -- this is a second specification correction beyond what
the spike checked: the production digest functions must prepend a
domain tag before hashing, closing the (currently only theoretical, not
demonstrated) risk that an `input`-shaped byte string and a `policy`-
shaped byte string could collide or be swapped between the two digest
fields.

Rational and matrix encoding is reused from R21 outright (`parse_
rational`, `parse_vector`, `parse_matrix`, and `canonical_input_
digest`'s own canonical line format for `D`/`r`); the one genuine
extension is `L`'s own canonical serialisation (never part of `roc-
input/v1`), plus, per the corrections above, folding `provenance` into
the policy digest and adding domain-separation prefixes to both digest
functions.

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
and its two checks (edge-consistency, independent-pair label
separation) to pass BEFORE the three equalities above are even
evaluated -- confirmed directly in the spike (`_verify_exact` calls
`_verify_admissibility_labelling` first and returns early on failure).

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
   committed, DIRECTED provenance graph (`policy_digest`-bound) in
   EXACTLY that order -- not reversed, since a directed
   `[descendant, ancestor]` edge does not license traversing it
   backwards as evidence of the opposite ancestry relation;
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

Per SS14, `EXACT`/`UNDERDETERMINED`/`OBSTRUCTED` each additionally
require an `admissibility_witness`:

    { "component_labels": { <evidence_id>: <label>, ... } }

### Required checks

1. every committed provenance edge `[a, b]` connects two IDENTICALLY-
   labelled nodes (`labels[a] == labels[b]`);
2. every policy-declared independent pair `[left, right]` carries
   DIFFERENT labels (`labels[left] != labels[right]`).

By induction over check 1 (an edge always connects equal labels), any
two nodes connected by SOME path of committed edges, in either
direction, necessarily share a label; therefore two DIFFERENTLY
labelled nodes cannot be connected by any path at all -- check 2 is
therefore a genuine, checkable proof of non-connectivity, and hence of
admissibility for that pair, WITHOUT the verifier ever traversing the
graph itself. The generator constructs the labelling via its own
union-find search (`pce_certificate_spike.compute_component_labels`,
confirmed to reuse no verifier-side code); the verifier only checks
label-consistency, locally, edge by edge and pair by pair.

This mechanism and `INADMISSIBLE`'s own explicit-path witness (SS9) are
the positive and negative sides of the SAME underlying connectivity
fact, verified via two DIFFERENT, independently checkable witness
shapes -- deliberately not unified into one mechanism, since a positive
non-connectivity proof (a labelling) and a negative connectivity proof
(a path) have genuinely different verification shapes, and conflating
them would make either check harder to audit in isolation.

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

`L` is mathematically required for `EXACT`/`UNDERDETERMINED` but not
for `OBSTRUCTED`'s own proof. Per this document's own recommendation
(closed, verdict-specific instance schemas inside one common envelope,
rather than one shared superset instance schema): the production
schema should define `INSTANCE_KEYS` per verdict, analogous to `WITNESS
_KEYS` per verdict, with `L` REQUIRED for `EXACT`/`UNDERDETERMINED` and
FORBIDDEN (not merely optional/null) for `OBSTRUCTED`. The spike's own
`INSTANCE_KEYS` is a single shared frozenset with `L` merely nullable
for all four verdicts -- looser than this document's own
recommendation. This is a third specification correction found by
holding the spike to this document's own stated principle, not a claim
that the spike already implements the stricter form.

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
| Search provenance graph (labelling) | permitted | forbidden |
| Check `D u = r`                     | permitted |  required |
| Check `M D = L`                     | permitted |  required |
| Check `M r = x`                     | permitted |  required |
| Check `D k = 0`                     | permitted |  required |
| Check `L k != 0`                    | permitted |  required |
| Check `y^T D = 0`                   | permitted |  required |
| Check `y^T r != 0`                  | permitted |  required |
| Validate supplied path edges (directed) | permitted |  required |
| Validate supplied component labelling   | permitted |  required |
| Recompute digests                   | permitted |  required |

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
obstructed` each call `_verify_admissibility_labelling` and return
early (REJECT propagates) if it fails, BEFORE any of SS6-8's own
algebraic checks run.

## 15. Tamper and threat model

The spike's own successful test classes (all confirmed by running
`pce_certificate_spike.py`, 23/23 as of this document):

- witness mutation (a single entry of `u`, `M`, `k`, or `y`);
- claimed-value mutation (`x`);
- digest mismatch (residue mutated in `instance` after the certificate
  was built, so `input_digest` no longer matches);
- path-edge mutation (a nonexistent node spliced into `ancestry_path`);
- endpoint mutation (`ancestry_path`'s own endpoint no longer matching
  the declared `left_evidence`/`right_evidence`);
- direction mutation (`direction` declared as the opposite of what the
  supplied path actually establishes);
- policy mutation (the declared independent pair no longer matching the
  implicated evidence);
- admissibility-labelling mutation (two declared-independent evidence
  identifiers relabelled to share a component);
- cross-verdict substitution (5 cases, SS11);
- missing and extra witness keys (structural, via `validate_closed_
  keys` and the required-keys check).

The production threat model additionally includes an untrusted
generator attempting to: fabricate a witness (covered by the tamper
classes above); substitute another instance or another policy
(digest mismatch, once SS4's `provenance`-in-`policy_digest` correction
is implemented); relabel the verdict (cross-verdict substitution);
exploit parsing ambiguity (non-canonical rational strings, duplicate
JSON keys -- both already rejected by the inherited `r21_certificate_
format` primitives this document reuses); exploit malformed dimensions
(ragged matrices, mismatched row/column counts -- rejected by `parse_
matrix`/explicit length checks); cause verifier resource exhaustion
(SS16).

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

The provenance path itself should be REQUIRED to be a simple path (no
repeated vertices) -- confirmed a defined, sensible restriction, since
a supplied ancestry path never needs a cycle to establish an ancestry
relation, and disallowing repeats bounds path length by the graph's own
node count for free. This is a specification requirement the spike does
not currently enforce (its own `_verify_inadmissible` does not check
for repeated vertices in `ancestry_path`) -- a fourth specification
correction found by writing this section, not a claim the spike already
checks it.

## 17. Spike traceability (non-normative)

Recorded here for provenance, not as production code:

- 23/23 spike checks passed (`spike_certificates/pce_certificate_
  spike.py`'s own final summary);
- four valid certificates accepted, one per verdict;
- 14 tamper cases rejected (3 each for `EXACT`/`UNDERDETERMINED`/
  `OBSTRUCTED`, 4 for `INADMISSIBLE`, 1 admissibility-labelling);
- 5 cross-verdict substitutions rejected;
- no solver, nullspace, or graph-search dependency in the verifier,
  confirmed by direct `grep` of its own imports, not merely its
  docstring's claim;
- the exact factorisation witness `M = [[1, 1]]` for the chain example
  (`D = [[-1,1,0],[0,-1,1]]`, `L = [-1,0,1]`), confirmed to satisfy
  both `M D = L` and `M r = L u = (5)`;
- the initial provenance rule implemented and then RENAMED during this
  document's own drafting, from `independent_rows_no_shared_ancestry`
  to `independent_rows_no_ancestry_relation`, with an added `direction`
  field and directed (not undirected) edge checking -- the naming
  correction that opened this document's own commit sequence;
- the fact that `spike/` and `spike_certificates/` both remain
  untracked as of this document.

This document also records four specification-level corrections found
by auditing the spike against its own stated principles, none of which
the spike itself currently implements (each flagged in place above,
SS4, SS4, SS11, SS16 respectively): `policy_digest` must bind
`provenance` as well as `policy`; both digest functions need explicit
domain-separation prefixes; instance schemas should be verdict-specific
(closed), not one shared superset; and `ancestry_path` should be
required to be a simple path. These are documented as PRODUCTION
requirements this specification adds, not claims about what the
untracked spike already does -- the distinction this document, and the
one before it, both insist on throughout.

The executable spike is not preserved as production code merely to
keep this evidence; this document records the observed result, and the
spike itself remains outside committed architecture.
