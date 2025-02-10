#!/usr/bin/env ambari-python-wrap
# -*- coding: utf-8 -*--
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import json
import os

from resource_management.libraries.functions.format import format
from resource_management.core.source import InlineTemplate
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.core.resources.system import Directory, File, Link, Execute
from setup_elasticsearch import setup_elasticsearch
from elasticsearch_service import elasticsearch_service


class ElasticSearchServer(Script):
  def install(self, env):
    import params
    env.set_params(params)
    
    from install_tarball import install_tarball
    install_tarball(env, name='elasticsearch')

    Logger.info("Install elasticsearch complete")

  def configure(self, env, upgrade_type=None):
    import params
    env.set_params(params)

    setup_elasticsearch(env, "elasticsearchserver",
                        upgrade_type=upgrade_type, action='config')

  def start(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    # Configure Elasticsearch
    self.configure(env)

    # starts elasticsearch
    elasticsearch_service("elasticsearchserver", upgrade_type=upgrade_type, action="start")

    # metrics
    params_data = {
      "es": {
        "ip": params.elasticsearch_server_host,
        "port": params.elasticsearch_port,
        "pid_file": params.elastic_pid_file,
        "log_dir": params.elastic_log_dir,
        "xpack_security_enabled": params.xpack_security_enabled,
        "auth_user": params.elasticsearch_username,
        "auth_password": params.elasticsearch_password
      },
      "metrics_collector": {
        "ip": params.metrics_collector_host,
        "port": params.metrics_collector_port
      }
    }
    Logger.info("params_data: {0}".format(json.dumps(params_data)))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = "nohup /usr/bin/python -u {0}/es_metrics.py '{1}'  > /dev/null 2>&1 &".format(current_dir,
                                                                                        json.dumps(params_data))
    Execute(cmd, user=params.elastic_user)

  def stop(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    # Stop Elasticsearch
    elasticsearch_service("elasticsearchserver", upgrade_type=upgrade_type, action="stop")

    Logger.info("Stop elasticsearch complete!")

  def status(self, env):
    import status_params
    env.set_params(status_params)

    # Use built-in method to check status using pidfile
    check_process_status(status_params.elastic_pid_file)

  def restart(self, env):
    self.stop(env)
    self.start(env)

  def add_security_enabled(self, env):
    import params
    env.set_params(params)
    Logger.info("******** custom process ********")
    self.stop(env)

    File(format("{params.elastic_conf_dir}/elastic-stack-ca.p12"), action="delete")
    File(format("{params.elastic_conf_dir}/elastic-certificates.p12"), action="delete")

    # 1,elasticsearch-certutil 工具为集群生成 CA证书
    Execute('{0}/bin/elasticsearch-certutil ca -out  {1}/elastic-stack-ca.p12 -pass \'\' '.format(
      params.elastic_home, params.elastic_conf_dir),
      user=params.elastic_user,
      ignore_failures=True)

    # 2,为集群中的节点生成证书和私钥
    Execute(
      '{0}/bin/elasticsearch-certutil cert --ca {1}/elastic-stack-ca.p12 --ca-pass \'\' -out {1}/elastic-certificates.p12 -pass \'\' '.format(
        params.elastic_home, params.elastic_conf_dir),
      user=params.elastic_user,
      ignore_failures=True)

    # 3,拷贝到其他elasticsearch_server_hosts节点
    for host in params.elasticsearch_server_hosts:
      Execute(
        'scp {0}/elasticsearch.keystore  {0}/elastic-certificates.p12  {0}/elastic-stack-ca.p12 {1}:{0}/ '.format(
          params.elastic_conf_dir, host),
        user='root',
        ignore_failures=True)

    self.start(env)
    Logger.info(
      "custom elasticsearch server successfully! you should xpack_security_enabled=true, and then reboot elasticsearch_server")


if __name__ == "__main__":
  ElasticSearchServer().execute()
