#!/usr/bin/env bash
# NetScan — Network Anomaly Detection Launcher (Linux / Kali)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Preserve user site-packages when running under sudo on Kali
if [ -n "$SUDO_USER" ]; then
    USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    for pydir in "$USER_HOME"/.local/lib/python3.*/site-packages; do
        if [ -d "$pydir" ]; then
            export PYTHONPATH="$pydir${PYTHONPATH:+:$PYTHONPATH}"
        fi
    done
fi

python3 netscan.py "$@"

