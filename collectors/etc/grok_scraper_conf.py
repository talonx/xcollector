#!/usr/bin/env python

"""
Config for the grok processes to be run
"""
from collectors.etc import yaml_conf

GROK_CONFIG = yaml_conf.load_collector_configuration('grok.yml')['collector']

GROK_EXPORTER_DIR = GROK_CONFIG['grok_exporter_dir']

if 'grok_exporter_debug' in GROK_CONFIG:
    GROK_EXPORTER_DEBUG = GROK_CONFIG['grok_exporter_debug']
else:
    GROK_EXPORTER_DEBUG = False

GROK_SCRAPER_CONFIG_DIR = GROK_CONFIG['grok_scraper_config_dir']

def get_grok_exporter_dir():
    return GROK_EXPORTER_DIR

def get_grok_exporter_debug():
    return GROK_EXPORTER_DEBUG

def get_grok_scraper_config_dir():
    return GROK_SCRAPER_CONFIG_DIR
