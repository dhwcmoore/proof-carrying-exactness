# Proof-Carrying Exactness Verifier: Traceability Manifest

Maps every normative requirement in
[`docs/design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md`](design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md)
to at least one production test in `tests/test_pce_*.py`, so the
implementation and the specification cannot silently diverge. 95
production tests as of this document; see each test file's own module
docstring for which spec section it covers.

## SS3 Common envelope

| Requirement | Test |
|---|---|
| Unknown top-level keys rejected | `test_pce_parser.py::test_rejects_unknown_top_level_key` |
| Duplicate JSON keys rejected at any nesting level | `test_pce_parser.py::test_rejects_duplicate_top_level_key`, `::test_rejects_duplicate_key_at_any_nesting_level` |
| Missing required keys rejected | `test_pce_parser.py::test_rejects_missing_required_key` |
| Verdict-specific witness schemas closed | `test_pce_parser.py::test_rejects_unknown_witness_key`, `test_pce_cross_verdict.py` (all cases) |
| Values parsed before arithmetic | `test_pce_parser.py::test_rejects_incorrect_json_type_for_matrix` |
| Malformed input fails closed, no uncaught exception | `test_pce_resource_limits.py::test_unexpected_internal_error_reported_generically_not_leaked`, `::test_non_bytes_input_is_an_anticipated_rejection_not_a_crash` |
| Unrecognized schema/verdict rejected | `test_pce_parser.py::test_rejects_unrecognized_schema`, `::test_rejects_unrecognized_verdict` |

## SS4 Digest model

| Requirement | Test |
|---|---|
| Provenance bound by `input_digest`, not `policy_digest` | `test_pce_digests.py::test_provenance_mutation_changes_input_digest` |
| Policy bound by `policy_digest` | `test_pce_digests.py::test_independence_policy_mutation_changes_policy_digest` |
| Domain-separated digests | `test_pce_digests.py::test_input_and_policy_domains_differ_for_identical_payload_bytes` |
| Object key order does not matter | `test_pce_digests.py::test_object_key_order_does_not_matter_before_canonicalisation` |
| Array order significant where semantically ordered | `test_pce_digests.py::test_array_order_remains_significant_where_semantically_ordered` |
| Rational values have one canonical representation | `test_pce_digests.py::test_rational_values_have_one_canonical_representation` |
| Equivalent matrices produce identical canonical bytes | `test_pce_digests.py::test_equivalent_matrices_produce_identical_canonical_bytes` |
| Swapped digest values rejected | `test_pce_digests.py::test_swapped_input_and_policy_digest_values_rejected` |
| Residue mutation after digest creation caught | `test_pce_digests.py::test_residue_mutation_after_digest_creation_caught_by_input_digest` |

## SS5 Rational and matrix representation

| Requirement | Test |
|---|---|
| No floating-point values | `test_pce_parser.py::test_rejects_floating_point_rational` |
| Canonical reduced form | `test_pce_parser.py::test_rejects_non_canonical_rational_string` |
| Positive denominators | `test_pce_parser.py::test_rejects_negative_denominator` |
| Rectangular matrices only | `test_pce_parser.py::test_rejects_ragged_matrix` |
| Explicit dimension compatibility | `test_pce_parser.py::test_rejects_dimension_mismatch_between_D_and_r` |

## SS6 EXACT

| Requirement | Test |
|---|---|
| `D u = r` | `test_pce_exact.py::test_exact_rejects_a_repair_that_does_not_satisfy_D_u_equals_r` |
| `M D = L` | `test_pce_exact.py::test_exact_rejects_tampered_factorisation_witness` |
| Normative `M r = x` | `test_pce_exact.py::test_exact_rejects_tampered_claimed_value` |
| `L u = x` permitted redundant check | `proof_carrying_exactness/verifier.py::_verify_exact` (both checks present); exercised by `test_pce_exact.py::test_exact_accepts_valid_repair` |
| Any valid repair verifies, same claim | `test_pce_exact.py::test_exact_accepts_a_different_but_equally_valid_repair_with_the_same_claim` |
| `L` required | `test_pce_exact.py::test_exact_requires_L_in_instance` |
| Admissibility witness required | `test_pce_exact.py::test_exact_rejects_missing_admissibility_witness` |

## SS7 UNDERDETERMINED

| Requirement | Test |
|---|---|
| `D u = r` | `test_pce_underdetermined.py::test_underdetermined_rejects_tampered_repair_witness` |
| `D k = 0` | `test_pce_underdetermined.py::test_underdetermined_rejects_gauge_witness_with_Dk_nonzero` |
| `L k != 0` | `test_pce_underdetermined.py::test_underdetermined_rejects_gauge_witness_with_Lk_zero` |
| Vector-valued `L k != 0` means any component non-zero | `test_pce_underdetermined.py::test_underdetermined_vector_valued_Lk_inequality_means_any_component_nonzero` |
| Alternate repair derived, not a certificate field | `test_pce_underdetermined.py::test_underdetermined_alternate_repair_is_derived_not_a_required_field` |
| `L` required | `test_pce_underdetermined.py::test_underdetermined_requires_L_in_instance` |

## SS8 OBSTRUCTED

| Requirement | Test |
|---|---|
| `y^T D = 0` | `test_pce_obstructed.py::test_obstructed_rejects_separator_with_nonzero_yTD` |
| `y^T r != 0` | `test_pce_obstructed.py::test_obstructed_rejects_separator_with_zero_yTr` |
| `L` forbidden | `test_pce_obstructed.py::test_obstructed_forbids_L_as_an_irrelevant_algebraic_field` |
| Claim metadata digest-bound, not checked mathematically | `test_pce_obstructed.py::test_obstructed_claim_metadata_is_optional_and_digest_bound_but_not_checked_mathematically` |

## SS9 INADMISSIBLE

| Requirement | Test |
|---|---|
| Rule recognised | `test_pce_inadmissible.py::test_rejects_unrecognized_rule_id` |
| Direction recognised | `test_pce_inadmissible.py::test_rejects_unrecognized_direction` |
| Path has >= 2 entries | `test_pce_inadmissible.py::test_rejects_path_with_fewer_than_two_entries` |
| Endpoints match declared direction | `test_pce_inadmissible.py::test_rejects_direction_that_does_not_match_the_supplied_path`, `::test_rejects_endpoint_mismatch` |
| Every consecutive directed edge exists | `test_pce_inadmissible.py::test_rejects_nonexistent_provenance_edge` |
| Policy declares the pair independent | `test_pce_inadmissible.py::test_rejects_policy_no_longer_declaring_the_pair_independent` |
| Simple directed path (no repeated vertex) | `test_pce_inadmissible.py::test_rejects_repeated_vertex_in_ancestry_path` |
| Unknown vertex rejected | `test_pce_inadmissible.py::test_rejects_path_referencing_unknown_vertex` |
| `D`/`r`/`L` forbidden entirely | `test_pce_inadmissible.py::test_inadmissible_forbids_D_r_L_entirely` |
| Valid simple ancestry path accepted | `test_pce_inadmissible.py::test_inadmissible_accepts_valid_simple_ancestry_path` |

## SS10 Admissibility witness (reachability cuts)

| Requirement | Test |
|---|---|
| Common-ancestor case accepted despite shared weak component | `test_pce_exact.py::test_exact_accepts_common_ancestor_case_despite_shared_weak_component`, `test_pce_provenance.py::test_common_ancestor_case_admissible_despite_shared_weak_component` |
| Direct edge defeats a falsely claimed cut | `test_pce_provenance.py::test_direct_edge_defeats_a_falsely_claimed_cut` |
| Longer path defeats a falsely claimed cut | `test_pce_provenance.py::test_longer_path_defeats_a_falsely_claimed_cut` |
| Cut omitting the required vertex rejected | `test_pce_provenance.py::test_cut_omitting_the_required_vertex_itself_rejected` |
| Cut improperly including the excluded endpoint rejected | `test_pce_provenance.py::test_cut_improperly_including_the_excluded_endpoint_rejected` |
| Duplicate cut vertices rejected | `test_pce_provenance.py::test_cut_with_duplicate_vertices_rejected` |
| Unknown cut vertex rejected | `test_pce_provenance.py::test_cut_with_unknown_vertex_rejected` |
| Missing cut for a declared pair rejected | `test_pce_provenance.py::test_missing_cut_for_a_declared_independent_pair_rejected` |
| No search performed by the verifier | `test_pce_provenance.py::test_no_search_performed_by_admissibility_verification`, `test_pce_import_boundary.py` (mechanical) |

## SS11 Closed witness/instance variants

| Requirement | Test |
|---|---|
| Cross-verdict witness substitution rejected (5 cases) | `test_pce_cross_verdict.py` (all cases) |
| Verdict-specific closed instance schemas | `test_pce_cross_verdict.py::test_extra_instance_field_rejected_under_*` (4 cases) |

## SS12 Verification API

| Requirement | Test |
|---|---|
| `verify_certificate_bytes(bytes) -> VerificationResult` | every test in this suite exercises this exact entry point |
| No exception escapes | `test_pce_resource_limits.py::test_unexpected_internal_error_reported_generically_not_leaked` |

## SS13 Generator and verifier separation

| Requirement | Test |
|---|---|
| No solver/search import anywhere in the package | `test_pce_import_boundary.py` (full file) |
| Only the permitted `rational_linear_algebra` names imported | `test_pce_import_boundary.py::test_no_file_imports_forbidden_names_from_rational_linear_algebra` |

## SS14 Soundness obligations / verdict exclusivity

| Requirement | Test |
|---|---|
| Admissibility witness required on all three algebraic verdicts | `test_pce_exact.py::test_exact_rejects_missing_admissibility_witness`, and the corresponding required-key sets exercised throughout `test_pce_underdetermined.py`/`test_pce_obstructed.py` |

## SS15 Tamper and threat model

Covered exhaustively across `test_pce_exact.py`, `test_pce_
underdetermined.py`, `test_pce_obstructed.py`, `test_pce_inadmissible.
py`, `test_pce_digests.py`, `test_pce_provenance.py`, and `test_pce_
cross_verdict.py` -- see each file for its own specific cases.

## SS16 Resource limits

| Requirement | Test |
|---|---|
| Oversized certificate rejected before parsing | `test_pce_resource_limits.py::test_oversized_certificate_rejected_before_parsing`, `::test_oversized_certificate_via_public_api_fails_closed` |
| Excessive JSON nesting rejected | `test_pce_resource_limits.py::test_excessive_json_nesting_rejected` |
| Oversized rational string rejected | `test_pce_resource_limits.py::test_oversized_rational_string_rejected` |
| Oversized vector/matrix rejected | `test_pce_resource_limits.py::test_oversized_vector_rejected`, `::test_oversized_matrix_rows_rejected`, `::test_oversized_matrix_cols_rejected` |
| Oversized ancestry path rejected | `test_pce_resource_limits.py::test_oversized_ancestry_path_rejected` |
| Simple-path requirement (repeated vertex) | `test_pce_inadmissible.py::test_rejects_repeated_vertex_in_ancestry_path` |

## SS17 Spike traceability

Non-normative; this manifest itself is the production-side counterpart
-- the spike traceability lives in the certificate spec document, not
here.
