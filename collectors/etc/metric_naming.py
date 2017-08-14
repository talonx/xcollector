#!/usr/bin/env python

def print_if_apptuit_standard_metric(metric, mapping, timestamp, value, tags):
    if metric not in mapping["metrics"].keys():
        return
    new_metric_name = mapping["metrics"][metric]["standard_name"]
    new_metric_tags = mapping["metrics"][metric]["tags"]
    for tag in tags:
        new_metric_tags[tag] = tags[tag]
    for tag in mapping["tags"]:
        new_metric_tags[tag] = mapping["tags"][tag]
    tags = ""
    for i, tag in enumerate(new_metric_tags):
        if i != len(new_metric_tags):
            tags += tag + "=" + new_metric_tags[tag] + " "
        else:
            tags += tag + "=" + new_metric_tags[tag]
    print ("%s %d %s %s"
           % (new_metric_name, timestamp, value, tags))