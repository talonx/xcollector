#!/usr/bin/env python

import requests
import traceback

import sys
import time

from collectors.etc import yaml_conf
from collectors.lib import utils

GOPROC_CONFIG = yaml_conf.load_collector_configuration('go_expvar.yml')['collector']['config']

COLLECTION_INTERVAL_SECONDS = 15
NANO_MULTIPLIER = 1000 * 1000 * 1000
SKIP_MEM_KEYS = ['PauseNs', 'PauseEnd', 'BySize', 'EnableGC', 'DebugGC', 'LastGC']

DEBUG = False


def print_debug(msg):
    if (DEBUG):
        print(msg)


def _print_nested_metrics(key, value, ts, root=None):
    if isinstance(value, dict):
        for ck, cv in value.items():
            _print_nested_metrics(ck, cv, ts, ('' if root is None else (root + '.')) + key)
    else:
        _print_metric(key if root is None else '%s.%s' % (root, key), ts, value)


def _print_metric(metric, ts, value):
    print('%s.%s %s %s' % (GOPROC_CONFIG['endpoints'][0]['metric_prefix'], metric, ts, value))


def _check_connection(expvar_url):
    try:
        response = requests.get(expvar_url)
        code = response.status_code
        if code != 200:
            utils.err("Unexpected status code for %s: %d content: %s" % (expvar_url, code, response.text))
            exit(13)
    except:
        utils.err("Unexpected error while checking conn to %s: %s" % (expvar_url, sys.exc_info()[0]))
        traceback.print_exc()
        exit(13)


def main(argv):
    utils.drop_privileges()
    expvar_url = GOPROC_CONFIG['endpoints'][0]["expvar_url"] # TODO supporting single URL for now
    if not expvar_url.endswith('/debug/vars'):
        expvar_url = expvar_url + '/debug/vars'

    _check_connection(expvar_url)

    while True:
        try:
            response = requests.get(expvar_url)
            code = response.status_code
            if code != 200:
                utils.err("Unexpected status code for %s: %d content: %s" % (expvar_url, code, response.text))
            else:
                res_json = response.json()
                ts_seconds = int(time.time())
                ts_span_ago_ns = (ts_seconds - COLLECTION_INTERVAL_SECONDS) * NANO_MULTIPLIER
                for k, v in res_json.items():
                    if k == 'memstats':
                        print_debug(v)
                        pause_ns = v['PauseNs']
                        pause_end = v['PauseEnd']
                        num_gc = v['NumGC']
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
                        for mk, mv in v.items():
                            if mk not in SKIP_MEM_KEYS:
                                _print_metric("memstats.%s" % mk, ts_seconds, mv)
                    elif k != 'cmdline':
                        _print_nested_metrics(k, v, ts_seconds)
        except:
            utils.err("Unexpected error for %s: %s" % (expvar_url, sys.exc_info()[0]))
            traceback.print_exc()
        sys.stdout.flush()
        time.sleep(COLLECTION_INTERVAL_SECONDS)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
