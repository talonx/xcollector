#!/usr/bin/env python

from __future__ import print_function
import traceback

import requests
import sys
import time

from collectors.etc import goprocconf
from collectors.lib import utils

COLLECTION_INTERVAL_SECONDS = 15
SKIP_MEM_KEYS = ['PauseNs', 'PauseEnd', 'BySize']


# "stats":
#     {"advanced":
#          {"closed": 748,
#           "opened": 0
#          },
#      "connections": 748
#      }

def _print_nested_metrics(key, value, ts, root=None):
    if isinstance(value, dict):
        for ck, cv in value.items():
            _print_nested_metrics(ck, cv, ts, ('' if root is None else (root + '.')) + key)
    else:
        print("%s %s %s" % (key, ts, value) if root is None else "%s.%s %s %s" % (root, key, ts, value))


def main(argv):
    expvar_url = goprocconf.get_expvar_url()
    if not expvar_url.endswith('/debug/vars'):
        expvar_url = expvar_url + '/debug/vars'

    while True:
        try:
            response = requests.get(expvar_url)
            code = response.status_code
            if code != 200:
                utils.err("Unexpected status code: %d content: %s" % (code, response.text))
                exit(13)
            else:
                res_json = response.json()
                ts = int(time.time())
                for k, v in res_json.items():
                    if k == 'memstats':
                        for mk, mv in v.items():
                            if mk not in SKIP_MEM_KEYS:
                                print("memstats.%s %s %s" % (mk, ts, mv))
                    elif k != 'cmdline':
                        _print_nested_metrics(k, v, ts)
            sys.stdout.flush()
        except:
            utils.err("Unexpected error: %s" % sys.exc_info()[0])
            traceback.print_exc()
            exit(13)
        time.sleep(COLLECTION_INTERVAL_SECONDS)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
