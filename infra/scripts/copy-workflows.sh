#!/usr/bin/env bash
set -euo pipefail

echo "Deploying CI workflows from infra/ci/ to .github/workflows/..."
mkdir -p .github/workflows
cp -v infra/ci/*.yml .github/workflows/
echo "CI workflows successfully copied to .github/workflows/"
