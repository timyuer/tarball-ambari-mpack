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

Ambari Agent

"""

from ambari_commons import OSConst
from ambari_commons.os_family_impl import OsFamilyFuncImpl, OsFamilyImpl
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions.show_logs import show_logs
from resource_management.core.resources.system import Execute, File
from resource_management.core.resources.service import Service


def zookeeper_service(action="start", upgrade_type=None):
    import params

    cmd = format("env ZOOCFGDIR={conf_dir} ZOOCFG=zoo.cfg {zk_bin}/zkServer.sh")

    if action == "start":
        daemon_cmd = format("source {conf_dir}/zookeeper-env.sh ; {cmd} start")
        no_op_test = format(
            "ls {zk_pid_file} >/dev/null 2>&1 && ps -p `cat {zk_pid_file}` >/dev/null 2>&1"
        )

        try:
            Execute(daemon_cmd, not_if=no_op_test, user=params.zk_user)
        except:
            show_logs(params.zk_log_dir, params.zk_user)
            raise

        if params.security_enabled:
            kinit_cmd = format(
                "{kinit_path_local} -kt {smoke_user_keytab} {smokeuser_principal};"
            )

            Execute(kinit_cmd, user=params.smokeuser)

    elif action == "stop":
        daemon_cmd = format("source {conf_dir}/zookeeper-env.sh ; {cmd} stop")
        try:
            Execute(daemon_cmd, user=params.zk_user)
        except:
            show_logs(params.zk_log_dir, params.zk_user)
            raise
        File(params.zk_pid_file, action="delete")
