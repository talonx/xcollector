#!/usr/bin/env python
import logging
import os
import re
import requests
import signal
import subprocess
import sys
import time
import yaml
import traceback

from StringIO import StringIO

from collectors.etc import grok_scraper_conf
from collectors.etc import metric_naming
from collectors.etc import yaml_conf

COLLECTION_INTERVAL_SECONDS = 15
processes = []
urls_vs_patterns = {}

METRIC_MAPPING = yaml_conf.load_collector_configuration('grok_metrics.yml')

logging.basicConfig(stream=sys.stderr)
LOG = logging.getLogger('grok_scraper')
LOG.setLevel(logging.INFO)

class Proc():
    def __init__(self, proc):
        self.proc = proc
        self.alive = True


def launch_grokker(exporter_dir, config, generate_debug_log):
    try:
        debug_log_fd = open(os.devnull, 'w')
        if generate_debug_log:
            debug_log_fd = None
        # No need to set the setsid or do pgkill here since we know grokker does not launch any subprocesses
        proc = subprocess.Popen([exporter_dir + '/grok_exporter', '-config',
                                 config],
                                stdout=debug_log_fd,
                                stderr=debug_log_fd,
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
            if metric['type'] in ('histogram', 'summary'):
                pattern = re.compile('^(%s)([^\}]*[\}]*)(\s+[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)' % (metric_name + '_count'))
                patterns.append(pattern)
                pattern = re.compile('^(%s)([^\}]*[\}]*)(\s+[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)' % (metric_name + '_sum'))
                patterns.append(pattern)
            pattern = re.compile('^(%s)([^\}]*[\}]*)(\s+[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)' % metric_name)
            patterns.append(pattern)
        host = ycfg['server']['host']
        port = ycfg['server']['port']
        urls_vs_patterns['http://%s:%d/metrics' % (host,port)] = patterns
    except Exception as e:
        traceback.print_exc()
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

def check_log_accessibility(config_file_path):
    with open(config_file_path, 'r') as stream:
        yconfig = None
        try:
            yconfig = yaml.load(stream)
        except yaml.YAMLError as exc:
            LOG.error("Error parsing grokker config: {0}".format(exc))
            die()
        if 'input' not in yconfig or 'path' not in yconfig['input']:
            LOG.error("Improper grokker config as argument")
            die()
        input_path = yconfig['input']['path']
        if not os.access(input_path, os.R_OK):
            LOG.error("The file " + input_path + " does not exist or xcollector does not have read permissions to it")
            die()
    return

def main():
    signal.signal(signal.SIGTERM, die)
    exporter_dir = grok_scraper_conf.get_grok_exporter_dir()
    scraper_dir = grok_scraper_conf.get_grok_scraper_config_dir()
    current_grok_scraper = os.path.basename(__file__)
    current_grok_scraper = current_grok_scraper[0:current_grok_scraper.index('.')]
    config_file_name = "grok_" + current_grok_scraper + ".yml"
    config_file_path = os.path.join(scraper_dir, config_file_name)
    check_log_accessibility(config_file_path)
    launch_grokker(exporter_dir, config_file_path, grok_scraper_conf.get_grok_exporter_debug())
    start_poller()


def die(signum=signal.SIGTERM, stack_frame=None):
    kill_children(signum)
    exit(13)  # Signal to tcollector


def kill_children(signum):
    for p in processes:
        try:
            inner_proc = p.proc
            if p.alive:
                os.kill(inner_proc.pid, signum)
        except:
            pass


def fetch_metrics():
    def format_metric_value(value):
        float_value = float(value)
        if float_value.is_integer():
            return int(float_value)
        else:
            return "{0:.3f}".format(float_value)

    def print_metric(metric_name, timestamp, value, tags):
        print("%s %s %s %s" % (metric_name, timestamp, format_metric_value(value), tags))

    for (url, patterns) in urls_vs_patterns.iteritems():
        try:
            response = requests.get(url)
            timestamp = int(time.time())
            global buf
            buf = StringIO(response.text)
            found = False
            for line in buf.readlines():
                metric_line = ""
                for pattern in patterns:
                    matcher = pattern.search(line)
                    if matcher is not None:  # TODO would checking for startswith be more efficient here?
                        g = matcher.groups()
                        if g[1].startswith('_count'):
                            continue
                        elif g[1].startswith('_sum'):
                            continue
                        tags = ' '.join(g[1].replace('"', '').strip('{}').split(','))
                        if '::_' in g[0]:
                            extratags = g[0].split('::_')
                            global finalmetricname
                            finalmetricname = extratags[0]
                            for i, extratag in enumerate(extratags):
                                if i == 0:
                                    continue
                                elif extratag.startswith('_'):
                                    finalmetricname += extratag
                                else:
                                    tags += ' ' + extratag.replace('_', '=')
                            print_metric(finalmetricname, timestamp, g[2], tags)
                            metric_naming.print_if_apptuit_standard_metric(finalmetricname, METRIC_MAPPING, timestamp, format_metric_value(g[2]),
                                                                           tags=None, tags_str=tags)
                        else:
                            print_metric(g[0], timestamp, g[2], tags)
                            metric_naming.print_if_apptuit_standard_metric(g[0], METRIC_MAPPING, timestamp, format_metric_value(g[2]), tags=None,
                                                                           tags_str=tags)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
            die()

if __name__ == '__main__':
    main()
