#!/usr/bin/env python

"""Collector for scraping data from Go processes' expvar endpoint"""

import sys
import traceback
import time
import requests

from collectors.etc import yaml_conf
from collectors.lib import utils

GOPROC_CONFIG = yaml_conf.load_collector_configuration('go_expvar.yml')['collector']['config']

COLLECTION_INTERVAL_SECONDS = 15
NANO_MULTIPLIER = 1000 * 1000 * 1000
SKIP_MEM_KEYS = ['PauseNs', 'PauseEnd', 'BySize', 'EnableGC', 'DebugGC', 'LastGC']

DEBUG = False


def print_debug(msg):
    """Prints out debug message"""
    if DEBUG:
        print(msg)


def _print_nested_metrics(key, value, timestamp, root=None):
    if isinstance(value, dict):
        for c_key, c_value in value.items():
            _print_nested_metrics(c_key, c_value, timestamp,
                                  ('' if root is None else (root + '.')) + key)
    else:
        _print_metric(key if root is None else '%s.%s' % (root, key), timestamp, value)


def _print_metric(metric, timestamp, value):
    print('%s.%s %s %s' %
          (GOPROC_CONFIG['endpoints'][0]['metric_prefix'], metric, timestamp, value)
          )


def _check_connection(expvar_url):
    try:
        response = requests.get(expvar_url)
        code = response.status_code
        if code != 200:
            utils.err("Error status code for %s: %d : %s" % (expvar_url, code, response.text))
            exit(13)
    except:
        utils.err("Unexpected error while checking %s: %s" % (expvar_url, sys.exc_info()[0]))
        traceback.print_exc()
        exit(13)


def main(argv):
    utils.drop_privileges()
    expvar_url = GOPROC_CONFIG['endpoints'][0]["expvar_url"]  # TODO supporting single URL for now
    if not expvar_url.endswith('/debug/vars'):
        expvar_url = expvar_url + '/debug/vars'

    _check_connection(expvar_url)

    while True:
        try:
            response = requests.get(expvar_url)
            code = response.status_code
            if code != 200:
                utils.err("Unexpected status code for %s: %d content: %s"
                          % (expvar_url, code, response.text))
            else:
                res_json = response.json()
                ts_seconds = int(time.time())
                ts_span_ago_ns = (ts_seconds - COLLECTION_INTERVAL_SECONDS) * NANO_MULTIPLIER
                for j_key, j_value in res_json.items():
                    if j_key == 'memstats':
                        print_debug(j_value)
                        pause_ns = j_value['PauseNs']
                        pause_end = j_value['PauseEnd']
                        num_gc = j_value['NumGC']
                        cur_pos = (num_gc + 255) % 256
                        index = cur_pos
                        pause_sum = 0
                        gc_count = 0
                        # TODO optimize for last GC run.
                        while index >= 0 and pause_end[index] >= ts_span_ago_ns:
                            print_debug('Item %s %s' % (pause_ns[index], pause_end[index]))
                            pause_sum += pause_ns[index]
                            gc_count += 1
                            index = index - 1
                        _print_metric('memstats.PauseNs.sum', ts_seconds, pause_sum)
                        _print_metric('memstats.GC.count', ts_seconds, gc_count)
                        for mem_key, mem_value in j_value.items():
                            if mem_key not in SKIP_MEM_KEYS:
                                _print_metric("memstats.%s" % mem_key, ts_seconds, mem_value)
                    elif j_key != 'cmdline':
                        _print_nested_metrics(j_key, j_value, ts_seconds)
        except:
            utils.err("Unexpected error for %s: %s" % (expvar_url, sys.exc_info()[0]))
            traceback.print_exc()
        sys.stdout.flush()
        time.sleep(COLLECTION_INTERVAL_SECONDS)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
