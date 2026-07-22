# Proof-Carrying Exactness: End-to-End Demonstration

**Status (2026-07-22): canonical reference example.** Every command and
output below was actually run, from a fresh `git clone` of this
repository at the commit named below, not reconstructed from memory or
hand-edited afterward. `tests/test_pce_assess_demonstration.py` re-runs
the same four pipelines and asserts the certificate digests and
verdicts below still hold -- this document cannot silently drift from
what the repository actually does without that test failing.

## Scope of what this demonstrates

This shows the complete chain for the generic, region-agnostic
end-to-end boundary:

```text
instance JSON (examples/pce_assess/*.json)
          |
          v
pce_assess.py  (proof_carrying_exactness_assess)
          |
          +--> parse and validate
          +--> proof_carrying_exactness_generator.generate_certificate  (untrusted)
          +--> proof_carrying_exactness.verify_certificate_bytes         (production, called a SECOND time here)
          +--> render only what the verified certificate proves
          v
    ACCEPT <verdict> + certificate file, or REJECT + a distinct exit code
```

It does **not** demonstrate, and this repository does not claim, that
any real regional/tracking evidence has been correctly translated into
`(D, r, L)` in the first place -- the instance files here are the same
small, hand-verified affine-rational examples already used throughout
`tests/generator_fixtures.py`. A region-native adapter that performs
that translation is separate, out of scope here, and is this
repository's next milestone (see `docs/design/PROOF_CARRYING_
EXACTNESS_PROPOSAL.md`).

## Commit and toolchain versions

Captured from the actual run, in a clean clone of this repository:

```text
git commit:  db221711b3f31a6b61e3b3c38181964a0512ddb3 (db22171)
Python:      3.12.3
pytest:      9.1.1
```

No Rocq/OCaml toolchain is exercised by this demonstration -- the
entire `pce_assess.py` pipeline (`proof_carrying_exactness`,
`proof_carrying_exactness_generator`, `proof_carrying_exactness_assess`)
is pure Python with no compiled dependency, unlike the R21 demonstration
(`docs/R21_END_TO_END_DEMONSTRATION.md`).

Reproduction, in order:

```sh
git clone <this-repository-url> pce-fresh-clone
cd pce-fresh-clone
git checkout db22171
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## The four verdicts

Each instance below lives at `examples/pce_assess/<verdict>.json` and
shares the same small algebra already exercised throughout this
project's own test suite (`tests/generator_fixtures.py`).

### EXACT

```sh
$ python3 pce_assess.py examples/pce_assess/exact.json --certificate-out /tmp/exact-certificate.json
ACCEPT EXACT
Claim is invariant across every permitted repair.
Certificate verified independently.
$ echo $?
0
```

Certificate written to `/tmp/exact-certificate.json`:

```json
{"input_digest":"sha256:1d53c4f0d509d71e7edf2afe857d374b9eedbd69daf39a0c77ed381aa5d6eef2","instance":{"D":[["-1","1","0"],["0","-1","1"]],"L":[["-1","0","1"]],"policy":{"independent_pairs":[["row-0","row-1"]],"policy_version":"pce-policy/v1"},"provenance":{"edges":[],"vertices":["row-0","row-1"]},"r":["3","2"],"row_evidence_ids":{"0":"row-0","1":"row-1"}},"policy_digest":"sha256:75b88377a47918b349e281a303b53387185a116df475984449d460ce744a1569","schema":"proof-carrying-exactness/certificate/v1","verdict":"EXACT","witness":{"admissibility_witness":{"cuts":[{"left_not_reaches_right":["row-0"],"pair":["row-0","row-1"],"right_not_reaches_left":["row-1"]}]},"claimed_value":["5"],"factorisation_witness":[["1","1"]],"repair_witness":["-5","-2","0"]}}
```

### UNDERDETERMINED

```sh
$ python3 pce_assess.py examples/pce_assess/underdetermined.json --certificate-out /tmp/underdetermined-certificate.json
ACCEPT UNDERDETERMINED
A repair exists, but the declared claim changes along a permitted gauge direction.
Certificate verified independently.
$ echo $?
0
```

Certificate `input_digest`: `sha256:50c1cbf6ea9fd156c072637533fd937d957f1085858f02ec95ef41dad1573779`

### OBSTRUCTED

```sh
$ python3 pce_assess.py examples/pce_assess/obstructed.json --certificate-out /tmp/obstructed-certificate.json
ACCEPT OBSTRUCTED
No permitted repair reconciles the evidence with the declared adjustments.
Certificate verified independently.
$ echo $?
0
```

Certificate `input_digest`: `sha256:e4b1e621a7d20826c3819fd07d645971331ba71f38b35d099b802a903c66a13b`

### INADMISSIBLE

```sh
$ python3 pce_assess.py examples/pce_assess/inadmissible.json --certificate-out /tmp/inadmissible-certificate.json
ACCEPT INADMISSIBLE
An ancestry relation exists between evidence declared independent, so the declared admissibility policy does not hold.
Certificate verified independently.
$ echo $?
0
```

Certificate `input_digest`: `sha256:93cb61a7cfbc9af08d5cd28d7d8e150ba1749b3de48800a859621b7d37b19011`

## Deterministic certificate bytes across separate runs

Three separate `pce_assess.py` invocations over the identical EXACT
instance, each a fresh process:

```sh
$ python3 pce_assess.py examples/pce_assess/exact.json --certificate-out /tmp/exact-certificate.json
$ python3 pce_assess.py examples/pce_assess/exact.json --certificate-out /tmp/exact-certificate-run2.json
$ python3 pce_assess.py examples/pce_assess/exact.json --certificate-out /tmp/exact-certificate-run3.json
$ sha256sum /tmp/exact-certificate.json /tmp/exact-certificate-run2.json /tmp/exact-certificate-run3.json
455aa0faba87911ff90745150ceffa433fe1d4db4e23ff9411970cade6d7800b  /tmp/exact-certificate.json
455aa0faba87911ff90745150ceffa433fe1d4db4e23ff9411970cade6d7800b  /tmp/exact-certificate-run2.json
455aa0faba87911ff90745150ceffa433fe1d4db4e23ff9411970cade6d7800b  /tmp/exact-certificate-run3.json
```

Byte-identical across all three runs.

## Direct acceptance by the production verifier

The same certificate, verified again with no CLI or assess layer
involved at all -- calling `proof_carrying_exactness.verify_
certificate_bytes` directly, exactly as any independent third party
could:

```sh
$ python3 -c "
from proof_carrying_exactness import verify_certificate_bytes
data = open('/tmp/exact-certificate.json', 'rb').read()
result = verify_certificate_bytes(data)
print('accepted:', result.accepted)
print('verdict:', result.verdict)
print('reason:', result.reason)
"
accepted: True
verdict: EXACT
reason: ACCEPT
```

## One tampered certificate, rejected

The EXACT certificate above, with its `claimed_value` witness field
changed after generation, verified directly (no CLI involved):

```sh
$ python3 -c "
import json
from proof_carrying_exactness import verify_certificate_bytes

cert = json.loads(open('/tmp/exact-certificate.json', 'rb').read())
cert['witness']['claimed_value'] = ['999999']
tampered = json.dumps(cert).encode('utf-8')

result = verify_certificate_bytes(tampered)
print('accepted:', result.accepted)
print('verdict:', result.verdict)
print('reason:', result.reason)
"
accepted: False
verdict: None
reason: M @ r != claimed_value -- the claim map's value does not follow from the residue alone
```

## One malicious-generator simulation, rejected by the assessment layer

This is the load-bearing scenario: a generator that no longer gates
its own release (or has been replaced by something actively
malicious), returning a certificate with correctly-bound digests but a
bogus `claimed_value`. `proof_carrying_exactness_assess.assess.
generate_certificate` is monkeypatched to simulate exactly that --
there is no other way to make the real `proof_carrying_exactness_
generator.generate_certificate` return unverified bytes, since it has
no argument or mode that skips its own release gate. `assess_instance`'s
own, independent, second call to `verify_certificate_bytes` is what
catches it:

```sh
$ python3 - << 'PYEOF'
import json
from fractions import Fraction

import proof_carrying_exactness_assess.assess as assess_module
from proof_carrying_exactness_assess import assess_instance
from proof_carrying_exactness.digests import compute_input_digest, compute_policy_digest

D = [[Fraction(-1), Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1), Fraction(1)]]
r = [Fraction(3), Fraction(2)]
L = [[Fraction(-1), Fraction(0), Fraction(1)]]
provenance = {"vertices": ["row-0", "row-1"], "edges": []}
policy = {"independent_pairs": [["row-0", "row-1"]], "policy_version": "pce-policy/v1"}
row_evidence_ids = {"0": "row-0", "1": "row-1"}

fake_certificate = json.dumps({
    "schema": "proof-carrying-exactness/certificate/v1",
    "verdict": "EXACT",
    "input_digest": compute_input_digest(D, r, L, provenance, row_evidence_ids, None),
    "policy_digest": compute_policy_digest(policy),
    "instance": {
        "D": [["-1", "1", "0"], ["0", "-1", "1"]],
        "r": ["3", "2"],
        "L": [["-1", "0", "1"]],
        "provenance": provenance,
        "policy": policy,
        "row_evidence_ids": row_evidence_ids,
    },
    "witness": {
        "repair_witness": ["-5", "-2", "0"],
        "factorisation_witness": [["1", "1"]],
        "claimed_value": ["999999"],  # correct digests, but a bogus claimed value
        "admissibility_witness": {
            "cuts": [{"pair": ["row-0", "row-1"], "left_not_reaches_right": ["row-0"], "right_not_reaches_left": ["row-1"]}]
        },
    },
}).encode("utf-8")

assess_module.generate_certificate = lambda instance: fake_certificate

instance = json.load(open("examples/pce_assess/exact.json"))
result = assess_instance(json.dumps(instance).encode("utf-8"))

print("accepted:", result.accepted)
print("verdict:", result.verdict)
print("certificate_bytes:", result.certificate_bytes)
print("summary:", result.summary)
print("reason:", result.reason)
PYEOF
accepted: False
verdict: None
certificate_bytes: None
summary: The generated certificate was rejected by independent verification.
reason: verification_rejected: M @ r != claimed_value -- the claim map's value does not follow from the residue alone
```

`certificate_bytes` is `None` -- nothing was released, exactly as
`tests/test_pce_assess_fail_closed.py::test_cli_never_bypasses_the_
verifier` already proves for the CLI itself.

## Fresh-clone reproduction

The exact sequence used to capture every command and output above:

```sh
git clone <this-repository-url> pce-fresh-clone
cd pce-fresh-clone
git checkout db22171
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python3 pce_assess.py examples/pce_assess/exact.json --certificate-out /tmp/exact-certificate.json
python3 pce_assess.py examples/pce_assess/underdetermined.json --certificate-out /tmp/underdetermined-certificate.json
python3 pce_assess.py examples/pce_assess/obstructed.json --certificate-out /tmp/obstructed-certificate.json
python3 pce_assess.py examples/pce_assess/inadmissible.json --certificate-out /tmp/inadmissible-certificate.json
pytest -q tests/test_pce_assess_cli.py tests/test_pce_assess_fail_closed.py tests/test_pce_assess_demonstration.py
```

`tests/test_pce_assess_demonstration.py` pins the exact `input_digest`
values and verdicts recorded above against the committed
`examples/pce_assess/*.json` fixtures; if a future change to the
generator, the verifier, or the digest scheme ever changes what these
four instances certify to, that test fails rather than letting this
document silently go stale.
