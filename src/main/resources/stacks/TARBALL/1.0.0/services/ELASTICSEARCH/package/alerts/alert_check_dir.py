#!/usr/bin/env ambari-python-wrap
# -*- coding: utf-8 -*--

from resource_management import *
import os
import socket


def execute(configurations={}, parameters={}, host_name=None):
    config = Script.get_config()
    elastic_head_pid_dir = config['configurations']['elasticsearch-env']['elastic_head_pid_dir'].rstrip("/")
    elastic_head_pid_file = format("{elastic_head_pid_dir}/elasticsearch-head.pid")

    result = os.path.exists(elastic_head_pid_file)
    if result:
        result_code = 'OK'
        es_head_process_running = True
    else:
        # OK、WARNING、CRITICAL、UNKNOWN、NONE
        result_code = 'CRITICAL'
        es_head_process_running = False

    if host_name is None:
        host_name = socket.getfqdn()

    # 告警时显示的内容Response
    alert_label = 'Elasticsearch Head is running on {0}' if es_head_process_running else 'Elasticsearch Head is NOT running on {0}'
    alert_label = alert_label.format(host_name)

    return ((result_code, [alert_label]))
