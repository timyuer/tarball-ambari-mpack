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
from resource_management.libraries.resources.xml_config import XmlConfig
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions import Direction

from resource_management.core.logger import Logger


def setup_seatunnel(env, type='seatunnelclient', upgrade_type=None, action=None):
  import params
  import status_params

  Directory([params.seatunnel_log_dir, params.seatunnel_conf_dir, status_params.seatunnel_pid_dir],
            mode=0755,
            cd_access='a',
            owner=params.seatunnel_user,
            group=params.user_group,
            create_parents=True,
            recursive_ownership=True,
            )

  File(format("{params.seatunnel_conf_dir}/seatunnel.yaml"),
       owner=params.seatunnel_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.seatunnel_conf_content))

  File(format("{params.seatunnel_conf_dir}/hazelcast.yaml"),
       owner=params.seatunnel_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.hazelcast_conf_content))

  File(format("{params.seatunnel_conf_dir}/hazelcast-client.yaml"),
       owner=params.seatunnel_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.hazelcast_client_conf_content))

  File(format("{params.seatunnel_conf_dir}/log4j2.properties"),
       owner=params.seatunnel_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.seatunnel_log4j2_properties))

  File(format("{params.seatunnel_conf_dir}/log4j2_client.properties"),
       owner=params.seatunnel_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.seatunnel_log4j2_client_properties))

  File(format("{params.seatunnel_conf_dir}/seatunnel-env.sh"),
       owner=params.seatunnel_user,
       group=params.user_group,
       mode=0755,
       content=InlineTemplate(params.seatunnel_env_content))

  # On some OS this folder could be not exists, so we will create it before pushing there files
  Directory(params.limits_conf_dir,
            create_parents=True,
            owner='root',
            group='root'
            )

  File(os.path.join(params.limits_conf_dir, 'seatunnel.conf'),
       owner='root',
       group='root',
       mode=0644,
       content=Template("seatunnel.conf.j2")
       )

