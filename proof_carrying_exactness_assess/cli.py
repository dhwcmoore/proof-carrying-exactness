"""
proof_carrying_exactness_assess.cli

The `pce-assess` CLI (root-level launcher: `pce_assess.py`):

    pce-assess instance.json --certificate-out verdict.json

Prints a concise terminal report and, only on ACCEPT, writes the
verified certificate to `--certificate-out` if given. No certificate
file is ever written for a REJECT, and a failed write never leaves a
partial file behind (the underlying write is a single `write_bytes`
call -- it either fully succeeds or the destination is never created/
touched).

Exit codes:
    0  ACCEPT
    1  malformed instance (bad JSON or a schema violation)
    2  certificate generation failed
    3  the generated certificate was rejected by independent verification
    4  the certificate was accepted but could not be written to --certificate-out
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .assess import (
    STAGE_GENERATION_FAILED,
    STAGE_MALFORMED_INSTANCE,
    STAGE_VERIFICATION_REJECTED,
    AssessmentResult,
    assess_instance,
)

EXIT_SUCCESS = 0
EXIT_MALFORMED_INSTANCE = 1
EXIT_GENERATION_FAILED = 2
EXIT_VERIFICATION_REJECTED = 3
EXIT_OUTPUT_WRITE_FAILED = 4

_EXIT_CODE_BY_STAGE = {
    STAGE_MALFORMED_INSTANCE: EXIT_MALFORMED_INSTANCE,
    STAGE_GENERATION_FAILED: EXIT_GENERATION_FAILED,
    STAGE_VERIFICATION_REJECTED: EXIT_VERIFICATION_REJECTED,
}


def _exit_code_for_rejection(reason: str) -> int:
    stage = reason.split(":", 1)[0]
    return _EXIT_CODE_BY_STAGE.get(stage, EXIT_MALFORMED_INSTANCE)


def render_report(result: AssessmentResult) -> str:
    if result.accepted:
        return "\n".join([f"ACCEPT {result.verdict}", result.summary, "Certificate verified independently."])
    return "\n".join(["REJECT", result.summary, result.reason])


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pce-assess",
        description="Assess a proof-carrying-exactness instance end to end: generate a four-verdict "
                    "certificate and report only what independent verification proves.",
    )
    parser.add_argument("instance", type=Path, help="path to the instance JSON file")
    parser.add_argument(
        "--certificate-out", type=Path, default=None,
        help="path to write the generated certificate, if one is produced and verified",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        instance_bytes = args.instance.read_bytes()
    except OSError as e:
        print(f"REJECT\ncould not read instance file {args.instance}: {e}")
        return EXIT_MALFORMED_INSTANCE

    result = assess_instance(instance_bytes)
    print(render_report(result))

    if not result.accepted:
        return _exit_code_for_rejection(result.reason)

    if args.certificate_out is not None:
        try:
            args.certificate_out.write_bytes(result.certificate_bytes)
        except OSError as e:
            print(f"could not write certificate to {args.certificate_out}: {e}", file=sys.stderr)
            return EXIT_OUTPUT_WRITE_FAILED

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
