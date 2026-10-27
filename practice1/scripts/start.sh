#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 src/main.py --vfs ./vfs/files.csv --script ./scripts/commands5.txt "$@"
