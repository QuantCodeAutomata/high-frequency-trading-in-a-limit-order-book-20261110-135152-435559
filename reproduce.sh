#!/usr/bin/env bash
# Runs the test suite and every experiment of the Avellaneda-Stoikov
# inventory market-making replication, overwriting results/ in place.
set -uo pipefail

python -m pytest || exit 1

python -m exp.exp1
python -m exp.exp2
python -m exp.exp3
python -m exp.exp4
