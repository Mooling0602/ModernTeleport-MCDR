#!/usr/bin/env bash
source .venv/bin/activate
docformatter --in-place -r src/ --wrap-summaries 72 --wrap-descriptions 72
