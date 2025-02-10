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
import random

from ambari_commons.constants import UPGRADE_TYPE_NON_ROLLING

from resource_management.libraries.script.script import Script
from resource_management.libraries.functions import get_unique_id_and_date
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.core import shell
from resource_management.core.logger import Logger
from resource_management.libraries.functions.check_process_status import (
    check_process_status,
)
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions.validate import call_and_match_output
from setup_zookeeper import setup_zookeeper
from zookeeper_service import zookeeper_service


class ZookeeperServer(Script):

    def install(self, env):
        import params

        env.set_params(params)
        # self.install_packages(env)
        from install_tarball import install_tarball

        install_tarball(env)
        self.configure(env)

    def configure(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        setup_zookeeper(type="server", upgrade_type=upgrade_type)

    def start(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        self.configure(env, upgrade_type=upgrade_type)
        zookeeper_service(action="start", upgrade_type=upgrade_type)

    def stop(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        zookeeper_service(action="stop", upgrade_type=upgrade_type)

    def status(self, env):
        import status_params

        env.set_params(status_params)
        check_process_status(status_params.zk_pid_file)


if __name__ == "__main__":
    ZookeeperServer().execute()
