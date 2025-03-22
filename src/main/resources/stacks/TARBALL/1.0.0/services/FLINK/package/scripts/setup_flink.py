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
from resource_management.core.source import InlineTemplate
from resource_management.libraries.resources.properties_file import PropertiesFile


def setup_flink(env, type, upgrade_type=None, action=None):
    import params

    Directory(params.flink_pid_dir,
                owner=params.flink_user,
                group=params.user_group,
                mode=0775,
                create_parents=True
                )

    Directory(params.flink_log_dir,
                mode=0775,
                cd_access='a',
                owner=params.flink_user,
                group=params.user_group,
                create_parents=True
                )

    Directory(params.flink_conf_dir,
                owner=params.flink_user,
                group=params.user_group,
                mode=0775,
                create_parents=True)

    if type == 'historyserver' and action == 'config':
        params.HdfsResource(params.flink_hdfs_user_dir,
                            type="directory",
                            action="create_on_execute",
                            owner=params.flink_user,
                            mode=0775
                            )
        params.HdfsResource(params.flink_hdfs_dir,
                            type="directory",
                            action="create_on_execute",
                            owner=params.flink_user,
                            mode=0775
                            )

        params.HdfsResource(None, action="execute")

        Directory(params.historyserver_web_tmpdir,
                mode=0755,
                cd_access='a',
                owner=params.flink_user,
                group=params.user_group,
                create_parents=True
                )

    File(format("{params.flink_conf_dir}/config.yaml"),
        owner=params.flink_user,
        group=params.user_group,
        mode=0755,
        content=InlineTemplate(params.flink_config_yaml_content))

    File(format("{params.flink_conf_dir}/log4j.properties"),
        owner=params.flink_user,
        group=params.user_group,
        mode=0755,
        content=InlineTemplate(params.flink_log4j_properties_content))

    # copy hadoop conf to flink
    Link(params.flink_conf_dir + "/hdfs-site.xml",
        to=params.hadoop_conf_dir + "/hdfs-site.xml")
    Link(params.flink_conf_dir + "/yarn-site.xml",
        to=params.hadoop_conf_dir + "/yarn-site.xml")
    Link(params.flink_conf_dir + "/core-site.xml",
        to=params.hadoop_conf_dir + "/core-site.xml")

    Logger.info("Configuration complete")



