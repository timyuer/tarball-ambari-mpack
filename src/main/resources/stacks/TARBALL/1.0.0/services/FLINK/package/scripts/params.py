#!/usr/bin/env ambari-python-wrap
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import functools
from resource_management.core.logger import Logger
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

java_home = config['ambariLevelParams']['java_home']

stack_version_home = os.path.join(stack_root, stack_version_unformatted)

flink_home = os.path.join(stack_version_home, "flink")
flink_home_conf_dir = flink_home + "/conf"
flink_conf_dir = "/etc/flink/conf"
flink_bin_dir = flink_home + "/bin"
flink_lib_dir = flink_home + "/lib"
flink_log_dir = config['configurations']['flink-env']['flink_log_dir']
# pid=$FLINK_PID_DIR/flink-$FLINK_IDENT_STRING-$DAEMON.pid
flink_pid_dir = status_params.flink_pid_dir
flink_historyserver_pid_file = status_params.flink_historyserver_pid_file
flink_historyserver_start = format(
    "export HADOOP_CLASSPATH=`hadoop classpath`;{flink_home}/bin/historyserver.sh start")
flink_historyserver_stop = format("{flink_home}/bin/historyserver.sh stop")

host_info = config['clusterHostInfo']
host_level_params = config['ambariLevelParams']

# default hadoop parameters
hadoop_home = stack_select.get_hadoop_dir("home")
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
dfs_type = default("/clusterLevelParams/dfs_type", "")
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name']
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
default_fs = config['configurations']['core-site']['fs.defaultFS']
hdfs_site = config['configurations']['hdfs-site']
hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore"

flink_name = 'flink'
flink_user = status_params.flink_user
flink_group = status_params.flink_group
user_group = status_params.user_group
flink_hdfs_user_dir = format("/user/{flink_user}")
flink_hdfs_dir = format("/{flink_name}")

flink_historyserver_hosts = default("/clusterHostInfo/flink_historyserver_hosts", ['localhost'])
flink_historyserver_host = flink_historyserver_hosts[0]

# params from flink-ambari-config
'''
KEY_ENV_PID_DIR="env.pid.dir"
KEY_ENV_LOG_DIR="env.log.dir"
KEY_ENV_LOG_MAX="env.log.max"
KEY_ENV_YARN_CONF_DIR="env.yarn.conf.dir"
KEY_ENV_HADOOP_CONF_DIR="env.hadoop.conf.dir"
KEY_ENV_HBASE_CONF_DIR="env.hbase.conf.dir"
KEY_ENV_JAVA_HOME="env.java.home"
KEY_ENV_JAVA_OPTS="env.java.opts"
KEY_ENV_JAVA_OPTS_JM="env.java.opts.jobmanager"
KEY_ENV_JAVA_OPTS_TM="env.java.opts.taskmanager"
KEY_ENV_JAVA_OPTS_HS="env.java.opts.historyserver"
KEY_ENV_JAVA_OPTS_CLI="env.java.opts.client"
KEY_ENV_SSH_OPTS="env.ssh.opts"
KEY_HIGH_AVAILABILITY="high-availability"
KEY_ZK_HEAP_MB="zookeeper.heap.mb"
'''
env_java_opts = '-XX:+UseG1GC'
env_log_max = config['configurations']['flink-env']['env_log_max']

historyserver_web_tmpdir = '/tmp/flinkhistoryserver/'
flink_conf_yaml_content = config['configurations']['flink-conf-yaml']['flink-conf-content']
flink_log4j_properties_content = config['configurations']['flink-log4j-properties']['log4j-properties-content']
flink_dependency_jar = config['configurations']['flink-env']['flink_dependency_jar']
HISTORY_WEB_ADDRESS = socket.gethostname()


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
