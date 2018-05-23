#!/usr/bin/env python

from collectors.etc import yaml_conf

GOPROC_CONFIG = yaml_conf.load_collector_configuration('goproc.yml')['collector']['config']


def get_expvar_url():
    return GOPROC_CONFIG["expvar_url"]
