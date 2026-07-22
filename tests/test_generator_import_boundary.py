"""
Mechanical import-boundary test between the production verifier
(`proof_carrying_exactness/`) and the untrusted generator
(`proof_carrying_exactness_generator/`), matching the AST-scan
discipline `tests/test_pce_import_boundary.py` already established for
the verifier's own boundary against solver/search machinery.

This test asserts the SYMMETRIC half that file does not cover: the
verifier package must never import the generator package, in either
direction, statically or dynamically. (The generator importing the
verifier is expected and required -- `generate_certificate` calls
`verify_certificate_bytes` before releasing any bytes -- so that
direction is deliberately not checked here.)
"""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERIFIER_PACKAGE_DIR = REPO_ROOT / "proof_carrying_exactness"
GENERATOR_PACKAGE_DIR = REPO_ROOT / "proof_carrying_exactness_generator"

FORBIDDEN_MODULES = {"proof_carrying_exactness_generator"}


def _verifier_python_files():
    return sorted(VERIFIER_PACKAGE_DIR.glob("*.py"))


def test_generator_package_exists_and_is_nonempty():
    files = sorted(GENERATOR_PACKAGE_DIR.glob("*.py"))
    assert files
    assert (GENERATOR_PACKAGE_DIR / "__init__.py") in files


def test_verifier_never_imports_the_generator_package():
    for path in _verifier_python_files():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    assert top not in FORBIDDEN_MODULES, f"{path.name} imports forbidden module {top!r}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    assert top not in FORBIDDEN_MODULES, f"{path.name} imports from forbidden module {top!r}"


def test_verifier_never_dynamically_imports_the_generator_package():
    dynamic_names = {"__import__", "import_module"}
    for path in _verifier_python_files():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                if func_name in dynamic_names:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            assert arg.value not in FORBIDDEN_MODULES, (
                                f"{path.name} dynamically imports forbidden module {arg.value!r}"
                            )


def test_importing_the_verifier_does_not_pull_in_the_generator_package():
    was_present_before = "proof_carrying_exactness_generator" in sys.modules
    import proof_carrying_exactness  # noqa: F401

    if not was_present_before:
        assert "proof_carrying_exactness_generator" not in sys.modules, (
            "importing proof_carrying_exactness pulled in proof_carrying_exactness_generator transitively"
        )
