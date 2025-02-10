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


def install_tarball(env, name):
  import params
  import status_params
  env.set_params(params)
  from resource_management.libraries.script.script import Script
  config = Script.get_config()
  # -------------------------------download tarball--------------------
  doris_download_url = config['configurations']['doris-download']['doris_download_url']

  Directory(['/etc/doris'],
            mode=0755,
            cd_access='a',
            owner=params.doris_user,
            group=params.user_group,
            create_parents=True
            )
  
  if name == 'fe':
    Directory(params.fe_home, action="delete")

    Directory([params.fe_home, '/etc/doris-fe'],
              mode=0755,
              cd_access='a',
              owner=params.doris_user,
              group=params.user_group,
              create_parents=True
              )

    Execute('wget -O /opt/doris.tar.gz {0}'.format(doris_download_url))
    Execute('mkdir -p {1} && tar -xvf {0} -C {1} --strip-components=1'.format('/opt/doris.tar.gz', '/opt/doris'))
    Execute('rm -rf {0} && mv /opt/doris/fe {0}'.format(params.fe_home))
    # create link
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.fe_home_conf_dir, params.fe_conf_dir))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.fe_home, params.stack_root + "/current/doris-fe"))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.doris_fe_log_dir, params.fe_home + "/log"))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.meta_dir, params.fe_home + "/doris-meta"))
    # chown
    Execute(
      format('chown -R {params.doris_user}:{params.user_group} {params.fe_home}'))
    # delete
    Execute('rm -rf /opt/doris /opt/doris.tar.gz')
    Logger.info('Install the doris-fe Success')

  elif name == 'be':
    Directory([params.be_home], action="delete")

    Directory([params.be_home, '/etc/doris-be'],
              mode=0755,
              cd_access='a',
              owner=params.doris_user,
              group=params.user_group,
              create_parents=True
              )
    
    Execute('wget -O /opt/doris.tar.gz {0}'.format(doris_download_url))
    Execute('mkdir -p {1} && tar -xvf {0} -C {1} --strip-components=1'.format('/opt/doris.tar.gz', '/opt/doris'))
    Execute('rm -rf {0} && mv /opt/doris/be {0}'.format(params.be_home))
    # create link
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.be_home_conf_dir, params.be_conf_dir))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.be_home, params.stack_root + "/current/doris-be"))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.doris_be_log_dir, params.be_home + "/log"))
    # chown
    Execute(format('chown -R {params.doris_user}:{params.user_group} {params.be_home}'))
    
    # delete
    Execute('rm -rf /opt/doris /opt/doris.tar.gz')
    Logger.info('Install the doris-be Success')