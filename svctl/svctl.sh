#!/bin/bash

notice() {
  echo "$@" 1>&2
}

usage() {
  notice "Usage: ${0##*/} start|stop|status name"
  exit 1
}

running() {
  if [[ -e "$PIDFILE" ]]; then
    PID=$(<"$PIDFILE")
    if [[ $PID =~ ^[0-9]+$ ]]; then
      if [[ $(pgrep -c -u "$LOGNAME" -s $PID) -gt 0 ]]; then
        return 0
      fi
    else
      notice "File '$PIDFILE' is corrupt."
    fi
  fi
  return 1
}

svcstart() {
  if running $1; then
    notice "Service $1 is already running!"
    exit 2
  fi
  notice -n "Starting ${1}..."
  setsid $1 1>/dev/null 2>&1 &
  echo $! 1>"$PIDFILE"
  sleep 0.1
  if running $1 1>/dev/null; then
    notice "OK"
  else
    notice "FAIL"
    rm -f "$PIDFILE"
    exit 3
  fi
}

svcstop() {
  if running $1; then
    notice -n "Stopping $1 gracefully..."
    pkill -s $(<"$PIDFILE")
    I=0
    while running $1 1>/dev/null && [[ $I -le 5 ]]; do
      sleep 1
      let I++
    done
    if running $1 1>/dev/null; then
      notice 'FAIL'
      notice -n "Killing ${1}..."
      pkill -9 -s $(<"$PIDFILE")
      I=0
      while running $1 1>/dev/null && [[ $I -le 5 ]]; do
        sleep 1
        let I++
      done
      if running $1 1>/dev/null; then
        notice 'FAIL'
        exit 3
      fi
    fi
    notice 'OK'
    rm -f "$PIDFILE"
  else
    notice "Service $1 is not running!"
    exit 2
  fi
}

svcstatus() {
  if running $1; then
    pstree -aclnp $(<"$PIDFILE")
  else
    exit 1
  fi
}

if [[ $# -lt 2 ]]; then
  usage
fi

if [[ -z "$LOGNAME" ]]; then
  LOGNAME=$(id -un)
  if [[ -z "$LOGNAME" ]]; then
    notice "LOGNAME variable is not set, can't work without it."
    exit 1
  fi
fi

PIDFILE=${2##*/}
PIDFILE="/tmp/${LOGNAME}.${PIDFILE//[.-]/}.pid"

case $1 in
  start)
    svcstart $2
  ;;
  stop)
    svcstop $2
  ;;
  restart)
    svcstop $2
    svcstart $2
  ;;
  status)
    svcstatus $2
  ;;
  *)
    usage
  ;;
esac
