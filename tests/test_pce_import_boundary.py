"""
Mechanical import-boundary test for the proof_carrying_exactness
production verifier package, matching the discipline this repository's
own inherited `tests/test_stonesoup_import_boundary.py` already
established: an AST scan of every module's own source, not merely a
docstring claim, proving the verifier never imports discovery/search
machinery.

Forbidden anywhere in proof_carrying_exactness/:
  - the entire r21_repair_or_separator module (Gauss-Jordan elimination
    with y-tracking -- a solver);
  - rational_linear_algebra.nullspace_over_Q / solve_over_Q (both also
    perform elimination -- for a kernel basis or a particular solution
    respectively);
  - any graph-search library (networkx or similar);
  - any certificate generator (pce_certificate_spike or similarly named
    modules from either untracked spike).

Permitted from rational_linear_algebra: mat_vec, mat_mat, row_vec_mat,
dot, is_zero -- direct evaluation of an already-fully-specified product,
never an elimination or search.
"""

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = REPO_ROOT / "proof_carrying_exactness"

FORBIDDEN_MODULES = {"r21_repair_or_separator", "networkx", "igraph", "pce_certificate_spike", "pce_semantics"}
ALLOWED_FROM_RATIONAL_LINEAR_ALGEBRA = {"mat_vec", "mat_mat", "row_vec_mat", "dot", "is_zero"}
FORBIDDEN_FROM_RATIONAL_LINEAR_ALGEBRA = {"nullspace_over_Q", "solve_over_Q"}


def _package_python_files():
    return sorted(PACKAGE_DIR.glob("*.py"))


def test_package_exists_and_is_nonempty():
    files = _package_python_files()
    assert files
    assert (PACKAGE_DIR / "__init__.py") in files


def test_no_file_imports_a_forbidden_module():
    for path in _package_python_files():
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


def test_no_file_imports_forbidden_names_from_rational_linear_algebra():
    for path in _package_python_files():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "rational_linear_algebra":
                imported_names = {alias.name for alias in node.names}
                forbidden = imported_names & FORBIDDEN_FROM_RATIONAL_LINEAR_ALGEBRA
                assert not forbidden, f"{path.name} imports forbidden rational_linear_algebra name(s): {forbidden}"
                unexpected = imported_names - ALLOWED_FROM_RATIONAL_LINEAR_ALGEBRA
                assert not unexpected, (
                    f"{path.name} imports unrecognised rational_linear_algebra name(s) {unexpected} -- "
                    f"update ALLOWED_FROM_RATIONAL_LINEAR_ALGEBRA in this test if this is a deliberate, "
                    f"reviewed addition, not silently"
                )


def test_no_dynamic_import_of_forbidden_modules():
    dynamic_names = {"__import__", "import_module"}
    for path in _package_python_files():
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


def test_importing_the_package_does_not_pull_in_the_solver_module():
    import sys

    was_present_before = "r21_repair_or_separator" in sys.modules
    import proof_carrying_exactness  # noqa: F401

    if not was_present_before:
        assert "r21_repair_or_separator" not in sys.modules, (
            "importing proof_carrying_exactness pulled in r21_repair_or_separator transitively"
        )
