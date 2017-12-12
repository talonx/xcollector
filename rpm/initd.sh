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
  for file in "$PIDFILE" "$LOGFILE"; do
    parentdir=`dirname "$file"`
    if [ ! -d "$parentdir" ]; then
      install -m 755 -o $RUN_AS_USER -g $RUN_AS_GROUP -d $parentdir
    fi
  done
}

start() {
  echo -n $"Starting $prog: "
  sanity_check || return $?
  find `dirname ${TCOLLECTOR}` -name '*.pyc' -delete
  daemon --user=$RUN_AS_USER --pidfile=$PIDFILE $TCOLLECTOR $OPTIONS
  RETVAL=$?
  echo
  return $RETVAL
}

# When stopping xcollector a delay of ~15 seconds before SIGKILLing the
# process so as to give enough time for xcollector to SIGKILL any errant
# collectors.
stop() {
  echo -n $"Stopping $prog: "
  sanity_check || return $?
  killproc -p $PIDFILE -d 15 $TCOLLECTOR
  RETVAL=$?
  echo
  return $RETVAL
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
