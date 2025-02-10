#!/usr/bin/env ambari-python-wrap
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
  repo_base_url = config["repositoryFile"]["repositories"][0]["baseUrl"]

  # -------------------------------download tarball--------------------
  dolphinscheduler_download_url = repo_base_url + config['configurations']['dolphinscheduler-download']['dolphinscheduler_download_url']
  mysql_connector_download_url = repo_base_url + config['configurations']['dolphinscheduler-download']['mysql_connector_download_url']

  Directory(params.dolphinscheduler_home, action="delete")

  Directory(params.dolphinscheduler_home,
            mode=0755,
            cd_access='a',
            owner=params.dolphinscheduler_user,
            group=params.user_group,
            create_parents=True
            )
  Directory('/etc/dolphinscheduler',
            mode=0755,
            cd_access='a',
            owner=params.dolphinscheduler_user,
            group=params.user_group,
            create_parents=True
            )

  Execute(format('wget -O /tmp/dolphinscheduler.tar.gz {dolphinscheduler_download_url}'))
  Execute('tar -zxvf {0} -C {1} --strip-components=1 && rm -f {0}'
          .format('/tmp/dolphinscheduler.tar.gz', params.dolphinscheduler_home))
  # wget mysql jdbc
  Execute('wget -P {0} {1}'.format(params.master_server_lib_dir, mysql_connector_download_url))
  Execute('wget -P {0} {1}'.format(params.worker_server_lib_dir, mysql_connector_download_url))
  Execute('wget -P {0} {1}'.format(params.api_server_lib_dir, mysql_connector_download_url))
  Execute('wget -P {0} {1}'.format(params.alert_server_lib_dir, mysql_connector_download_url))
  Execute('wget -P {0} {1}'.format(params.tools_lib_dir, mysql_connector_download_url))
  # create link
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.dolphinscheduler_home_conf_dir, params.dolphinscheduler_conf_dir))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.dolphinscheduler_home, params.stack_root + "/current/dolphinscheduler"))
  # copy hadoop conf link
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_conf_dir + "/core-site.xml", params.api_server_conf_dir + "/core-site.xml"))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_conf_dir + "/hdfs-site.xml", params.api_server_conf_dir + "/hdfs-site.xml"))
  # chown
  Execute(
    format('chown -R {params.dolphinscheduler_user}:{params.user_group} {params.dolphinscheduler_home}'))
  Logger.info('Install the DolphinScheduler Success')