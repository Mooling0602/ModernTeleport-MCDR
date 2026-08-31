#!/usr/bin/env bash
source .venv/bin/activate
echo "----- Running ty check -----"
ty check src/
echo "----- Running ruff check -----"
ruff check src/
echo "----- Running ruff format (check only) -----"
format_output=$(ruff format --check src/ 2>&1)
format_status=$?
echo "$format_output"
if grep -q "would be reformatted" <<<"$format_output"; then
  echo 'Rerun `ruff format src/` \(without argument `--check`\) to apply format changes from ruff.'
  echo 'For more pep style format, run `./format_code.sh`'
fi
exit $format_status
