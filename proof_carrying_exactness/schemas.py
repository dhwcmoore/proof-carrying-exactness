"""
proof_carrying_exactness.schemas

Closed schema definitions for the production certificate envelope and
its four verdict-specific instance/witness variants, per
docs/design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md SS3, SS9-11.
Schema/constant definitions only -- no verification logic.
"""

ENVELOPE_SCHEMA = "proof-carrying-exactness/certificate/v1"

VERDICT_EXACT = "EXACT"
VERDICT_UNDERDETERMINED = "UNDERDETERMINED"
VERDICT_OBSTRUCTED = "OBSTRUCTED"
VERDICT_INADMISSIBLE = "INADMISSIBLE"

VERDICTS = frozenset({VERDICT_EXACT, VERDICT_UNDERDETERMINED, VERDICT_OBSTRUCTED, VERDICT_INADMISSIBLE})

ENVELOPE_KEYS = frozenset({"schema", "verdict", "input_digest", "policy_digest", "instance", "witness"})

# Per-verdict CLOSED instance key sets (spec SS11): irrelevant algebraic
# fields must not be silently accepted -- D/r are forbidden entirely
# for INADMISSIBLE; L is forbidden for OBSTRUCTED/INADMISSIBLE.
INSTANCE_KEYS = {
    VERDICT_EXACT: frozenset({"D", "r", "L", "provenance", "policy", "row_evidence_ids"}),
    VERDICT_UNDERDETERMINED: frozenset({"D", "r", "L", "provenance", "policy", "row_evidence_ids"}),
    VERDICT_OBSTRUCTED: frozenset({"D", "r", "provenance", "policy", "row_evidence_ids", "claim_metadata"}),
    VERDICT_INADMISSIBLE: frozenset({"provenance", "policy", "row_evidence_ids"}),
}
INSTANCE_REQUIRED_KEYS = {
    VERDICT_EXACT: INSTANCE_KEYS[VERDICT_EXACT],
    VERDICT_UNDERDETERMINED: INSTANCE_KEYS[VERDICT_UNDERDETERMINED],
    VERDICT_OBSTRUCTED: frozenset({"D", "r", "provenance", "policy", "row_evidence_ids"}),  # claim_metadata optional
    VERDICT_INADMISSIBLE: INSTANCE_KEYS[VERDICT_INADMISSIBLE],
}

PROVENANCE_KEYS = frozenset({"vertices", "edges"})
POLICY_KEYS = frozenset({"independent_pairs", "policy_version"})

# Per-verdict CLOSED witness key sets (spec SS11).
WITNESS_KEYS = {
    VERDICT_EXACT: frozenset({"repair_witness", "factorisation_witness", "claimed_value", "admissibility_witness"}),
    VERDICT_UNDERDETERMINED: frozenset({"repair_witness", "gauge_witness", "admissibility_witness"}),
    VERDICT_OBSTRUCTED: frozenset({"separator", "admissibility_witness"}),
    VERDICT_INADMISSIBLE: frozenset({"rule_id", "left_evidence", "right_evidence", "direction", "ancestry_path"}),
}
WITNESS_REQUIRED_KEYS = {
    VERDICT_EXACT: WITNESS_KEYS[VERDICT_EXACT],
    VERDICT_UNDERDETERMINED: WITNESS_KEYS[VERDICT_UNDERDETERMINED],
    VERDICT_OBSTRUCTED: WITNESS_KEYS[VERDICT_OBSTRUCTED],
    VERDICT_INADMISSIBLE: WITNESS_KEYS[VERDICT_INADMISSIBLE],
}

# Spec SS9: proves ONE directed ancestry relation (a path, in either
# direction), not the broader "shared common ancestor via two
# converging paths" claim.
SUPPORTED_RULE_IDS = frozenset({"independent_rows_no_ancestry_relation"})
DIRECTIONS = frozenset({"left_to_right", "right_to_left"})
