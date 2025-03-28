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
    if not os.path.exists(path):
        return ""

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

    md5_flag  = calculate_folder_md5(tmp_extract_dir) == calculate_folder_md5(home_dir)
    if not md5_flag:
        Logger.info("md5 is not equal, will re-install tarball")
        Directory(home_dir, action="delete")
        Directory(home_dir,
                    mode=0755,
                    cd_access='a',
                    create_parents=True
                )
        Execute('mv {0}/* {1}/'.format(tmp_extract_dir, home_dir))
    else:
        Logger.info("md5 is equal, will not re-install tarball")

    Execute('rm -rf {0}'.format(tmp_extract_dir))

def install_tarball(env):
    import params
    env.set_params(params)
    from resource_management.libraries.script.script import Script
    config = Script.get_config()
    repo_base_url = config["repositoryFile"]["repositories"][0]["baseUrl"]

    # tarball download
    seatunnel_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_url']
    seatunnel_hadoop3_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_hadoop3_url']
    seatunnel_connector_hive_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_connector_hive_url']
    seatunnel_connector_jdbc_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_connector_jdbc_url']
    seatunnel_connector_doris_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_connector_doris_url']
    seatunnel_connector_cdcmysql_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_connector_cdcmysql_url']
    seatunnel_connector_kafka_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_connector_kafka_url']
    seatunnel_connector_es_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_connector_es_url']
    seatunnel_connector_cdcsqlserver_url = repo_base_url + config['configurations']['seatunnel-download']['seatunnel_connector_cdcsqlserver_url']
    mysql_connector_url = repo_base_url + config['configurations']['seatunnel-download']['mysql_connector_url']
    sqlserver_connector_url = repo_base_url + config['configurations']['seatunnel-download']['sqlserver_connector_url']

    re_install(seatunnel_url, 'seatunnel', params.seatunnel_home)

    Directory([params.seatunnel_home, '/etc/seatunnel'],
                mode=0755,
                cd_access='a',
                owner=params.seatunnel_user,
                group=params.user_group,
                create_parents=True
                )

    # wget plugins lib jars
    Execute('wget -P {0} {1}'.format(params.seatunnel_lib_dir, mysql_connector_url))
    Execute('wget -P {0} {1}'.format(params.seatunnel_lib_dir, sqlserver_connector_url))
    # wget lib jars
    Execute('wget -P {0} {1}'.format(params.seatunnel_lib_dir, seatunnel_hadoop3_url))
    Execute('ln -sf {0} {1}'.format(params.stack_root + '/current/hive-client/lib/hive-exec*.jar', params.seatunnel_lib_dir))
    # wget connectors
    Execute('wget -P {0} {1}'.format(params.seatunnel_connectors_dir, seatunnel_connector_hive_url))
    Execute('wget -P {0} {1}'.format(params.seatunnel_connectors_dir, seatunnel_connector_jdbc_url))
    Execute('wget -P {0} {1}'.format(params.seatunnel_connectors_dir, seatunnel_connector_doris_url))
    Execute('wget -P {0} {1}'.format(params.seatunnel_connectors_dir, seatunnel_connector_cdcmysql_url))
    Execute('wget -P {0} {1}'.format(params.seatunnel_connectors_dir, seatunnel_connector_kafka_url))
    Execute('wget -P {0} {1}'.format(params.seatunnel_connectors_dir, seatunnel_connector_es_url))
    Execute('wget -P {0} {1}'.format(params.seatunnel_connectors_dir, seatunnel_connector_cdcsqlserver_url))
    # create links
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.seatunnel_home_conf_dir, params.seatunnel_conf_dir))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.seatunnel_home, params.stack_root + "/current/seatunnel"))
    # chown
    Execute('chown -R {0}:{1} {2}'.format(params.seatunnel_user, params.user_group, params.seatunnel_home))
