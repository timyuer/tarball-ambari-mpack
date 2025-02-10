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
# Python Imports
import os

# Local Imports
from resource_management.core.logger import Logger
from resource_management.libraries.functions import format
from resource_management.core.resources.system import Directory, File, Link, Execute
from resource_management.core.source import InlineTemplate, Template
from resource_management.libraries.resources.properties_file import PropertiesFile


def setup_dolphinscheduler(env, type, upgrade_type=None, action=None):
  import params

  Directory(params.dolphinscheduler_pid_dir,
            owner=params.dolphinscheduler_user,
            group=params.user_group,
            mode=0775,
            create_parents=True
            )

  Directory(params.dolphinscheduler_log_dir,
            mode=0775,
            cd_access='a',
            owner=params.dolphinscheduler_user,
            group=params.user_group,
            create_parents=True
            )

  Directory(params.dolphinscheduler_conf_dir,
            owner=params.dolphinscheduler_user,
            group=params.user_group,
            mode=0775,
            create_parents=True)

  File(format("{sudoers_conf_dir}/dolphinscheduler"),
       mode=0644,
       content=Template('dolphinscheduler.sudo.j2')
       )

  File(format("{params.dolphinscheduler_conf_dir}/dolphinscheduler_env.sh"),
       owner=params.dolphinscheduler_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.dolphinscheduler_env_content))
  
  common_config = dict(params.config['configurations']['common-properties'])
  common_config['resource.hdfs.fs.defaultFS'] = params.config['configurations']['core-site']['fs.defaultFS']

  if type == 'apiserver':
    PropertiesFile("common.properties",
        properties = common_config,
        key_value_delimiter = "=",
        dir=params.api_server_conf_dir,
        owner=params.dolphinscheduler_user,
        group=params.dolphinscheduler_group,
        mode=0644
    )
  elif type == 'workerserver':
    PropertiesFile("common.properties",
        properties = common_config,
        key_value_delimiter = "=",
        dir=params.worker_server_conf_dir,
        owner=params.dolphinscheduler_user,
        group=params.dolphinscheduler_group,
        mode=0644
    )

  params.HdfsResource(common_config['resource.storage.upload.base.path'],
                        type="directory",
                        action="create_on_execute",
                        owner=params.dolphinscheduler_user,
                        mode=0775
                        )

  params.HdfsResource(None, action="execute")
 

  Logger.info("Configuration complete")

