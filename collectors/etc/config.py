#!/usr/bin/env python
# This file is part of tcollector.
# Copyright (C) 2010  The tcollector Authors.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.

# This 'onload' function will be called by tcollector when it starts up.
# You can put any code here that you want to load inside the tcollector.
# This also gives you a chance to override the options from the command
# line or to add custom sanity checks on their values.
# You can also use this to change the global tags that will be added to
# every single data point.  For instance if you have multiple different
# pools or clusters of machines, you might wanna lookup the name of the
# pool or cluster the current host belongs to and add it to the tags.
# Throwing an exception here will cause the tcollector to die before it
# starts doing any work.
# Python files in this directory that don't have an "onload" function
# will be imported by tcollector too, but no function will be called.
# When this file executes, you can assume that its directory is in
# sys.path, so you can import other Python modules from this directory
# or its subdirectories.

from collectors.etc import yaml_conf

TCOLLECTOR_CONF = yaml_conf.load_collector_configuration('xcollector.yml')['collector']

def onload(options, tags):
    """Function called by tcollector when it starts up.

    Args:
        options: The options as returned by the OptionParser.
        tags: A dictionnary that maps tag names to tag values.
    """
    pass

def get_defaults():
    """Configuration values to use as defaults in the code

        This is called by the OptionParser.
    """

    defaults = TCOLLECTOR_CONF['config']
    defaults['pidfile'] = "/var/run/xcollector.pid"
    defaults['no_tcollector_stats'] = False
    defaults['evictinterval'] = 6000
    defaults['dedupinterval'] = 0
    defaults['deduponlyzero'] = False
    defaults['allowed_inactivity_time'] = 600
    defaults['maxtags'] = 25
    defaults['max_bytes'] = defaults['log_max_bytes']
    defaults['http_username'] = defaults['access_token']
    defaults['http_password'] = True
    defaults['reconnectinterval'] = 0
    if 'host' not in defaults:
        defaults['host'] = "api.apptuit.ai"
    if 'port' not in defaults:
        defaults['port'] = 443
    defaults['http'] = True
    defaults['http_api_path'] = "api/put"
    if 'tags' not in defaults:
        defaults['tags'] = {}
    defaults['remove_inactive_collectors'] = False
    defaults['backup_count'] = defaults['log_backup_count']
    defaults["cdir"] = "/usr/local/xcollector/collectors"
    if 'ssl' not in defaults:
        defaults['ssl'] = True
    defaults['stdin'] = False
    if 'daemonize' not in defaults:
        defaults['daemonize'] = False
    defaults['hosts'] = False

    return defaults
