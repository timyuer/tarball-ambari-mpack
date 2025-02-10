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

dolphinscheduler_user = config['configurations']['dolphinscheduler-env']['dolphinscheduler_user']
dolphinscheduler_group = config['configurations']['dolphinscheduler-env']['dolphinscheduler_group']
user_group = config['configurations']['cluster-env']['user_group']

dolphinscheduler_pid_dir = config['configurations']['dolphinscheduler-env']['dolphinscheduler_pid_dir']
