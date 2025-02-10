#!/usr/bin/env ambari-python-wrap
import os

from resource_management.core.source import InlineTemplate
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.libraries.functions import format
from resource_management.core.resources.system import Execute, Directory, File
from resource_management.core.resources.system import Link
from setup_flink import setup_flink
from flink_service import flink_service


class FlinkHistoryServer(Script):
  def install(self, env):
    import params
    env.set_params(params)
    from install_tarball import install_tarball
    install_tarball(env)
    self.configure(env)

  def configure(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    setup_flink(env, 'historyserver',
                upgrade_type=upgrade_type, action='config')

  def start(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    self.configure(env)
    flink_service('historyserver',
                  upgrade_type=upgrade_type, action='start')

  def stop(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    flink_service('historyserver',
                  upgrade_type=upgrade_type, action='stop')

  def status(self, env):
    import params
    env.set_params(params)
    check_process_status(params.flink_historyserver_pid_file)


if __name__ == "__main__":
  FlinkHistoryServer().execute()
