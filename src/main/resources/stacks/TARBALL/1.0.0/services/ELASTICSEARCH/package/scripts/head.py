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

import pwd
import grp
import os

from resource_management.libraries.functions.format import format
from resource_management.core.source import InlineTemplate, Template
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.core.resources.system import Execute, Directory, File

from setup_elasticsearch import setup_elasticsearch
from elasticsearch_service import elasticsearch_service

'''
Install
1. install nodejs, pm2
2. download elasticsearch-head source

Config
1. config elasticsearch-head dependency ip:port
2. create pid dir
3. update dir owner for home, pid, log

Start
1. use pm2 to start
'''


def install_node():
  import params

  cmd = format("wget {params.node_download} -O /tmp/node.tar.gz --no-check-certificate \
            && rm -rf /usr/share/node \
            && mkdir -p /usr/share/node && tar -xzf /tmp/node.tar.gz -C /usr/share/node --strip-components=1 \
            && rm -f /tmp/node.tar.gz \
            && ln -sf /usr/share/node/bin/npm /usr/bin/npm && ln -sf /usr/share/node/bin/node /usr/bin/node")
  Execute(cmd, user='root')

  Execute('/usr/bin/npm config set registry=https://registry.npmmirror.com && /usr/bin/npm install -g pm2', user='root')
  Execute('ln -sf /usr/share/node/bin/pm2 /usr/bin/pm2', user='root')


class Head(Script):

  def install(self, env, upgrade_type=None):
    import params
    env.set_params(params)

    # install_node()

    head_tar_path = '/tmp/elasticsearch-head.tar.gz'
    # Download Elasticsearch and head
    Execute('wget {0} -O {1}'.format(params.elastic_head_download, head_tar_path))

    # Install Elasticsearch
    Execute('/bin/rm -rf {0}'.format(params.elastic_head_home))
    Execute('mkdir -p {0}'.format(params.elastic_head_home))
    Execute('tar -zxvf {0} -C {1} --strip-components=1 && rm -rf {2}'
            .format(head_tar_path, params.elastic_head_home, head_tar_path))
    # Remove Elasticsearch installation file
    Execute('rm -rf {0}'.format(head_tar_path))

    Logger.info('elasticsearch-head install complete.')

  def configure(self, env, upgrade_type=None):
    import params
    env.set_params(params)

    setup_elasticsearch(env, "elasticsearchhead", upgrade_type=upgrade_type, action="config")

  def start(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    # Configure elasticsearch-head
    self.configure(env)

    elasticsearch_service("elasticsearchhead", upgrade_type=upgrade_type, action="start")

  def stop(self, env, upgrade_type=None):
    import params
    env.set_params(params)

    elasticsearch_service("elasticsearchhead", upgrade_type=upgrade_type, action="stop")

  def status(self, env):
    # Import properties defined in -env.xml file from the status_params class
    import status_params
    env.set_params(status_params)

    # Use built-in method to check status using pidfile
    check_process_status(status_params.elastic_head_pid_file)


if __name__ == "__main__":
  Head().execute()
