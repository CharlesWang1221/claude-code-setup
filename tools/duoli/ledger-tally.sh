#!/bin/bash
# 多利：ledger-tally（純腳本，不呼叫 AI）。加 --dry-run 只印出內容。
exec python3 -I "$(cd "$(dirname "$0")" && pwd)/duoli.py" ledger "$@"
