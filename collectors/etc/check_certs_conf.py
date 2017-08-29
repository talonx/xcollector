#!/usr/bin/env python

from collectors.etc import yaml_conf

CERT_CHECKER_CONF = yaml_conf.load_collector_configuration('cert_checker.yml')['collector']

NAME_VERSUS_DOMAINS = CERT_CHECKER_CONF['name_vs_domain']

def get_config():
    return NAME_VERSUS_DOMAINS