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
from resource_management.libraries.functions.get_not_managed_resources import (
    get_not_managed_resources,
)
from resource_management.libraries.script.script import Script
import os
import status_params

# server configurations
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

stack_name = default("/clusterLevelParams/stack_name", None)
stack_root = Script.get_stack_root()

# This is expected to be of the form #.#.#.#
stack_version_unformatted = config["clusterLevelParams"]["stack_version"]

# java_home = config["ambariLevelParams"]["java_home"]
java_home = '/usr/local/java17'
hostname = config["agentLevelParams"]["hostname"]
host_info = config["clusterHostInfo"]
host_level_params = config["ambariLevelParams"]

stack_version_home = os.path.join(stack_root, stack_version_unformatted)

# fe
fe_home = os.path.join(stack_version_home, "doris-fe")
fe_home_conf_dir = format("{fe_home}/conf")
doris_fe_log_dir = config["configurations"]["doris-env"]["doris_fe_log_dir"]
fe_lib_dir = format("{fe_home}/lib")
fe_bin_dir = format("{fe_home}/bin")
fe_conf_dir = "/etc/doris-fe/conf"

http_port = config["configurations"]["doris-fe-conf"]["http_port"]
meta_dir = config["configurations"]["doris-fe-conf"]["meta_dir"]
query_port = config["configurations"]["doris-fe-conf"]["query_port"]
rpc_port = config["configurations"]["doris-fe-conf"]["rpc_port"]
edit_log_port = config["configurations"]["doris-fe-conf"]["edit_log_port"]
sys_log_dir = config["configurations"]["doris-fe-conf"]["sys_log_dir"]
doris_fe_content = config["configurations"]["doris-fe-conf"]["doris_fe_content"]
doris_fe_pid_dir = status_params.doris_fe_pid_dir
fe_pid_file = status_params.fe_pid_file

# be
be_home = os.path.join(stack_version_home, "doris-be")
be_home_conf_dir = format("{be_home}/conf")
doris_be_log_dir = config["configurations"]["doris-env"]["doris_be_log_dir"]
be_lib_dir = format("{be_home}/lib")
be_bin_dir = format("{be_home}/bin")
be_conf_dir = "/etc/doris-be/conf"

be_port = config["configurations"]["doris-be-conf"]["be_port"]
webserver_port = config["configurations"]["doris-be-conf"]["webserver_port"]
heartbeat_service_port = config["configurations"]["doris-be-conf"][
    "heartbeat_service_port"
]
brpc_port = config["configurations"]["doris-be-conf"]["brpc_port"]
storage_root_path = config["configurations"]["doris-be-conf"]["storage_root_path"]
doris_be_content = config["configurations"]["doris-be-conf"]["doris_be_content"]
doris_be_pid_dir = status_params.doris_be_pid_dir
be_pid_file = status_params.be_pid_file

# user&group
doris_user = config["configurations"]["doris-env"]["doris_user"]
doris_group = config["configurations"]["doris-env"]["doris_group"]
user_group = config["configurations"]["cluster-env"]["user_group"]

# fe_hosts
fe_hosts = default("/clusterHostInfo/fe_hosts", [])
fe_host = fe_hosts[0]

# system
sudoers_conf_dir = "/etc/sudoers.d"
limits_conf_dir = "/etc/security/limits.d"
sysctl_conf_dir = "/etc/sysctl.d"
doris_user_nofile_soft = config["configurations"]["doris-env"]["doris_user_nofile_soft"]
doris_user_nofile_hard = config["configurations"]["doris-env"]["doris_user_nofile_hard"]
vm_max_map_count = config["configurations"]["doris-env"]["vm_max_map_count"]

# default hadoop parameters
hadoop_home = stack_select.get_hadoop_dir("home")
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
dfs_type = default("/clusterLevelParams/dfs_type", "")
hdfs_user = config["configurations"]["hadoop-env"]["hdfs_user"]
hdfs_principal_name = config["configurations"]["hadoop-env"]["hdfs_principal_name"]
hdfs_user_keytab = config["configurations"]["hadoop-env"]["hdfs_user_keytab"]
default_fs = config["configurations"]["core-site"]["fs.defaultFS"]
hdfs_site = config["configurations"]["hdfs-site"]
hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore"

# security
kinit_path_local = get_kinit_path(
    default("/configurations/kerberos-env/executable_search_paths", None)
)
security_enabled = config["configurations"]["cluster-env"]["security_enabled"]
smokeuser = config["configurations"]["cluster-env"]["smokeuser"]
smokeuser_principal = config["configurations"]["cluster-env"][
    "smokeuser_principal_name"
]
smoke_user_keytab = config["configurations"]["cluster-env"]["smokeuser_keytab"]

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
    dfs_type=dfs_type,
)
