#!/usr/bin/env ambari-python-wrap
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


import os

from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.resources.properties_file import PropertiesFile
from resource_management.libraries.resources.template_config import TemplateConfig
from resource_management.core.resources.system import Directory, Execute, File, Link
from resource_management.core.source import StaticFile, Template, InlineTemplate
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions import format
from resource_management.libraries.functions.generate_logfeeder_input_config import generate_logfeeder_input_config
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature
import re

from resource_management.core.logger import Logger


def install_tarball(env):
  import params
  env.set_params(params)
  from resource_management.libraries.script.script import Script
  config = Script.get_config()

  # zookeeper download
  repo_base_url = config["repositoryFile"]["repositories"][0]["baseUrl"]
  zookeeper_url = repo_base_url + config['configurations']['zookeeper-download']['zookeeper_url']

  Directory(params.zookeeper_home, action="delete")

  Directory([params.zookeeper_home, params.zk_log_dir, params.zk_pid_dir],
            mode=0755,
            cd_access='a',
            owner=params.zk_user,
            group=params.user_group,
            create_parents=True
            )
  Directory(['/etc/zookeeper', params.stack_root + '/current'],
            mode=0755,
            cd_access='a',
            owner=params.zk_user,
            group=params.user_group,
            create_parents=True
            )

  tarball_name = zookeeper_url.split('/')[-1]
  Execute('wget -O {0} {1}'.format('/tmp/' + tarball_name, zookeeper_url))
  Execute('tar -zxvf {0} -C {1} --strip-components=1 && rm -f {0}'
          .format('/tmp/' + tarball_name, params.zookeeper_home))
  # create link
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.zookeeper_home + '/conf', params.conf_dir))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.zookeeper_home, params.stack_root + "/current/zookeeper-server"))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.zookeeper_home, params.stack_root + "/current/zookeeper-client"))
  # chown
  Execute(
    format('chown -R {params.zk_user}:{params.user_group} {params.zookeeper_home}'))
