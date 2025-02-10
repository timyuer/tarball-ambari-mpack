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

from resource_management.libraries.functions.format import format
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.default import default

config = Script.get_config()

seatunnel_user = config['configurations']['seatunnel-env']['seatunnel_user']
seatunnel_group = config['configurations']['seatunnel-env']['seatunnel_group']
user_group = config['configurations']['cluster-env']['user_group']

seatunnel_pid_dir = config['configurations']['seatunnel-env']['seatunnel_pid_dir']
seatunnel_server_pid_file = format("{seatunnel_pid_dir}/seatunnel-server.pid")
