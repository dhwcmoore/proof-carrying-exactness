#!/usr/bin/env python3
"""
pce_assess.py

The `pce-assess` CLI entry point:

    python3 pce_assess.py instance.json --certificate-out verdict.json

A thin launcher around `proof_carrying_exactness_assess.cli.main` --
all logic lives in that package. See `proof_carrying_exactness_assess/
assess.py` for the full pipeline (parse and validate -> generate ->
verify -> render) and its trust boundary.
"""

import sys

from proof_carrying_exactness_assess.cli import main

if __name__ == "__main__":
    sys.exit(main())
