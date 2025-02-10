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


def dolphinscheduler_service(name, upgrade_type=None, action=None):
  import params

  if action == 'start':
    if name == 'masterserver':
      File(params.master_server_pid_file, action="delete")
      masterserver_no_op_test = as_sudo(["test", "-f", params.master_server_pid_file]) + \
                                " && " + \
                                as_sudo(["pgrep", "-F", params.master_server_pid_file])
      try:
        Execute(format('{params.dolphinscheduler_bin} start master-server'),
                user=params.dolphinscheduler_user,
                not_if=masterserver_no_op_test)
      except:
        show_logs(params.dolphinscheduler_log_dir, user=params.dolphinscheduler_user)
        raise
    elif name == 'workerserver':
      File(params.worker_server_pid_file, action="delete")
      workerserver_no_op_test = as_sudo(["test", "-f", params.worker_server_pid_file]) + \
                                " && " + \
                                as_sudo(["pgrep", "-F", params.worker_server_pid_file])
      try:
        Execute(format('{params.dolphinscheduler_bin} start worker-server'),
                user=params.dolphinscheduler_user,
                not_if=workerserver_no_op_test)
      except:
        show_logs(params.dolphinscheduler_log_dir, user=params.dolphinscheduler_user)
        raise
    elif name == 'apiserver':
      File(params.api_server_pid_file, action="delete")
      apiserver_no_op_test = as_sudo(["test", "-f", params.api_server_pid_file]) + \
                             " && " + \
                             as_sudo(["pgrep", "-F", params.api_server_pid_file])
      try:
        Execute(format('{params.dolphinscheduler_bin} start api-server'),
                user=params.dolphinscheduler_user,
                not_if=apiserver_no_op_test)
      except:
        show_logs(params.dolphinscheduler_log_dir, user=params.dolphinscheduler_user)
        raise
    elif name == 'alertserver':
      File(params.alert_server_pid_file, action="delete")
      alertserver_no_op_test = as_sudo(["test", "-f", params.alert_server_pid_file]) + \
                               " && " + \
                               as_sudo(["pgrep", "-F", params.alert_server_pid_file])
      try:
        Execute(format('{params.dolphinscheduler_bin} start alert-server'),
                user=params.dolphinscheduler_user,
                not_if=alertserver_no_op_test)
      except:
        show_logs(params.dolphinscheduler_log_dir, user=params.dolphinscheduler_user)
        raise

  elif action == 'stop':
    if name == 'masterserver':
      try:
        Execute(format('{params.dolphinscheduler_bin} stop master-server'),
                user=params.dolphinscheduler_user)
      except:
        show_logs(params.dolphinscheduler_log_dir, user=params.dolphinscheduler_user)
        raise

      File(params.master_server_pid_file, action="delete")
    if name == 'workerserver':
      try:
        Execute(format('{params.dolphinscheduler_bin} stop worker-server'),
                user=params.dolphinscheduler_user)
      except:
        show_logs(params.dolphinscheduler_log_dir, user=params.dolphinscheduler_user)
        raise

      File(params.worker_server_pid_file, action="delete")
    if name == 'apiserver':
      try:
        Execute(format('{params.dolphinscheduler_bin} stop api-server'),
                user=params.dolphinscheduler_user)
      except:
        show_logs(params.dolphinscheduler_log_dir, user=params.dolphinscheduler_user)
        raise

      File(params.api_server_pid_file, action="delete")
    if name == 'alertserver':
      try:
        Execute(format('{params.dolphinscheduler_bin} stop alert-server'),
                user=params.dolphinscheduler_user)
      except:
        show_logs(params.dolphinscheduler_log_dir, user=params.dolphinscheduler_user)
        raise

      File(params.alert_server_pid_file, action="delete")
