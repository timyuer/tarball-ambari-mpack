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

from time import sleep
from resource_management.core.resources.system import Execute
from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.libraries.functions import format


class service_check(Script):
  def service_check(self, env):
    import params
    env.set_params(params)
    Logger.info("******** check elasticsearch process ********")
    cmd = format(
      "curl -s -o /dev/null -w'%{{http_code}}' http://{elasticsearch_server_host}:{elasticsearch_port} | grep 200")
    if params.xpack_security_enabled:
      cmd = format(
        "curl -s -o /dev/null -w'%{{http_code}}' -u {params.elasticsearch_username}:{params.elasticsearch_password} -k http://{elasticsearch_server_host}:{elasticsearch_port} | grep 200")

    Execute(cmd,
            tries=10,
            try_sleep=10,
            logoutput=True,
            user=params.smoke_user
            )
    Logger.info("check successfully!")


if __name__ == "__main__":
  service_check().execute()
