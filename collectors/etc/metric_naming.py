#!/usr/bin/env python

def print_if_apptuit_standard_metric(metric, mapping, timestamp, value, tags=None, tags_str=None):
    if metric not in list(mapping["metrics"].keys()):
        return
    new_metric_name = mapping["metrics"][metric]["standard_name"]
    new_metric_tags_str = ""
    if tags is not None or tags_str is not None or "tags" in mapping or "tags" in mapping["metrics"][metric]:
        new_metric_tags = {}
        if tags is not None:
            for tag in tags:
                new_metric_tags[tag] = tags[tag]
        if "tags" in mapping:
            for tag in mapping["tags"]:
                new_metric_tags[tag] = mapping["tags"][tag]
        if "tags" in mapping["metrics"][metric]:
            for tag in mapping["metrics"][metric]["tags"]:
                new_metric_tags[tag] = mapping["metrics"][metric]["tags"][tag]
        for i, tag in enumerate(new_metric_tags):
            if i != len(new_metric_tags):
                new_metric_tags_str += tag + "=" + new_metric_tags[tag] + " "
            else:
                new_metric_tags_str += tag + "=" + new_metric_tags[tag]
        if tags_str is not None:
            new_metric_tags_str = new_metric_tags_str.strip()
            new_metric_tags_str += " " + tags_str.strip()
    print("%s %d %s %s"
           % (new_metric_name, timestamp, value, new_metric_tags_str))
