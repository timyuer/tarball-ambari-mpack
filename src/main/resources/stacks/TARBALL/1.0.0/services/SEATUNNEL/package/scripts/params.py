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
from resource_management.libraries.functions import get_kinit_path
from resource_management.libraries.resources import HdfsResource
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions.get_not_managed_resources import get_not_managed_resources
from resource_management.core.resources import Directory
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.format import format
from resource_management.core.logger import Logger
from resource_management.libraries.functions.get_architecture import get_architecture
from resource_management.libraries.functions.version import format_stack_version
import status_params

# server configurations
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

architecture = get_architecture()

stack_name = default("/clusterLevelParams/stack_name", None)
stack_root = Script.get_stack_root()
# This is expected to be of the form #.#.#.#
stack_version_unformatted = config['clusterLevelParams']['stack_version']
stack_version_formatted = format_stack_version(stack_version_unformatted)

hostname = config['agentLevelParams']['hostname']
ambari_server_host = config['ambariLevelParams']['ambari_server_host']

java_home = config["ambariLevelParams"]["java_home"]
java17_home = config['configurations']['cluster-env']['java17_home']
java_home = java17_home if java17_home is not None and os.path.exists(java17_home) else java_home

stack_version_home = os.path.join(stack_root, stack_version_unformatted)

# user group
seatunnel_user = status_params.seatunnel_user
seatunnel_group = status_params.seatunnel_group
user_group = status_params.user_group
smoke_user = config['configurations']['cluster-env']['smokeuser']

seatunnel_home = os.path.join(stack_version_home, 'seatunnel')
seatunnel_home_conf_dir = os.path.join(seatunnel_home, 'config')
seatunnel_conf_dir = '/etc/seatunnel/conf'
seatunnel_bin_dir = os.path.join(seatunnel_home, 'bin')
seatunnel_connectors_dir = os.path.join(seatunnel_home, 'connectors')
seatunnel_plugins_dir = os.path.join(seatunnel_home, 'plugins')

seatunnel_lib_dir = os.path.join(seatunnel_home, 'lib')

seatunnel_log_dir = config['configurations']['seatunnel-env']['seatunnel_log_dir']

seatunnel_conf_content = config['configurations']['seatunnel-yaml']['seatunnel_conf_content']
hazelcast_conf_content = config['configurations']['hazelcast-yaml']['hazelcast_conf_content']
hazelcast_client_conf_content = config['configurations']['hazelcast-client-yaml']['hazelcast_client_conf_content']
seatunnel_env_content = config['configurations']['seatunnel-env']['seatunnel_env_content']
seatunnel_log4j2_properties = config['configurations']['seatunnel-log4j2-properties']['seatunnel_log4j2_properties']
seatunnel_log4j2_client_properties = config['configurations']['seatunnel-log4j2-client-properties']['seatunnel_log4j2_client_properties']

network_port = config['configurations']['hazelcast-yaml']['network_port']
cluster_name = config['configurations']['hazelcast-yaml']['cluster_name']
seatunnel_server_hosts = default("/clusterHostInfo/seatunnel_server_hosts", ['localhost'])

seatunnel_cluster_start = 'sh {0}/seatunnel-cluster.sh -d'.format(seatunnel_bin_dir)
seatunnel_cluster_stop = 'sh {0}/stop-seatunnel-cluster.sh'.format(seatunnel_bin_dir)

# --------------------------limits------------------------------------------
limits_conf_dir = "/etc/security/limits.d"
seatunnel_user_nofile_soft = default("/configurations/seatunnel-env/seatunnel_user_nofile_soft", "32768")
seatunnel_user_nofile_hard = default("/configurations/seatunnel-env/seatunnel_user_nofile_hard", "65536")


# dependent service home
flink_home = os.path.join(stack_version_home, "flink")
spark_home = os.path.join(stack_version_home, "spark")

hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()

kinit_path_local = get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))
security_enabled = config['configurations']['cluster-env']['security_enabled']
smokeuser = config['configurations']['cluster-env']['smokeuser']
smokeuser_principal = config['configurations']['cluster-env']['smokeuser_principal_name']
smoke_user_keytab = config['configurations']['cluster-env']['smokeuser_keytab']
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name']
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
hdfs_site = config['configurations']['hdfs-site']
default_fs = config['configurations']['core-site']['fs.defaultFS']

dfs_type = default("/clusterLevelParams/dfs_type", "")

import functools
#create partial functions with common arguments for every HdfsResource call
#to create/delete/copyfromlocal hdfs directories/files we need to call params.HdfsResource in code
HdfsResource = functools.partial(
  HdfsResource,
  user=hdfs_user,
  hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore",
  security_enabled = security_enabled,
  keytab = hdfs_user_keytab,
  kinit_path_local = kinit_path_local,
  hadoop_bin_dir = hadoop_bin_dir,
  hadoop_conf_dir = hadoop_conf_dir,
  principal_name = hdfs_principal_name,
  hdfs_site = hdfs_site,
  default_fs = default_fs,
  immutable_paths = get_not_managed_resources(),
  dfs_type = dfs_type
)