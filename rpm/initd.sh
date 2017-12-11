#!/bin/bash
#
# xcollector   Startup script for the xcollector monitoring agent
#
# chkconfig:   2345 15 85
# description: XCollector - Data collection agent for apptuit.ai
# processname: xcollector
# pidfile: /var/run/xcollector.pid
#
### BEGIN INIT INFO
# Provides: xcollector
# Required-Start: $local_fs $remote_fs $network $named
# Required-Stop: $local_fs $remote_fs $network
# Short-Description: XCollector - Data collection agent for apptuit.ai
# Description: XCollector - Data collection agent for apptuit.ai
### END INIT INFO

# Source function library.
. /etc/init.d/functions

THIS_HOST=`hostname`
TCOLLECTOR=${TCOLLECTOR-/usr/local/xcollector/xcollector.py}
PIDFILE=${PIDFILE-/var/run/xcollector/xcollector.pid}
LOGFILE=${LOGFILE-/var/log/xcollector/xcollector.log}

RUN_AS_USER=${RUN_AS_USER-xcollector}
RUN_AS_GROUP=${RUN_AS_GROUP-xcollector}

prog=xcollector
if [ -f /etc/sysconfig/$prog ]; then
  . /etc/sysconfig/$prog
fi

lockfile=${LOCKFILE-/var/lock/subsys/xcollector}

EXTRA_TAGS_OPTS=""
for TV in $EXTRA_TAGS; do
    EXTRA_TAGS_OPTS=${EXTRA_TAGS_OPTS}" -t ${TV}"
done

if [ -z "$OPTIONS" ]; then
  OPTIONS="--daemonize"
  OPTIONS="$OPTIONS -t host=$THIS_HOST -P $PIDFILE"
  OPTIONS="$OPTIONS $EXTRA_TAGS_OPTS"
fi

sanity_check() {
  for i in "$PIDFILE" "$LOGFILE"; do
    # If the file doesn't exist, check that we have write access to its parent
    # directory to be able to create it.
    test -e "$i" || i=`dirname "$i"`
    test -w "$i" || {
      echo >&2 "error: Cannot write to $i"
      return 4
    }
  done
}

start() {
  echo -n $"Starting $prog: "
  sanity_check || return $?
  daemon --user=$RUN_AS_USER --pidfile=$PIDFILE $TCOLLECTOR $OPTIONS
  RETVAL=$?
  echo
  [ $RETVAL = 0 ] && touch ${lockfile}
  return $RETVAL
}

# When stopping xcollector a delay of ~15 seconds before SIGKILLing the
# process so as to give enough time for xcollector to SIGKILL any errant
# collectors.
stop() {
  echo -n $"Stopping $prog: "
  sanity_check || return $?
  find `dirname ${TCOLLECTOR}` -name '*.pyc' -delete
  killproc -p $PIDFILE -d 15 $TCOLLECTOR
  RETVAL=$?
  echo
  [ $RETVAL = 0 ] && rm -f ${lockfile} $PIDFILE
}

# See how we were called.
case "$1" in
  start) start;;
  stop) stop;;
  status)
    status -p $PIDFILE $TCOLLECTOR
    RETVAL=$?
    ;;
  restart|force-reload|reload) stop && start;;
  condrestart|try-restart)
    if status -p $PIDFILE $TCOLLECTOR >&/dev/null; then
      stop && start
    fi
    ;;
  *)
    echo $"Usage: $prog {start|stop|status|restart|force-reload|reload|condrestart|try-restart}"
    RETVAL=2
esac

exit $RETVAL
