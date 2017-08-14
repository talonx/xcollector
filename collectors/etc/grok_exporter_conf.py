#!/usr/bin/env python

"""
Config for the grok processes to be run
"""
from collectors.etc import yaml_conf

GROK_CONFIG = yaml_conf.load_collector_configuration('grok.yml')['collector']

GROK_EXPORTER_DIR = GROK_CONFIG['grok_dir']

CONFIG_FILES = GROK_CONFIG['config_files']

def get_config_files():
    return CONFIG_FILES

def get_grok_exporter_dir():
    return GROK_EXPORTER_DIR
