#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-localhost}"
PORT="${2:-5432}"
TIMEOUT="${3:-30}"

echo "Waiting for service at $HOST:$PORT (timeout: ${TIMEOUT}s)..."

for i in $(seq 1 "$TIMEOUT"); do
    if nc -z "$HOST" "$PORT" 2>/dev/null || (echo > /dev/tcp/"$HOST"/"$PORT") 2>/dev/null; then
        echo "Service at $HOST:$PORT is ready!"
        exit 0
    fi
    sleep 1
done

echo "Timed out waiting for service at $HOST:$PORT"
exit 1
