#!/bin/bash

notice() {
    echo -e "$@" 1>&2
}

die() {
    notice "$@"
    exit 1
}

usage() {
    die "Usage: \n  ${0##*/} list\n  ${0##*/} start|stop|status name"
}

svc_running() {
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
    (
        flock -n 9 || die "Cannot acquire lock on ${PIDFILE}.lock"
        if svc_running; then
            die "Service $1 is already running!"
        fi
        if ! which $1 &>/dev/null; then
            die "Executable not found: $1"
        fi
        notice -n "Starting ${1}..."
        setsid $1 &>/dev/null &
        echo $! 1>"$PIDFILE"
        chmod 600 "$PIDFILE"
        sleep 0.1
        if svc_running 1>/dev/null; then
            notice "OK"
        else
            rm -f "$PIDFILE"
            die "FAIL"
        fi
    ) 9>"${PIDFILE}.lock"
    rm -f "${PIDFILE}.lock"
}

svcstop() {
    if svc_running; then
        notice -n "Stopping $1 gracefully..."
        pkill -s $(<"$PIDFILE")
        I=0
        while svc_running 1>/dev/null && [[ $I -le 5 ]]; do
            sleep 1
            let I++
        done
        if svc_running 1>/dev/null; then
            notice 'FAIL'
            notice -n "Killing ${1}..."
            pkill -9 -s $(<"$PIDFILE")
            I=0
            while svc_running 1>/dev/null && [[ $I -le 5 ]]; do
                sleep 1
                let I++
            done
            if svc_running 1>/dev/null; then
                die 'FAIL'
            fi
        fi
        notice 'OK'
        rm -f "$PIDFILE"
    else
        die "Service $1 is not running!"
    fi
}

svcstatus() {
    if svc_running; then
        pstree -aclnp $(<"$PIDFILE")
    else
        return 1
    fi
}

svclist() {
    for PIDFILE in ${HOME}/.svctl.*.pid; do
        [[ -r $PIDFILE ]] || continue
        svcstatus
    done
}

if [[ -z "$LOGNAME" ]]; then
    LOGNAME=$(id -un)
    if [[ -z "$LOGNAME" ]]; then
        die "LOGNAME variable is not set, can't work without it."
    fi
fi

if [[ -n "$2" ]]; then
    PIDFILE=${2##*/}
    PIDFILE="${HOME}/.svctl.${PIDFILE//[.-]/}.pid"
elif [[ "$1" != "list" ]]; then
    usage
fi

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
    list)
        svclist
    ;;
    *)
        usage
    ;;
esac
