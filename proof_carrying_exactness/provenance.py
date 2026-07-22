"""
proof_carrying_exactness.provenance

Direct, non-search provenance validation, per
docs/design/PROOF_CARRYING_EXACTNESS_CERTIFICATE_SPEC.md SS9-10.

Two mechanisms, both checked locally with no verifier-side graph
search:

- `verify_admissibility_cuts`: for the three ALGEBRAIC verdicts, proves
  admissibility via a REACHABILITY-CUT witness per declared independent
  pair -- two forward-closed vertex sets, one proving each direction is
  unreachable. Sound AND complete for finite directed graphs (unlike an
  earlier, superseded component-labelling witness -- see this
  project's own certificate spec SS10 for the counterexample, `a <- c
  -> b`, that motivated the replacement).
- `verify_inadmissible_path`: for `INADMISSIBLE`, checks a supplied
  SIMPLE directed path establishes an ancestry relation between two
  implicated evidence identifiers, edge by edge, against the committed,
  digest-bound provenance graph.

Neither function ever traverses the graph to DISCOVER a path or cut --
both are entirely generator-supplied and only checked here.
"""

from typing import Dict, List

from .errors import CertificateRejected
from .limits import MAX_PROVENANCE_PATH_LENGTH
from .schemas import DIRECTIONS, SUPPORTED_RULE_IDS


def _verify_cut(vertices: set, edges: List[tuple], S, must_contain: str, must_exclude: str, label: str) -> None:
    if not isinstance(S, list):
        raise CertificateRejected(f"{label}: cut must be a list of vertex identifiers")
    if len(set(S)) != len(S):
        raise CertificateRejected(f"{label}: cut contains duplicate vertex identifiers")
    S_set = set(S)
    unknown = S_set - vertices
    if unknown:
        raise CertificateRejected(f"{label}: cut references unknown vertex identifier(s): {sorted(unknown)}")
    if must_contain not in S_set:
        raise CertificateRejected(f"{label}: cut does not contain required vertex {must_contain!r}")
    if must_exclude in S_set:
        raise CertificateRejected(f"{label}: cut improperly includes the excluded endpoint {must_exclude!r}")
    for a, b in edges:
        if a in S_set and b not in S_set:
            raise CertificateRejected(
                f"{label}: cut is not closed under edge ({a!r}, {b!r}) -- {a!r} is in S but {b!r} is not"
            )


def verify_admissibility_cuts(provenance: dict, policy: dict, admissibility_witness: dict) -> None:
    """Raises CertificateRejected on any failure; returns normally (no
    value) if every declared independent pair's cut pair is valid."""
    vertices = set(provenance.get("vertices", []))
    edges = [tuple(e) for e in provenance.get("edges", [])]
    independent_pairs = policy.get("independent_pairs", [])

    if not isinstance(admissibility_witness, dict):
        raise CertificateRejected("admissibility_witness must be a JSON object")
    cuts = admissibility_witness.get("cuts")
    if not isinstance(cuts, list):
        raise CertificateRejected("admissibility_witness.cuts must be a list")
    if len(cuts) != len(independent_pairs):
        raise CertificateRejected(
            f"admissibility_witness supplies {len(cuts)} cut-pair(s) but the policy declares "
            f"{len(independent_pairs)} independent pair(s)"
        )

    by_pair: Dict[frozenset, dict] = {}
    for entry in cuts:
        if not isinstance(entry, dict) or "pair" not in entry:
            raise CertificateRejected(f"malformed admissibility cut entry: {entry!r}")
        pair = entry["pair"]
        if not (isinstance(pair, list) and len(pair) == 2):
            raise CertificateRejected(f"malformed admissibility cut pair: {pair!r}")
        by_pair[frozenset(pair)] = entry

    for left, right in independent_pairs:
        entry = by_pair.get(frozenset({left, right}))
        if entry is None:
            raise CertificateRejected(f"no admissibility cut supplied for declared independent pair ({left!r}, {right!r})")
        _verify_cut(vertices, edges, entry.get("left_not_reaches_right"), left, right,
                    f"cut({left},{right}) left_not_reaches_right")
        _verify_cut(vertices, edges, entry.get("right_not_reaches_left"), right, left,
                    f"cut({left},{right}) right_not_reaches_left")


def verify_inadmissible_path(provenance: dict, policy: dict, witness: dict) -> None:
    """Raises CertificateRejected unless the supplied witness genuinely
    establishes a policy-violating ancestry relation."""
    vertices = set(provenance.get("vertices", []))
    edges = provenance.get("edges", [])
    independent_pairs = policy.get("independent_pairs", [])

    rule_id = witness["rule_id"]
    left = witness["left_evidence"]
    right = witness["right_evidence"]
    direction = witness["direction"]
    path = witness["ancestry_path"]

    if rule_id not in SUPPORTED_RULE_IDS:
        raise CertificateRejected(f"unrecognized rule_id: {rule_id!r}")
    if direction not in DIRECTIONS:
        raise CertificateRejected(f"unrecognized direction: {direction!r}")
    if not isinstance(path, list) or len(path) < 2:
        raise CertificateRejected("ancestry_path must be a list of at least 2 evidence identifiers")
    if len(path) > MAX_PROVENANCE_PATH_LENGTH:
        raise CertificateRejected(f"ancestry_path length {len(path)} exceeds MAX_PROVENANCE_PATH_LENGTH={MAX_PROVENANCE_PATH_LENGTH}")
    if len(set(path)) != len(path):
        raise CertificateRejected("ancestry_path contains a repeated vertex -- a simple path is required")
    unknown = set(path) - vertices
    if unknown:
        raise CertificateRejected(f"ancestry_path references unknown vertex identifier(s): {sorted(unknown)}")

    expected_start, expected_end = (left, right) if direction == "left_to_right" else (right, left)
    if path[0] != expected_start or path[-1] != expected_end:
        raise CertificateRejected(
            f"ancestry_path ({path[0]!r} .. {path[-1]!r}) does not match direction {direction!r} "
            f"for the implicated pair ({left!r}, {right!r}) -- expected to start at {expected_start!r} "
            f"and end at {expected_end!r}"
        )

    committed_edges = {(a, b) for a, b in edges if isinstance(a, str) and isinstance(b, str)}
    for i in range(len(path) - 1):
        edge = (path[i], path[i + 1])
        if edge not in committed_edges:
            raise CertificateRejected(f"ancestry_path edge {edge!r} is not present in the committed, directed provenance graph")

    declared_pairs = {frozenset(p) for p in independent_pairs if isinstance(p, list) and len(p) == 2}
    if frozenset({left, right}) not in declared_pairs:
        raise CertificateRejected(
            f"the policy does not declare ({left!r}, {right!r}) as required to be independent -- nothing was violated"
        )
