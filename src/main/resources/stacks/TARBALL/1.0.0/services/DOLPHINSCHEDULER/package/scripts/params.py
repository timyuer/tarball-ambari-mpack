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
import functools
from resource_management.core.logger import Logger
from resource_management.core.utils import PasswordString
from resource_management.libraries.functions.is_empty import is_empty
from resource_management.libraries.functions import format
from resource_management.libraries.resources import HdfsResource
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions import get_kinit_path
from resource_management.libraries.functions.get_not_managed_resources import get_not_managed_resources
from resource_management.libraries.script.script import Script
import json
import socket
import os
import status_params

# server configurations
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

stack_name = default("/clusterLevelParams/stack_name", None)
stack_root = Script.get_stack_root()

# This is expected to be of the form #.#.#.#
stack_version_unformatted = config['clusterLevelParams']['stack_version']

java_home = config["ambariLevelParams"]["java_home"]
java17_home = config['configurations']['cluster-env']['java17_home']
java_home = java17_home if java17_home is not None and os.path.exists(java17_home) else java_home

host_info = config['clusterHostInfo']
host_level_params = config['ambariLevelParams']

stack_version_home = os.path.join(stack_root, stack_version_unformatted)

dolphinscheduler_home = os.path.join(stack_version_home, "dolphinscheduler")
master_server_home = os.path.join(dolphinscheduler_home, "master-server")
worker_server_home = os.path.join(dolphinscheduler_home, "worker-server")
api_server_home = os.path.join(dolphinscheduler_home, "api-server")
alert_server_home = os.path.join(dolphinscheduler_home, "alert-server")
# libs
master_server_lib_dir = os.path.join(master_server_home, "libs")
worker_server_lib_dir = os.path.join(worker_server_home, "libs")
api_server_lib_dir = os.path.join(api_server_home, "libs")
alert_server_lib_dir = os.path.join(alert_server_home, "libs")
tools_lib_dir = os.path.join(dolphinscheduler_home, "tools", "libs")
# conf
master_server_conf_dir = os.path.join(master_server_home, "conf")
worker_server_conf_dir = os.path.join(worker_server_home, "conf")
api_server_conf_dir = os.path.join(api_server_home, "conf")
alert_server_conf_dir = os.path.join(alert_server_home, "conf")

dolphinscheduler_home_conf_dir = dolphinscheduler_home + "/bin/env"
dolphinscheduler_conf_dir = "/etc/dolphinscheduler/conf"
dolphinscheduler_bin_dir = dolphinscheduler_home + "/bin"
dolphinscheduler_lib_dir = dolphinscheduler_home + "/lib"
dolphinscheduler_log_dir = config['configurations']['dolphinscheduler-env']['dolphinscheduler_log_dir']
dolphinscheduler_pid_dir = status_params.dolphinscheduler_pid_dir
master_server_pid_file = format("{master_server_home}/pid")
worker_server_pid_file = format("{worker_server_home}/pid")
api_server_pid_file = format("{api_server_home}/pid")
alert_server_pid_file = format("{alert_server_home}/pid")

dolphinscheduler_bin = format("{dolphinscheduler_home}/bin/dolphinscheduler-daemon.sh")

dolphinscheduler_database_type = config['configurations']['dolphinscheduler-env']['dolphinscheduler_database_type']
dolphinscheduler_database_name = config['configurations']['dolphinscheduler-env']['dolphinscheduler_database_name']
dolphinscheduler_database_user = config['configurations']['dolphinscheduler-env']['dolphinscheduler_database_user']
dolphinscheduler_database_password = config['configurations']['dolphinscheduler-env']['dolphinscheduler_database_password']
dolphinscheduler_database_host = config['configurations']['dolphinscheduler-env']['dolphinscheduler_database_host']
dolphinscheduler_database_port = config['configurations']['dolphinscheduler-env']['dolphinscheduler_database_port']

dolphinscheduler_env_content = config['configurations']['dolphinscheduler-env']['content']

# sudoers.d
sudoers_conf_dir = "/etc/sudoers.d"

seatunnel_home = os.path.join(stack_version_home, "seatunnel")
flink_home = os.path.join(stack_version_home, "flink")
# default hadoop parameters
hadoop_home = stack_select.get_hadoop_dir("home")
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
dfs_type = default("/clusterLevelParams/dfs_type", "hdfs")
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name']
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
default_fs = config['configurations']['core-site']['fs.defaultFS']
hdfs_site = config['configurations']['hdfs-site']
hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore"

zookeeper_hosts = config['clusterHostInfo']['zookeeper_server_hosts']
zookeeper_port = config['configurations']['zoo.cfg']['clientPort']

zookeeper_url = ','.join(host + ':' + zookeeper_port for host in zookeeper_hosts)

api_server_host = default("/clusterHostInfo/api_server_hosts", ['localhost'])[0]


dolphinscheduler_name = 'dolphinscheduler'
dolphinscheduler_user = status_params.dolphinscheduler_user
dolphinscheduler_group = status_params.dolphinscheduler_group
user_group = status_params.user_group
dolphinscheduler_hdfs_user_dir = format("/user/{dolphinscheduler_user}")


kinit_path_local = get_kinit_path(
    default('/configurations/kerberos-env/executable_search_paths', None))
security_enabled = config['configurations']['cluster-env']['security_enabled']
smokeuser = config['configurations']['cluster-env']['smokeuser']
smokeuser_principal = config['configurations']['cluster-env']['smokeuser_principal_name']
smoke_user_keytab = config['configurations']['cluster-env']['smokeuser_keytab']

# create partial functions with common arguments for every HdfsResource call
# to create/delete hdfs directory/file/copyfromlocal we need to call params.HdfsResource in code
HdfsResource = functools.partial(
    HdfsResource,
    user=hdfs_user,
    hdfs_resource_ignore_file=hdfs_resource_ignore_file,
    security_enabled=security_enabled,
    keytab=hdfs_user_keytab,
    kinit_path_local=kinit_path_local,
    hadoop_bin_dir=hadoop_bin_dir,
    hadoop_conf_dir=hadoop_conf_dir,
    principal_name=hdfs_principal_name,
    hdfs_site=hdfs_site,
    default_fs=default_fs,
    immutable_paths=get_not_managed_resources(),
    dfs_type=dfs_type
)
