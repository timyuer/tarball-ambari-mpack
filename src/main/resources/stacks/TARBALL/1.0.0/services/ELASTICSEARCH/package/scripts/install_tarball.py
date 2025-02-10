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


def install_tarball(env, name='elasticsearch'):
  import params
  env.set_params(params)
  from resource_management.libraries.script.script import Script
  config = Script.get_config()
  repo_base_url = config["repositoryFile"]["repositories"][0]["baseUrl"]

  if name == 'elasticsearch':
    # tarball download
    elasticsearch_url = repo_base_url + config['configurations']['elasticsearch-download']['elasticsearch_url']
    
    Directory(params.elastic_home, action="delete")

    Directory('/etc/elasticsearch',
                mode=0755,
                cd_access='a',
                owner=params.elastic_user,
                group=params.user_group,
                create_parents=True
                )

    tmp_es_tar_path = '/tmp/elasticsearch.tar.gz'
    # Download elasticsearch.tar.gz
    Execute(
        'wget {0} -O {1}'.format(elasticsearch_url, tmp_es_tar_path))

    # Install Elasticsearch
    Execute('/bin/rm -rf {0}'.format(params.elastic_home))
    Execute('mkdir -p {0}'.format(params.elastic_home))
    Execute('tar -zxvf {0} -C {1} --strip-components=1 && rm -rf {2}'
              .format(tmp_es_tar_path, params.elastic_home, tmp_es_tar_path))

    # Remove Elasticsearch installation file
    Execute('rm -rf {0}'.format(tmp_es_tar_path))
    # create link
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.elastic_home_conf_dir, params.elastic_conf_dir))
    Execute('rm -rf {1} && ln -sf {0} {1}'.format(params.elastic_home, params.stack_root + "/current/elasticsearch"))


  elif name == 'kibana':
    kibana_url = repo_base_url + config['configurations']['elasticsearch-download']['kibana_url']

    Directory(params.elastic_kibana_home, action="delete")

    # Create directories
    Directory([params.elastic_kibana_home, params.kibana_logging_dest_dir, params.elastic_kibana_pid_dir],
              mode=0755,
              cd_access='a',
              owner=params.elastic_user,
              group=params.user_group,
              create_parents=True
              )

    # Download Kibana
    tmp_kibana_tar_path = '/tmp/kibana.tar.gz'
    Execute(format("wget {kibana_url} -O {tmp_kibana_tar_path}"))

    # Install Kibana
    Execute(format("tar -zxf {tmp_kibana_tar_path} -C {elastic_kibana_home} --strip-components=1"))

    # Ensure all files owned by Kibana user
    Execute(format("chown -R {elastic_user}:{user_group} {elastic_kibana_home}"))

    # Remove Kibana installation file
    Execute(format("rm -rf {tmp_kibana_tar_path}"))

    Execute('echo "Kibana install complete"')