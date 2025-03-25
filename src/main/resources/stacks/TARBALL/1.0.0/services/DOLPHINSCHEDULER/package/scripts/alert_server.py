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

from resource_management.core.source import InlineTemplate
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.libraries.functions import format
from resource_management.core.resources.system import Execute, Directory, File
from resource_management.core.resources.system import Link
from setup_dolphinscheduler import setup_dolphinscheduler
from dolphinscheduler_service import dolphinscheduler_service


class AlertServer(Script):
  def install(self, env):
    import params
    env.set_params(params)
    self.install_packages(env)
    from install_tarball import install_tarball
    install_tarball(env)

  def configure(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    setup_dolphinscheduler(env, 'alertserver',
                           upgrade_type=upgrade_type, action='config')

  def start(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    self.configure(env)
    dolphinscheduler_service('alertserver',
                             upgrade_type=upgrade_type, action='start')

  def stop(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    dolphinscheduler_service('alertserver',
                             upgrade_type=upgrade_type, action='stop')

  def status(self, env):
    import params
    env.set_params(params)
    check_process_status(params.alert_server_pid_file)


if __name__ == "__main__":
  AlertServer().execute()
