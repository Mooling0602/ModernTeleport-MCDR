#!/usr/bin/env bash
# Run all static checks: ty, ruff lint, ruff format and docstring formatting.
# Exit status is non-zero if any check fails.
source .venv/bin/activate
status=0

echo "----- Running ty check -----"
ty check src/ || status=1

echo "----- Running ruff check -----"
ruff check src/ || status=1

echo "----- Running ruff format (check only) -----"
format_output=$(ruff format --check src/ 2>&1)
format_status=$?
echo "$format_output"
if grep -q "would be reformatted" <<<"$format_output"; then
    echo 'Rerun `ruff format src/` \(without argument `--check`\) to apply format changes from ruff.'
    echo 'For full formatting, run `./format_code.sh --apply`'
fi
[[ $format_status -eq 0 ]] || status=1

echo "----- Running docstring format check -----"
./format_code.sh || status=1

exit $status
