#!/usr/bin/env python

from collectors.etc import yaml_conf

MYSQL_CONFIG = yaml_conf.load_collector_configuration('mysql.yml')['collector']


def get_user_password(input_sock_file):
    """Given the path of a socket file, returns a tuple (user, password)."""
    for sock_file in MYSQL_CONFIG['sock_files']:
        if sock_file['path'] == input_sock_file:
            return (sock_file['username'], sock_file['password'])
