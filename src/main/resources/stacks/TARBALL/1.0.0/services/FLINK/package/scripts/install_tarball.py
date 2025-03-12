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
  # tarball download
  repo_base_url = config["repositoryFile"]["repositories"][0]["baseUrl"]
  flink_url = repo_base_url + config['configurations']['flink-download']['flink_url']
  flink_shaded_hadoop_url = repo_base_url + config['configurations']['flink-download']['flink_shaded_hadoop_url']
  commons_cli_url = repo_base_url + config['configurations']['flink-download']['commons_cli_url']
  rs_url = repo_base_url + config['configurations']['flink-download']['rs_url']
  jersey_core_url = repo_base_url + config['configurations']['flink-download']['jersey_core_url']
  jersey_common_url = repo_base_url + config['configurations']['flink-download']['jersey_common_url']
  flnk_jdbc_url = repo_base_url + config['configurations']['flink-download']['flnk_jdbc_url']
  flnk_kafka_url = repo_base_url + config['configurations']['flink-download']['flnk_kafka_url']
  
  flink_tgz_name = flink_url.split('/')[-1]

  Directory(params.flink_home, action="delete")

  Directory([params.flink_home, '/etc/flink', params.stack_root + "/current"],
            mode=0755,
            cd_access='a',
            owner=params.flink_user,
            group=params.user_group,
            create_parents=True
            )

  tmp_flink_tgz_path = os.path.join('/tmp/', flink_tgz_name)
  Execute('wget -O {0} {1}'.format(tmp_flink_tgz_path, flink_url))
  Execute('tar -zxvf {0} -C {1} --strip-components=1 && rm -f {0}'
          .format(tmp_flink_tgz_path, params.flink_home))

  # wget
  Execute('wget -P {0} {1}'.format(params.flink_lib_dir, flink_shaded_hadoop_url))
  Execute('wget -P {0} {1}'.format(params.flink_lib_dir, commons_cli_url))
  Execute('wget -P {0} {1}'.format(params.flink_lib_dir, rs_url))
  Execute('wget -P {0} {1}'.format(params.flink_lib_dir, jersey_core_url))
  Execute('wget -P {0} {1}'.format(params.flink_lib_dir, jersey_common_url))
  Execute('wget -P {0} {1}'.format(params.flink_lib_dir, flnk_jdbc_url))
  Execute('wget -P {0} {1}'.format(params.flink_lib_dir, flnk_kafka_url))
  # create link
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.flink_home, params.stack_root + "/current/flink"))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.flink_home_conf_dir, params.flink_conf_dir))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.flink_bin_dir + '/flink', "/usr/bin/flink"))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.flink_bin_dir + '/sql-client.sh', "/usr/bin/sql-client"))
  Logger.info('Install the FlinkHistoryServer Success')
