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
from resource_management.core.logger import Logger
from resource_management.libraries.functions import format

config = Script.get_config()

elastic_pid_dir = config['configurations']['elasticsearch-env']['elastic_pid_dir']
elastic_pid_file = format("{elastic_pid_dir}/elasticsearch.pid")

elastic_head_pid_dir = config['configurations']['elasticsearch-env']['elastic_head_pid_dir']
elastic_head_pid_file = format("{elastic_head_pid_dir}/elasticsearch-head.pid")

elastic_kibana_pid_dir = config['configurations']['elasticsearch-env']['elastic_kibana_pid_dir']
elastic_kibana_pid_file = format("{elastic_kibana_pid_dir}/elasticsearch-kibana.pid")
