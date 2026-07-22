"""
proof_carrying_exactness_assess.renderer

Human-readable text for an already-ACCEPTED certificate's verdict.
Describes only what the verified certificate proves -- no inferred
cause, no recommended repair, no provenance conclusion beyond the
admissibility witness itself. Never invoked for a REJECT: there is no
verdict to describe if independent verification did not accept one.
"""

_VERDICT_SUMMARIES = {
    "EXACT": "Claim is invariant across every permitted repair.",
    "UNDERDETERMINED": "A repair exists, but the declared claim changes along a permitted gauge direction.",
    "OBSTRUCTED": "No permitted repair reconciles the evidence with the declared adjustments.",
    "INADMISSIBLE": "An ancestry relation exists between evidence declared independent, so the declared admissibility policy does not hold.",
}


def render_summary(verdict: str) -> str:
    try:
        return _VERDICT_SUMMARIES[verdict]
    except KeyError:
        raise ValueError(f"no rendering defined for verdict {verdict!r}") from None
