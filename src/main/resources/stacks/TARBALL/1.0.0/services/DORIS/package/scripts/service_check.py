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
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.validate import call_and_match_output
from resource_management.core.resources.system import Execute
from resource_management.libraries.functions.format import format
from resource_management.core.logger import Logger
from resource_management.core import sudo


class ServiceCheck(Script):
  def service_check(self, env):
    import params
    env.set_params(params)

    if params.security_enabled:
      kinit_cmd = format("{kinit_path_local} -kt {smoke_user_keytab} {smokeuser_principal}; ")
      Execute(kinit_cmd, user=params.smokeuser)

    cmd = format(
      "curl -s -o /dev/null -w'%{{http_code}}' http://{fe_host}:{http_port}/api/bootstrap | grep 200")

    Execute(cmd,
            tries=10,
            try_sleep=10,
            logoutput=True,
            user=params.smokeuser
            )
    Logger.info("check successfully!")


if __name__ == "__main__":
  ServiceCheck().execute()
