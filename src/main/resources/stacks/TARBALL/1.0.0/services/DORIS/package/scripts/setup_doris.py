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
from resource_management.libraries.functions import format
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions import Direction

from resource_management.core.logger import Logger


def setup_doris(env, type, upgrade_type=None, action=None):
  import params
  import status_params

  File(os.path.join(params.limits_conf_dir, 'doris.conf'),
       owner='root',
       group='root',
       mode=0644,
       content=Template("doris.conf.j2")
       )

  File(os.path.join(params.sysctl_conf_dir, 'doris-sysctl.conf'),
       owner='root',
       group='root',
       mode=0644,
       content=Template("doris-sysctl.conf.j2")
       )
  Execute('sysctl -p /etc/sysctl.d/doris-sysctl.conf')
  # disable /proc/swaps
  Execute('swapoff -a')

  if type == 'fe':
    Directory([params.doris_fe_log_dir, params.fe_conf_dir, params.meta_dir, params.doris_fe_pid_dir],
              owner=params.doris_user,
              group=params.user_group,
              mode=0775,
              cd_access='a',
              create_parents=True
              )

    File(format("{params.fe_conf_dir}/fe.conf"),
       owner=params.doris_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.doris_fe_content))
    
  elif type == 'be':
    Directory([params.doris_be_log_dir, params.be_conf_dir, params.storage_root_path, params.doris_be_pid_dir],
              owner=params.doris_user,
              group=params.user_group,
              mode=0775,
              cd_access='a',
              create_parents=True
              )

    File(format("{params.be_conf_dir}/be.conf"),
       owner=params.doris_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.doris_be_content))

  Logger.info("Configuration complete")


