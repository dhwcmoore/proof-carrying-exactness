"""
proof_carrying_exactness_generator.admissibility

Generator-side provenance graph search: reachability sets, ancestry
paths, and reachability-cut witnesses. This is the graph-search
machinery `proof_carrying_exactness.provenance` deliberately never
performs -- that module only ever CHECKS an already-supplied cut or
path; discovering one is this package's job.
"""

from typing import Dict, List, Optional, Set, Tuple


def reachable_set(edges: List[List[str]], source: str) -> Set[str]:
    """Directed BFS, forward only: every vertex reachable from `source`,
    including `source` itself. The result is, by construction, forward-
    closed -- if u is reachable and (u, v) is an edge, v is reachable
    too -- exactly what a valid reachability-cut witness requires."""
    adjacency: Dict[str, List[str]] = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)
    seen = {source}
    frontier = [source]
    while frontier:
        node = frontier.pop()
        for neighbour in adjacency.get(node, []):
            if neighbour not in seen:
                seen.add(neighbour)
                frontier.append(neighbour)
    return seen


def _bfs_directed_path(edges: List[List[str]], start: str, goal: str) -> Optional[List[str]]:
    """Breadth-first search for a SIMPLE directed path from start to
    goal (no repeated vertices, guaranteed by BFS over a "seen" set)."""
    adjacency: Dict[str, List[str]] = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)

    frontier = [[start]]
    seen = {start}
    while frontier:
        path = frontier.pop(0)
        node = path[-1]
        if node == goal:
            return path
        for neighbour in adjacency.get(node, []):
            if neighbour not in seen:
                seen.add(neighbour)
                frontier.append(path + [neighbour])
    return None


def find_ancestry_path(
    edges: List[List[str]], left: str, right: str
) -> Tuple[Optional[str], Optional[List[str]]]:
    """Tries BOTH directions of the ancestry relation between `left` and
    `right`, returning (direction, path) for whichever direction a
    directed path is actually found, or (None, None) if neither holds."""
    path = _bfs_directed_path(edges, left, right)
    if path is not None:
        return "left_to_right", path
    path = _bfs_directed_path(edges, right, left)
    if path is not None:
        return "right_to_left", path
    return None, None


def build_admissibility_witness(provenance: dict, policy: dict) -> dict:
    """For every declared independent pair, computes both reachable
    sets. Raises ValueError if either direction turns out to be
    reachable -- a caller that reaches this function should already have
    classified the instance as INADMISSIBLE upstream, so this is a
    defensive invariant check, not a decision point."""
    edges = provenance.get("edges", [])
    cuts = []
    for left, right in policy.get("independent_pairs", []):
        S_left = reachable_set(edges, left)
        S_right = reachable_set(edges, right)
        if right in S_left:
            raise ValueError(f"{left!r} can reach {right!r} -- should have been classified INADMISSIBLE")
        if left in S_right:
            raise ValueError(f"{right!r} can reach {left!r} -- should have been classified INADMISSIBLE")
        cuts.append({
            "pair": [left, right],
            "left_not_reaches_right": sorted(S_left),
            "right_not_reaches_left": sorted(S_right),
        })
    return {"cuts": cuts}
