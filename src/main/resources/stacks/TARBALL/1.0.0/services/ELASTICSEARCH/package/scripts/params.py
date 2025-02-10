#!/usr/bin/env ambari-python-wrap
# -*- coding: utf-8 -*--
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

from resource_management.core.resources import Directory
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions.version import format_stack_version
from resource_management.core.logger import Logger
import status_params

# config object that holds the configurations declared in the -config.xml file
config = Script.get_config()
stack_root = Script.get_stack_root()
tmp_dir = Script.get_tmp_dir()

# This is expected to be of the form #.#.#.#
stack_version_unformatted = config['clusterLevelParams']['stack_version']

hostname = config['agentLevelParams']['hostname']
ambari_server_host = config['ambariLevelParams']['ambari_server_host']

java_home = config['ambariLevelParams']['java_home']
# elastic user group
elastic_user = config['configurations']['elasticsearch-env']['elastic_user']
user_group = config['configurations']['cluster-env']['user_group']
smoke_user = config['configurations']['cluster-env']['smokeuser']

stack_version_home = os.path.join(stack_root, stack_version_unformatted)

elastic_home = os.path.join(stack_version_home, 'elasticsearch')
elastic_head_home = os.path.join(stack_version_home, 'elasticsearch-head')
elastic_kibana_home = os.path.join(stack_version_home, 'elasticsearch-kibana')
elastic_home_conf_dir = elastic_home + '/config'
elastic_conf_dir = '/etc/elasticsearch/conf'
elastic_head_site_dir = elastic_head_home + '/_site'

elastic_log_dir = config['configurations']['elasticsearch-env']['elastic_log_dir']
elastic_pid_dir = status_params.elastic_pid_dir
elastic_pid_file = status_params.elastic_pid_file
elastic_head_pid_dir = status_params.elastic_head_pid_dir
elastic_head_pid_file = status_params.elastic_head_pid_file
elastic_kibana_pid_dir = status_params.elastic_kibana_pid_dir
elastic_kibana_pid_file = status_params.elastic_kibana_pid_file

service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
elastic_scripts_dir = os.path.join(service_packagedir, "scripts")

es_log_file = os.path.join(elastic_log_dir, 'elasticsearch-start.log')

metrics_collector_host = default("/clusterHostInfo/metrics_collector_hosts", ['localhost'])[0]
elasticsearch_server_host = default("/clusterHostInfo/elasticsearch_server_hosts", ['localhost'])[0]


# --------------------------limits------------------------------------------
limits_conf_dir = "/etc/security/limits.d"
elastic_user_nofile_limit = default("/configurations/elasticsearch-env/elastic_user_nofile_limit", "32768")
elastic_user_nproc_limit = default("/configurations/elasticsearch-env/elastic_user_nproc_limit", "65536")

# --------------------------elastic------------------------------------------
cluster_name = config['configurations']['elasticsearch-yml']['cluster_name']
node_attr_rack = config['configurations']['elasticsearch-yml']['node_attr_rack']
path_data = config['configurations']['elasticsearch-yml']['path_data'].strip(",")
elasticsearch_yml = config['configurations']['elasticsearch-yml']['content']

bootstrap_memory_lock = str(config['configurations']['elasticsearch-yml']['bootstrap_memory_lock'])
bootstrap_system_call_filter = str(config['configurations']['elasticsearch-yml']['bootstrap_system_call_filter'])

# Elasticsearch expetcs that boolean values to be true or false and will generate an error if you use True or False.
if bootstrap_memory_lock == 'True':
    bootstrap_memory_lock = 'true'
else:
    bootstrap_memory_lock = 'false'

if bootstrap_system_call_filter == 'True':
    bootstrap_system_call_filter = 'true'
else:
    bootstrap_system_call_filter = 'false'

network_host = config['configurations']['elasticsearch-yml']['network_host']
elasticsearch_port = config['configurations']['elasticsearch-yml']['elasticsearch_port']
elasticsearch_head_port = config['configurations']['elasticsearch-yml']['elasticsearch_head_port']
# metrics_collector_port = config['configurations']['ams-site']['timeline.metrics.service.webapp.address'].split(":")[1]
metrics_collector_port = \
    default("configurations/ams-site/timeline.metrics.service.webapp.address", "0.0.0.0:6188").split(":")[1]
# metrics_collector_pid_path = config['configurations']['ams-env']['metrics_collector_pid_dir']
# metrics_collector_pid_file = os.path.join(metrics_collector_pid_path, "ambari-metrics-collector.pid")


# discovery_zen_ping_unicast_hosts = config['clusterHostInfo']['all_hosts']
elasticsearch_server_hosts = config['clusterHostInfo']['elasticsearch_server_hosts']
# import json
# server_hosts = config['clusterHostInfo']
# print(json.dumps(server_hosts))

# Need to parse the comma separated hostnames to create the proper string format within the configuration file
# Elasticsearch expects the format ["host1","host2"]
discovery_zen_ping_unicast_hosts = '[' + ','.join('"' + x + '"' for x in elasticsearch_server_hosts) + ']'
cluster_initial_master_nodes = '[' + ','.join('"' + x + '"' for x in elasticsearch_server_hosts) + ']'

discovery_zen_minimum_master_nodes = len(elasticsearch_server_hosts) / 2 + 1

gateway_recover_after_nodes = config['configurations']['elasticsearch-yml']['gateway_recover_after_nodes']
node_max_local_storage_nodes = config['configurations']['elasticsearch-yml']['node_max_local_storage_nodes']

action_destructive_requires_name = str(config['configurations']['elasticsearch-yml']['action_destructive_requires_name'])

# Elasticsearch expecgts boolean values to be true or false and will generate an error if you use True or False.
if action_destructive_requires_name == 'True':
    action_destructive_requires_name = 'true'
else:
    action_destructive_requires_name = 'false'

# head requires
http_cors_enabled = config['configurations']['elasticsearch-yml']['http_cors_enabled']
http_cors_allow_origin = config['configurations']['elasticsearch-yml']['http_cors_allow_origin']
http_cors_allow_headers = config['configurations']['elasticsearch-yml']['http_cors_allow_headers']

if http_cors_enabled:
    http_cors_enabled = 'true'
else:
    http_cors_enabled = 'false'

# Elasticsearch expects boolean values to be true or false and will generate an error if you use True or False.
xpack_security_enabled = config['configurations']['elasticsearch-yml']['xpack_security_enabled']

ping_timeout_default = config['configurations']['elasticsearch-yml']['ping_timeout_default']
discovery_zen_ping_timeout = config['configurations']['elasticsearch-yml']['discovery_zen_ping_timeout']
zookeeper_session_timeout = config['configurations']['elasticsearch-yml']['zookeeper.session.timeout']

# --------------------------kibana------------------------------------------
elasticsearch_hosts = '[' + ','.join(
    '"http://' + x + ':' + elasticsearch_port + '"' for x in elasticsearch_server_hosts) + ']'
kibana_server_host = config['configurations']['kibana-yml']['server.host']
kibana_server_port = config['configurations']['kibana-yml']['server.port']
kibana_server_name = config['configurations']['kibana-yml']['server.name']
kibana_logging_dest_dir = config['configurations']['kibana-yml']['logging.dest.dir']
kibana_logging_dest = kibana_logging_dest_dir + '/kibana.log'
kibana_i18n_locale = config['configurations']['kibana-yml']['i18n.locale']
kibana_server_publicBaseUrl = 'http://' + kibana_server_host + ':' + kibana_server_port
#
elasticsearch_username = config['configurations']['kibana-yml']['elasticsearch.username']
elasticsearch_password = config['configurations']['kibana-yml']['elasticsearch.password']

kibana_kibana_content = config['configurations']['kibana-yml']['kibana_kibana_content']
# --------------------------------jvm.-------------------
jvm_options = config['configurations']['elasticsearch-yml']['jvm_options']
jvm_heap_size = config['configurations']['elasticsearch-env']['java_heap_size']

