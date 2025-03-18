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

def re_install(download_url, name, home_dir):
    tmp_extract_dir = '/opt/' + name
    tarball_path = '/opt/' + download_url.split('/')[-1]
    Execute('wget -O {0} {1}'.format(tarball_path, download_url))

    Execute('rm -rf {0} && mkdir -p {0}'.format(tmp_extract_dir))
    Execute('tar -xf {0} -C {1} --strip-components=1'.format(tarball_path, tmp_extract_dir))

    if name == 'fe':
        md5_flag  = calculate_folder_md5(tmp_extract_dir + '/fe') == calculate_folder_md5(home_dir)
        if not md5_flag:
            Logger.info("md5 is not equal, will re-install tarball")
            Directory(home_dir, action="delete")
            Directory(home_dir,
                        mode=0755,
                        cd_access='a',
                        create_parents=True
                    )
            Execute('mv {0}/fe/* {1}/'.format(tmp_extract_dir, home_dir))
        else:
            Logger.info("md5 is equal, will not re-install tarball")
    elif name == 'be':
        md5_flag  = calculate_folder_md5(tmp_extract_dir + '/be') == calculate_folder_md5(home_dir)
        if not md5_flag:
            Logger.info("md5 is not equal, will re-install tarball")
            Directory(home_dir, action="delete")
            Directory(home_dir,
                        mode=0755,
                        cd_access='a',
                        create_parents=True
                    )
            Execute('mv {0}/be/* {1}/'.format(tmp_extract_dir, home_dir))
        else:
            Logger.info("md5 is equal, will not re-install tarball")

    Execute('rm -rf {0}'.format(tmp_extract_dir))


def install_tarball(env, name):
  import params
  import status_params
  env.set_params(params)
  from resource_management.libraries.script.script import Script
  config = Script.get_config()
  # -------------------------------download tarball--------------------
  repo_base_url = config["repositoryFile"]["repositories"][0]["baseUrl"]
  doris_download_url = repo_base_url + config['configurations']['doris-download']['doris_download_url']

  Directory(['/etc/doris', params.stack_root + "/current"],
            mode=0755,
            cd_access='a',
            owner=params.doris_user,
            group=params.user_group,
            create_parents=True
            )
  
  if name == 'fe':
    re_install(doris_download_url, 'fe', params.fe_home)

    Directory([params.fe_home, '/etc/doris-fe'],
              mode=0755,
              cd_access='a',
              owner=params.doris_user,
              group=params.user_group,
              create_parents=True
              )

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
    re_install(doris_download_url, 'be', params.be_home)

    Directory([params.be_home, '/etc/doris-be'],
              mode=0755,
              cd_access='a',
              owner=params.doris_user,
              group=params.user_group,
              create_parents=True
              )
    
    # create link
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.be_home_conf_dir, params.be_conf_dir))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.be_home, params.stack_root + "/current/doris-be"))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.doris_be_log_dir, params.be_home + "/log"))
    # chown
    Execute(format('chown -R {params.doris_user}:{params.user_group} {params.be_home}'))
    
    # delete
    Execute('rm -rf /opt/doris /opt/doris.tar.gz')
    Logger.info('Install the doris-be Success')