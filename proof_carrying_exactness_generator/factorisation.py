"""
proof_carrying_exactness_generator.factorisation

Generator-side factorisation search: given D and a claim map L, finds M
with M D = L by solving D^T m_i = (row i of L) for each row of L.
Reuses `rational_linear_algebra.{solve_over_Q, transpose}` -- Gauss-
Jordan elimination, exactly the discovery machinery the production
verifier package (`proof_carrying_exactness/`) is forbidden from
importing. Its result is never trusted directly: `generator.py` only
ever releases a certificate once `proof_carrying_exactness.verify_
certificate_bytes` has independently accepted it.
"""

from fractions import Fraction
from typing import List, Optional, Tuple

from rational_linear_algebra import solve_over_Q, transpose


def find_factorisation(
    D: List[List[Fraction]], L: List[List[Fraction]]
) -> Tuple[bool, Optional[List[List[Fraction]]]]:
    D_T = transpose(D)
    M_rows = []
    for L_row in L:
        solvable, m_row = solve_over_Q(D_T, L_row)
        if not solvable:
            return False, None
        M_rows.append(m_row)
    return True, M_rows
