#!/usr/bin/env bash
# Format docstrings (docformatter) and code (ruff format).
#
# Order matters: docformatter runs FIRST and ruff format runs LAST.
# docformatter 1.7.8 has a bug (the loop bound `_num_tokens - index - 1` in
# _get_attribute_docstring_newlines) that makes its "two blank lines before a
# top-level def/class" rule miss docstrings in the second half of the token
# stream, so it collapses the blank lines that ruff format requires --
# the two tools would ping-pong forever. Making ruff format the final
# arbiter keeps the tree stable; the default mode below therefore checks
# convergence of the *combined* pipeline instead of `docformatter --check`
# alone.
#
# Usage:
#   ./format_code.sh          check only (print a diff if not converged)
#   ./format_code.sh --apply  apply formatting in-place
#
# NOTE: run from the repo root; both tools read options from pyproject.toml
# in the current working directory.
set -euo pipefail
source .venv/bin/activate

# docformatter exits 3 ("format required") after successfully rewriting files
# in-place; treat 0 and 3 as success, propagate anything else.
run_docformatter() {
    local ec=0
    docformatter "$@" || ec=$?
    if [[ $ec -ne 0 && $ec -ne 3 ]]; then
        echo "docformatter failed with exit code $ec" >&2
        return "$ec"
    fi
    return 0
}

if [[ "${1:-}" == "--apply" ]]; then
    run_docformatter --in-place -r src/
    ruff format src/
    echo "Formatted: docformatter (docstrings) + ruff format (code)."
else
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    cp -r src "$tmp/src"
    run_docformatter --in-place -r "$tmp/src"
    ruff format --config pyproject.toml "$tmp/src" >/dev/null
    if diff -ru --exclude=__pycache__ src "$tmp/src" >"$tmp/diff.txt"; then
        echo "Docstring formatting converged (docformatter + ruff format)."
    else
        sed "s|$tmp/src|src (after formatting)|g" "$tmp/diff.txt"
        echo
        echo "Working tree is not converged. Run './format_code.sh --apply' to fix."
        exit 1
    fi
fi
