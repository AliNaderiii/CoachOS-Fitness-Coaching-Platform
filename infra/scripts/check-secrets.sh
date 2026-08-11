#!/usr/bin/env bash
set -euo pipefail

echo "======================================================"
echo " CoachOS Security & Language Compliance Scanner"
echo "======================================================"

EXIT_CODE=0

echo "[1/4] Checking for forbidden Arabic locale resources..."
# Check for any Arabic locale files (ar.json, ar-*.json, etc.)
ARABIC_FILES=$(find . -type f \( -name "*ar-*.json" -o -name "*ar.json" -o -name "*ar.po" -o -name "*ar.mo" \) -not -path "*/node_modules/*" -not -path "*/.venv/*" || true)
if [ -n "$ARABIC_FILES" ]; then
    echo "❌ ERROR: Arabic locale files detected:"
    echo "$ARABIC_FILES"
    EXIT_CODE=1
else
    echo "✅ PASS: No Arabic locale files found."
fi

echo "[2/4] Scanning for potential committed secrets..."
# Common secret patterns
SECRETS_FOUND=0
PATTERNS=(
    "AKIA[0-9A-Z]{16}"                    # AWS Access Key
    "AIza[0-9A-Za-z\\-_]{35}"             # Google API Key
    "ghp_[0-9a-zA-Z]{36}"                 # GitHub Personal Access Token
    "BEGIN (RSA|OPENSSH|PGP) PRIVATE KEY" # Private Keys
)

for PATTERN in "${PATTERNS[@]}"; do
    MATCHES=$(grep -rE "$PATTERN" . --exclude-dir={.git,.venv,node_modules,.next,build,dist} --exclude="check-secrets.sh" 2>/dev/null || true)
    if [ -n "$MATCHES" ]; then
        echo "❌ ERROR: Potential secret match for pattern '$PATTERN':"
        echo "$MATCHES"
        SECRETS_FOUND=1
        EXIT_CODE=1
    fi
done

if [ "$SECRETS_FOUND" -eq 0 ]; then
    echo "✅ PASS: No private secret patterns detected."
fi

echo "[3/4] Checking frontend public environment variable safety..."
# Ensure frontend .env files don't contain non-NEXT_PUBLIC vars
if [ -f "frontend/.env" ]; then
    BAD_VARS=$(grep -v "^#" "frontend/.env" | grep -v "^$" | grep -v "^NEXT_PUBLIC_" || true)
    if [ -n "$BAD_VARS" ]; then
        echo "❌ ERROR: Non-public environment variables found in frontend/.env:"
        echo "$BAD_VARS"
        EXIT_CODE=1
    else
        echo "✅ PASS: Frontend environment variables strictly use NEXT_PUBLIC_ prefix."
    fi
else
    echo "ℹ️ INFO: No frontend/.env file found (safe default)."
fi

echo "[4/4] Verifying Web App Manifest validity..."
if [ -f "frontend/public/manifest.json" ]; then
    node -e '
        const fs = require("fs");
        const manifest = JSON.parse(fs.readFileSync("frontend/public/manifest.json", "utf8"));
        if (!manifest.name || !manifest.short_name || !manifest.icons || !manifest.start_url) {
            console.error("❌ Manifest missing required PWA fields");
            process.exit(1);
        }
        console.log("✅ PASS: Web App Manifest has required PWA fields.");
    ' || EXIT_CODE=1
fi

echo "======================================================"
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "🎉 ALL COMPLIANCE CHECKS PASSED"
else
    echo "⚠️ ONE OR MORE CHECKS FAILED"
fi
echo "======================================================"

exit "$EXIT_CODE"
