#!/usr/bin/env ambari-python-wrap

'''
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
'''
import os
import shutil
import glob

from resource_management.libraries.script.script import Script
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.functions.copy_tarball import copy_to_hdfs, get_tarball_paths
from resource_management.libraries.functions import format
from resource_management.core.resources.system import File, Execute
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.functions.constants import StackFeature
from resource_management.libraries.functions.show_logs import show_logs
from resource_management.core.shell import as_sudo
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management.core.logger import Logger
from resource_management.core.source import InlineTemplate, Template


def elasticsearch_service(name, upgrade_type=None, action=None):
  import params

  if action == 'start':
    if name == 'elasticsearchserver':
      File(params.elastic_pid_file, action="delete")
      '''
      # Option                Description
      # ------                -----------
      # -E <KeyValuePair>     Configure a setting
      # -V, --version         Prints elasticsearch version information and exits
      # -d, --daemonize       Starts Elasticsearch in the background
      # -h, --help            show help
      # -p, --pidfile <Path>  Creates a pid file in the specified path on start
      # -q, --quiet           Turns off standard output/error streams logging in console
      # -s, --silent          show minimal output
      # -v, --verbose         show verbose output
      '''
      cmd = format(
        "{elastic_home}/bin/elasticsearch --daemonize --pidfile {elastic_pid_file}")
      elasticsearchserver_no_op_test = as_sudo(["test", "-f", params.elastic_pid_file]) + \
                                       " && " + \
                                       as_sudo(["pgrep", "-F", params.elastic_pid_file])
      try:
        Execute(cmd,
                user=params.elastic_user,
                environment={'JAVA_HOME': params.java_home, 'ES_PATH_CONF': params.elastic_conf_dir, 'ES_HOME': params.elastic_home},
                not_if=elasticsearchserver_no_op_test)

      except:
        show_logs(params.elastic_log_dir, user=params.elastic_user)
        raise
    elif name == 'elasticsearchhead':
      File(params.elastic_head_pid_file, action="delete")
      # Start elasticsearch-head
      cmd = format("cd {elastic_head_home}; /usr/bin/pm2 start /usr/bin/npm --name elasticsearch-head -- run start")
      Execute(cmd, user=params.elastic_user)

      # get elasticsearch-head pid and write file
      Execute(format('/usr/bin/pm2 pid elasticsearch-head > {params.elastic_head_pid_file}'), user=params.elastic_user)

    elif name == 'kibanaserver':
      File(params.elastic_kibana_pid_file, action="delete")

      cmd = format(
        "nohup {elastic_kibana_home}/bin/kibana --log-file {kibana_logging_dest} &")
      kibanahserver_no_op_test = as_sudo(["test", "-f", params.elastic_pid_file]) + \
                                 " && " + \
                                 as_sudo(["pgrep", "-F", params.elastic_pid_file])
      try:
        Execute(cmd,
                user=params.elastic_user,
                environment={'JAVA_HOME': params.java_home})

        Execute(
          "echo $(ps -ef | grep 'elasticsearch-kibana' | grep -v grep  | awk '{print $2}') > " + params.elastic_kibana_pid_file,
          user=params.elastic_user)

      except:
        show_logs(params.elastic_log_dir, user=params.elastic_user)
        raise

  elif action == 'stop':
    if name == 'elasticsearchserver':
      try:
        Execute('ps -ef | grep "org.elasticsearch.bootstrap.Elasticsearch" | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.elastic_user,
                environment={'JAVA_HOME': params.java_home},
                ignore_failures=True)
      except:
        show_logs(params.elastic_log_dir, user=params.elastic_user)
        raise

      File(params.elastic_pid_file, action="delete")
    elif name == 'elasticsearchhead':
      # kill elasticsearch-head
      cmd = format("/usr/bin/pm2 delete elasticsearch-head")
      Execute(cmd, user=params.elastic_user, ignore_failures=True)

      # delete elasticsearch-head pid file
      File(params.elastic_head_pid_file, action="delete")
    elif name == 'kibanaserver':
      # Stop Kibana
      Execute(
        'ps -ef | grep ' + params.elastic_kibana_home +
        ' | grep -v grep | awk \'{print $2}\' | xargs kill -9',
        user=params.elastic_user,
        environment={'JAVA_HOME': params.java_home},
        ignore_failures=True)

      File(params.elastic_kibana_pid_file, action="delete")
