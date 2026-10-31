#!/usr/bin/env bash
# Starts and stops the frontend development server in the background.
# Usage: ./app.sh start|stop     (PORT overrides the default port)
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$APP_DIR/.run"
PID_FILE="$RUN_DIR/frontend.pid"
LOG_FILE="$RUN_DIR/frontend.log"
PORT="${PORT:-5173}"
START_TIMEOUT_SECONDS=30
STOP_TIMEOUT_SECONDS=10

usage() {
  echo "Usage: $0 start|stop" >&2
  exit 2
}

# The server runs in its own process group (see start), so the PID is also its group id.
# Checking that guards against stopping an unrelated process that reused the PID.
is_running() {
  [[ -f "$PID_FILE" ]] || return 1
  local pid
  pid="$(<"$PID_FILE")"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  [[ "$(ps -o pgid= -p "$pid" | tr -d ' ')" == "$pid" ]]
}

port_is_listening() {
  (exec 3<>"/dev/tcp/localhost/$PORT") 2>/dev/null
}

start() {
  if is_running; then
    echo "frontend already running (pid $(<"$PID_FILE")) at http://localhost:$PORT"
    return 0
  fi
  rm -f "$PID_FILE"

  command -v pnpm >/dev/null || { echo "pnpm is not installed" >&2; exit 1; }
  [[ -d "$APP_DIR/node_modules" ]] || {
    echo "dependencies are missing: run 'pnpm install --frozen-lockfile' in $APP_DIR" >&2
    exit 1
  }

  mkdir -p "$RUN_DIR"
  cd "$APP_DIR"
  setsid nohup pnpm dev --port "$PORT" --strictPort >"$LOG_FILE" 2>&1 < /dev/null &
  echo "$!" >"$PID_FILE"

  local waited=0
  until port_is_listening; do
    if ! is_running; then
      echo "frontend failed to start; last log lines:" >&2
      tail -n 20 "$LOG_FILE" >&2
      rm -f "$PID_FILE"
      exit 1
    fi
    if ((waited >= START_TIMEOUT_SECONDS)); then
      echo "frontend did not listen on port $PORT within ${START_TIMEOUT_SECONDS}s" >&2
      stop
      exit 1
    fi
    sleep 1
    waited=$((waited + 1))
  done
  echo "frontend started (pid $(<"$PID_FILE")) at http://localhost:$PORT, log: $LOG_FILE"
}

stop() {
  if ! is_running; then
    rm -f "$PID_FILE"
    echo "frontend is not running"
    return 0
  fi
  local pid waited=0
  pid="$(<"$PID_FILE")"
  kill -TERM -- "-$pid" 2>/dev/null || true
  while kill -0 "$pid" 2>/dev/null; do
    if ((waited >= STOP_TIMEOUT_SECONDS)); then
      kill -KILL -- "-$pid" 2>/dev/null || true
      break
    fi
    sleep 1
    waited=$((waited + 1))
  done
  rm -f "$PID_FILE"
  echo "frontend stopped"
}

[[ $# -eq 1 ]] || usage
case "$1" in
  start) start ;;
  stop) stop ;;
  *) usage ;;
esac
