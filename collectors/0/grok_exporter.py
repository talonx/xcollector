#!/usr/bin/env python
import os
import re
import requests
import signal
import subprocess
import sys
import time
import yaml
from StringIO import StringIO

from collectors.etc import grok_exporter_conf

COLLECTION_INTERVAL_SECONDS = 15
processes = []
urls_vs_patterns = {}


class Proc():
    def __init__(self, proc):
        self.proc = proc
        self.alive = True


def launch_grokker(exporter_dir, config):
    try:
        # No need to set the setsid or do pgkill here since we know grokker does not launch any subprocesses
        proc = subprocess.Popen([exporter_dir + '/grok_exporter', '-config',
                                config],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True,
                                cwd=exporter_dir)
        processes.append(Proc(proc))

	with open(config, 'r') as stream:
	    try:
        	ycfg = yaml.load(stream)
    	    except yaml.YAMLError as exc:
		print("Type error: {0}".format(exc))
        	die()

	metrics = ycfg['metrics']

        patterns = []
        for metric in metrics:
            metric_name = metric['name']
	    if metric['type'] in ('histogram','summary'):
#		print ((metric_name + '_count'))
		pattern = re.compile('^(%s)([^\}]*[\}]*)(\s+\d+)' % (metric_name + '_count'))
		patterns.append(pattern)
#		print ((metric_name + '_sum'))
		pattern = re.compile('^(%s)([^\}]*[\}]*)(\s+\d+)' % (metric_name + '_sum'))
		patterns.append(pattern)
#	    print((metric_name))
            pattern = re.compile('^(%s)([^\}]*[\}]*)(\s+\d+)' % metric_name)
            patterns.append(pattern)
        port = ycfg['server']['port']
#        print(port)
        urls_vs_patterns['http://localhost:%d/metrics' % port] = patterns
    except Exception as e:
#	print("Type error: {0}".format(e))
        die()


def check_procs():
    '''
    This seems to be the only way of checking if the process did not launch properly.
    Checking for pid returns a valid id even when the process is defunct (e.g. another grokker is already
    running). poll returns the exitcode after a while, not immediately, since it's not populated until after the
    subprocess has failed.
    '''
    found = False
    for proc in processes:
        p = proc.proc
        poll = p.poll()
        if poll is not None:  # has exited
            proc.alive = False
            found = True
    if found:
        die()


def start_poller():
    check_procs()
    while True:
        time.sleep(COLLECTION_INTERVAL_SECONDS)
        fetch_metrics()


def main():
    signal.signal(signal.SIGTERM, die)
    exporter_dir = grok_exporter_conf.get_grok_exporter_dir()
    config_files = grok_exporter_conf.get_config_files()
    for config_file in config_files:
        launch_grokker(exporter_dir, config_file)
    start_poller()


def die(signum=signal.SIGTERM, stack_frame=None):
    kill_children(signum)
    exit(13) # Signal to tcollector


def kill_children(signum):
    for p in processes:
        try:
            inner_proc = p.proc
            if p.alive:
                os.kill(inner_proc.pid, signum)
        except:
            pass


def fetch_metrics():
    for (url, patterns) in urls_vs_patterns.iteritems():
        try:
            response = requests.get(url)
            timestamp = int(time.time())
	    global buf
            buf = StringIO(response.text)
            found = False
#	    print(len(patterns))
            for line in buf.readlines():
                for pattern in patterns:
                    matcher = pattern.search(line)
                    if matcher is not None:  # TODO would checking for startswith be more efficient here?
#			print('Pattern matched on ' + line)
                        found = True
#			print (found)
                        g = matcher.groups()
			if g[1].startswith('_count'):
				continue
			elif g[1].startswith('_sum'):
				continue
#			print(g)
                        tags = ' '.join(g[1].replace('"', '').strip('{}').split(','))
 			if '::_' in g[0]:
#				print('Found pattern')
				extratags = g[0].split('::_');
#				print(extratags)
#				g[0] = extratags[0]
#				print(g[0])
#				print('Here')
				global finalmetricname
				finalmetricname = extratags[0]
#				print(finalmetricname)
				for i, extratag in enumerate(extratags):
					if i == 0:
						continue;
					elif extratag.startswith('_'):
						finalmetricname += extratag
					else:
						tags += ' ' + extratag.replace('_', '=')
				buf = '%s %s%s %s' % (finalmetricname, timestamp, g[2], tags)
			else:
	                        buf = '%s %s%s %s' % (g[0], timestamp, g[2], tags)
                        sys.stdout.write(buf)
                        sys.stdout.write('\n')
            if not found:
                die()
            sys.stdout.flush()
#	except UnboundLocalError as err:
#	    print("Type error: {0}".format(err))
#	except TypeError as err:
#	    print("Type error: {0}".format(err))
        except:
	    print("Unexpected error:", sys.exc_info()[0])
            die()


if __name__ == '__main__':
    main()

