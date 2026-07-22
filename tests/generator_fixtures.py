"""
tests/generator_fixtures.py

Instance fixtures for proof_carrying_exactness_generator, one per
verdict. Deliberately the same algebra/provenance already exercised by
`tests/pce_fixtures.py` against the production verifier (EXACT and
UNDERDETERMINED share D, r; OBSTRUCTED is the repository's own
canonical four-cycle; INADMISSIBLE is the row-0/row-1/derived-
intermediate ancestry case) -- so a generator test failure and a
verifier test failure can never be confused for two different bugs.
"""

EXACT_INSTANCE = {
    "D": [["-1", "1", "0"], ["0", "-1", "1"]],
    "r": ["3", "2"],
    "L": [["-1", "0", "1"]],
    "row_evidence_ids": {"0": "row-0", "1": "row-1"},
    "provenance": {"vertices": ["row-0", "row-1"], "edges": []},
    "policy": {"independent_pairs": [["row-0", "row-1"]], "policy_version": "pce-policy/v1"},
}

UNDERDETERMINED_INSTANCE = {
    "D": [["-1", "1", "0"], ["0", "-1", "1"]],
    "r": ["3", "2"],
    "L": [["0", "0", "1"]],
    "row_evidence_ids": {"0": "row-0", "1": "row-1"},
    "provenance": {"vertices": ["row-0", "row-1"], "edges": []},
    "policy": {"independent_pairs": [["row-0", "row-1"]], "policy_version": "pce-policy/v1"},
}

OBSTRUCTED_INSTANCE = {
    "D": [["-1", "1", "0", "0"], ["0", "-1", "1", "0"], ["0", "0", "-1", "1"], ["-1", "0", "0", "1"]],
    "r": ["1", "1", "1", "-2"],
    "claim_metadata": "global coherent assignment of four regional values",
    "row_evidence_ids": {"0": "edge-e12", "1": "edge-e23", "2": "edge-e34", "3": "edge-e14"},
    "provenance": {"vertices": ["edge-e12", "edge-e23", "edge-e34", "edge-e14"], "edges": []},
    "policy": {"independent_pairs": [], "policy_version": "pce-policy/v1"},
}

INADMISSIBLE_INSTANCE = {
    "row_evidence_ids": {"0": "row-0", "1": "row-1"},
    "provenance": {
        "vertices": ["row-0", "row-1", "derived-intermediate"],
        "edges": [["row-1", "derived-intermediate"], ["derived-intermediate", "row-0"]],
    },
    "policy": {"independent_pairs": [["row-0", "row-1"]], "policy_version": "pce-policy/v1"},
}

ALL_INSTANCES = {
    "EXACT": EXACT_INSTANCE,
    "UNDERDETERMINED": UNDERDETERMINED_INSTANCE,
    "OBSTRUCTED": OBSTRUCTED_INSTANCE,
    "INADMISSIBLE": INADMISSIBLE_INSTANCE,
}
