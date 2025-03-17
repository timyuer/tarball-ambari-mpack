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

from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.resources.properties_file import PropertiesFile
from resource_management.libraries.resources.template_config import TemplateConfig
from resource_management.core.resources.system import Directory, Execute, File, Link
from resource_management.core.source import StaticFile, Template, InlineTemplate
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions import format
from resource_management.libraries.functions.generate_logfeeder_input_config import generate_logfeeder_input_config
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature
import re

from resource_management.core.logger import Logger

def calculate_folder_md5(path):
  import os
  import hashlib
  md5_hash = hashlib.md5()
  files = os.listdir(path)
  files.sort()
  for filename in files:
    md5_hash.update(filename.encode('utf-8'))
  return md5_hash.hexdigest()

def re_install(env, tarball_path):
  import params
  env.set_params(params)
  Execute('rm -rf /opt/hadoop && mkdir -p /opt/hadoop')
  Execute('tar -zxvf {0} -C {1} --strip-components=1'.format(tarball_path, "/opt/hadoop"))
  md5_flag  = calculate_folder_md5("/opt/hadoop") == calculate_folder_md5(params.hadoop_home)
  if not md5_flag:
    Logger.info("md5 is not equal, will re-install tarball")
    Directory(params.hadoop_home, action="delete")
    Execute('tar -zxf {0} -C {1} --strip-components=1 && rm -f {0}'.format(tarball_path, params.hadoop_home))
  else:
    Logger.info("md5 is equal, will not re-install tarball")
  Execute('rm -rf /opt/hadoop')

def install_tarball(env):
  import params
  env.set_params(params)
  from resource_management.libraries.script.script import Script
  config = Script.get_config()
  # tarball download
  repo_base_url = config["repositoryFile"]["repositories"][0]["baseUrl"]
  hadoop_url = repo_base_url + config['configurations']['hadoop-download']['hadoop_url']
  stack_usr_bin = '/usr/bin'

  tarball_name = hadoop_url.split('/')[-1]
  Execute('wget -O {0} {1}'.format('/tmp/' + tarball_name, hadoop_url))
  
  re_install(env, '/tmp/' + tarball_name)

  Directory([params.hadoop_home, params.hdfs_log_dir_prefix, params.hadoop_pid_dir_prefix],
            mode=0755,
            cd_access='a',
            owner=params.hdfs_user,
            group=params.user_group,
            create_parents=True
            )
  Directory(['/etc/hadoop', params.stack_root + '/current'],
            mode=0755,
            cd_access='a',
            owner=params.hdfs_user,
            group=params.user_group,
            create_parents=True
            )

  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_home, params.stack_version_home+ '/hadoop-hdfs'))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_home, params.stack_version_home+ '/hadoop-yarn'))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_home, params.stack_version_home+ '/hadoop-mapreduce'))
  # create link
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_home + '/etc/hadoop', '/etc/hadoop/conf'))
  exec_shell_template = '''
#!/bin/bash

export HADOOP_LIBEXEC_DIR={0}

exec {1} "$@"
  '''

  File(stack_usr_bin + '/hadoop',
       owner=params.hdfs_user,
       group=params.user_group,
       mode=0755,
       content=exec_shell_template.format(params.hadoop_libexec_dir, params.hadoop_home + '/bin/hadoop'))
  File(stack_usr_bin + '/hdfs',
       owner=params.hdfs_user,
       group=params.user_group,
       mode=0755,
       content=exec_shell_template.format(params.hadoop_libexec_dir, params.hadoop_home + '/bin/hdfs'))
  File(stack_usr_bin + '/yarn',
       owner=params.hdfs_user,
       group=params.user_group,
       mode=0755,
       content=exec_shell_template.format(params.hadoop_libexec_dir, params.hadoop_home + '/bin/yarn'))
  File(stack_usr_bin + '/mapred',
       owner=params.hdfs_user,
       group=params.user_group,
       mode=0755,
       content=exec_shell_template.format(params.hadoop_libexec_dir, params.hadoop_home + '/bin/mapred'))

  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_home, params.stack_root + "/current/hadoop-client"))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_home, params.stack_root + "/current/hadoop-hdfs-client"))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_home, params.stack_root + "/current/hadoop-yarn-client"))
  Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.hadoop_home, params.stack_root + "/current/hadoop-mapreduce-client"))

  # chown
  Execute(format('chown -R {hdfs_user}:{user_group} {hadoop_home}'))
