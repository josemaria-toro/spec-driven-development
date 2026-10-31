#!/usr/bin/env bash
# Starts and stops the backend. Usage: ./app.sh start|stop
#
# The backend has no inbound adapter yet (HTTP or CLI), so there is nothing to run.
# Complete this script when the adapter exists, following apps/frontend/app.sh.
set -euo pipefail

usage() {
  echo "Usage: $0 start|stop" >&2
  exit 2
}

[[ $# -eq 1 ]] || usage
case "$1" in
  start)
    echo "the backend has no inbound adapter (HTTP or CLI) yet: there is nothing to start" >&2
    exit 1
    ;;
  stop)
    echo "the backend is not running: it has no inbound adapter (HTTP or CLI) yet"
    ;;
  *) usage ;;
esac
