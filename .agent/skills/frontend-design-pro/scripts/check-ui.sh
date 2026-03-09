#!/usr/bin/env bash
set -euo pipefail

# Simple UI hygiene checks (example)
# Usage: ./check-ui.sh --help

if [[ "${1:-}" == "--help" ]]; then
  echo "Usage: ./check-ui.sh [path]"
  echo "Runs basic checks for TSX components and reports counts."
  exit 0
fi

TARGET="${1:-.}"

echo "Scanning: $TARGET"
echo "TSX files:"
find "$TARGET" -type f -name "*.tsx" | wc -l | awk '{print "  count:", $1}'

echo "Potentially large className usage (heuristic):"
grep -R --line-number "className=\".{140,}\"" "$TARGET" 2>/dev/null | head -n 20 || true
