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


def setup_elasticsearch(env, type, upgrade_type=None, action=None):
  # Import properties defined in -config.xml file from the params class
  import params

  # This allows us to access the params.elastic_pid_file property as
  # format('{elastic_pid_file}')
  env.set_params(params)

  if action == "config":
    if type == "elasticsearchserver":

      File(format("{limits_conf_dir}/elasticsearch.conf"),
           mode=0644,
           content=Template('elasticsearch.conf.j2')
           )

      # mkdir pid dir
      Directory([params.elastic_log_dir, params.elastic_pid_dir, params.elastic_conf_dir],
                mode=0755,
                cd_access='a',
                owner=params.elastic_user,
                group=params.user_group,
                create_parents=True
                )

      # Ensure all files owned by elasticsearch user
      cmd = format(
        "chown -R {elastic_user}:{user_group} {elastic_home} {elastic_log_dir} {elastic_pid_dir}")
      Execute(cmd)

      File(format("{elastic_conf_dir}/elasticsearch.yml"),
           owner=params.elastic_user,
           group=params.user_group,
           content=InlineTemplate(params.elasticsearch_yml))

      File(format("{elastic_conf_dir}/jvm.options"),
           owner=params.elastic_user,
           group=params.user_group,
           content=InlineTemplate(params.jvm_options))

      # mkdir elasticsearch path_data
      path_data_es = params.path_data.split(',')
      for i in range(len(path_data_es)):
        Directory([path_data_es[i]],
                  mode=0755,
                  cd_access='a',
                  owner=params.elastic_user,
                  group=params.user_group,
                  create_parents=True
                  )
        cmd = "chown -R {0}:{1} {2}".format(
          params.elastic_user, params.user_group, path_data_es[i])
        Execute(cmd)

    elif type == "kibanaserver":
      File(format("{elastic_kibana_home}/config/kibana.yml"),
           content=InlineTemplate(params.kibana_kibana_content),
           owner=params.elastic_user,
           group=params.user_group)

      cmd = format(
        "chown -R {elastic_user}:{user_group} {elastic_kibana_home}")
      Execute(cmd)

      # Make sure pid directory exist
      Directory(params.elastic_kibana_pid_dir,
                mode=0755,
                cd_access='a',
                owner=params.elastic_user,
                group=params.user_group,
                create_parents=True
                )
    elif type == "elasticsearchhead":
      # create pid dir
      Directory([params.elastic_head_pid_dir],
                mode=0755,
                cd_access='a',
                owner=params.elastic_user,
                group=params.user_group,
                create_parents=True
                )

      # Ensure all files owned by elasticsearch user
      cmd = format("chown -R {elastic_user}:{user_group} {elastic_head_home} {elastic_head_pid_dir}")
      Execute(cmd)

      # Update the port in the web UI that displays the connection to the Elasticsearch
      File(os.path.join(params.tmp_dir, 'changeHostName.sh'),
           owner=params.elastic_user,
           group=params.user_group,
           mode=0644,
           content=Template("changeHostName.sh.j2")
           )
      cmd = format("cd {tmp_dir}; sh ./changeHostName.sh")
      Execute(cmd, user=params.elastic_user)

  Logger.info("Configuration complete")


