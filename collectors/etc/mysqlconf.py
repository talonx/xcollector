#!/usr/bin/env python

from collectors.etc import yaml_conf

MYSQL_CONFIG = yaml_conf.load_collector_configuration('mysql.yml')['collector']['config']


def get_db_hosts():
    return list(MYSQL_CONFIG["remote_hosts"].keys())


def get_db_connection_properties(host):
    return (MYSQL_CONFIG["remote_hosts"][host]["connect_host"], MYSQL_CONFIG["remote_hosts"][host]["connect_port"],
            MYSQL_CONFIG["remote_hosts"][host]["username"], MYSQL_CONFIG["remote_hosts"][host]["password"])


def get_db_custom_tags(host):
    if "tags" not in MYSQL_CONFIG["remote_hosts"][host]:
        return None
    return MYSQL_CONFIG["remote_hosts"][host]["tags"]
