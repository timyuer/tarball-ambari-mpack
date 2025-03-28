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
from resource_management import Script
from resource_management.core import sudo
from resource_management.core.logger import Logger
from resource_management.core.resources.system import Execute, File
from resource_management.core.exceptions import ComponentIsNotRunning, Fail
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions import Direction
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions import upgrade_summary
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.show_logs import show_logs
from kafka import ensure_base_directories

import upgrade
from kafka import kafka
from install_tarball import install_tarball

class KafkaBroker(Script):

  def install(self, env):
    import params
    env.set_params(params)
    install_tarball(env)

  def configure(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    kafka(upgrade_type=upgrade_type)

  def pre_upgrade_restart(self, env, upgrade_type=None):
    import params
    env.set_params(params)

    if params.version and check_stack_feature(StackFeature.ROLLING_UPGRADE, params.version):
      stack_select.select_packages(params.version)

    # This is extremely important since it should only be called if crossing the HDP 2.3.4.0 boundary.
    if params.version and params.upgrade_direction:
      src_version = dst_version = None
      if params.upgrade_direction == Direction.UPGRADE:
        src_version = upgrade_summary.get_source_version("KAFKA", default_version =  params.version)
        dst_version = upgrade_summary.get_target_version("KAFKA", default_version =  params.version)
      else:
        # These represent the original values during the UPGRADE direction
        src_version = upgrade_summary.get_target_version("KAFKA", default_version =  params.version)
        dst_version = upgrade_summary.get_source_version("KAFKA", default_version =  params.version)

      if not check_stack_feature(StackFeature.KAFKA_ACL_MIGRATION_SUPPORT, src_version) and check_stack_feature(StackFeature.KAFKA_ACL_MIGRATION_SUPPORT, dst_version):
        # Calling the acl migration script requires the configs to be present.
        self.configure(env, upgrade_type=upgrade_type)
        upgrade.run_migration(env, upgrade_type)

  def start(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    self.configure(env, upgrade_type=upgrade_type)

    if params.kerberos_security_enabled:
      if params.version and check_stack_feature(StackFeature.KAFKA_KERBEROS, params.version):
        kafka_kinit_cmd = format("{kinit_path_local} -kt {kafka_keytab_path} {kafka_jaas_principal};")
        Execute(kafka_kinit_cmd, user=params.kafka_user)

    daemon_cmd = format('source {params.conf_dir}/kafka-env.sh ; {params.kafka_start_cmd} >>/dev/null 2>>{params.kafka_err_file} & echo $!>{params.kafka_pid_file}')
    no_op_test = format('ls {params.kafka_pid_file}>/dev/null 2>&1 && ps -p `cat {params.kafka_pid_file}`>/dev/null 2>&1')
    try:
      Execute(daemon_cmd,
              user=params.kafka_user,
              not_if=no_op_test
      )
    except:
      show_logs(params.kafka_log_dir, params.kafka_user)
      raise

  def stop(self, env, upgrade_type=None):
    import os, time, params, signal

    env.set_params(params)
    # Kafka package scripts change permissions on folders, so we have to
    # restore permissions after installing repo version bits
    # before attempting to stop Kafka Broker
    ensure_base_directories()

    if not params.kafka_pid_file or not os.path.isfile(params.kafka_pid_file):
      Logger.info("Kafka is not running. No pid file found.")
      return
    
    try:
      pid = int(sudo.read_file(params.kafka_pid_file))
    except:
      Logger.info("Pid file {0} does not exist or does not contain a process id number".format(params.kafka_pid_file))
      return

    max_wait = 120
    for i in range(max_wait):
      Logger.info("Waiting for Kafka Broker stop, current pid: {0}, seconds: {1}s".format(pid, i + 1))
      try:
        sudo.kill(pid, signal.SIGTERM)
      except OSError, e:
        Logger.info("Kafka Broker is not running, delete pid file: {0}".format(params.kafka_pid_file))
        File(params.kafka_pid_file, action = "delete")
        return
        
      time.sleep(1)

      try:
        check_process_status(params.kafka_pid_file)
      except ComponentIsNotRunning, e:
        File(params.kafka_pid_file, action = "delete")
        return
    
    raise Fail("Cannot stop Kafka Broker after {0} seconds".format(max_wait))


  def disable_security(self, env):
    import params
    if not params.zookeeper_connect:
      Logger.info("No zookeeper connection string. Skipping reverting ACL")
      return
    if not params.secure_acls:
      Logger.info("The zookeeper.set.acl is false. Skipping reverting ACL")
      return
    Execute(
      "{0} --zookeeper.connect {1} --zookeeper.acl=unsecure".format(params.kafka_security_migrator, params.zookeeper_connect), \
      user=params.kafka_user, \
      environment={ 'JAVA_HOME': params.java64_home }, \
      logoutput=True, \
      tries=3)

  def status(self, env):
    import status_params
    env.set_params(status_params)
    check_process_status(status_params.kafka_pid_file)
    
  def get_log_folder(self):
    import params
    return params.kafka_log_dir
  
  def get_user(self):
    import params
    return params.kafka_user

  def get_pid_files(self):
    import status_params
    return [status_params.kafka_pid_file]

if __name__ == "__main__":
  KafkaBroker().execute()
