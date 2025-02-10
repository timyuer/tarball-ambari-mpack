#!/usr/bin/env ambari-python-wrap
import os

from resource_management.core.resources.system import Execute, Directory, File
from resource_management.core.source import InlineTemplate
from resource_management.libraries.script.script import Script
from resource_management.core.exceptions import ClientComponentHasNoStatus
from resource_management.core.resources.system import Link
from setup_flink import setup_flink

class FlinkClient(Script):
  def install(self, env):
    import params
    env.set_params(params)
    from install_tarball import install_tarball
    install_tarball(env)

    self.configure(env)

  def configure(self, env, upgrade_type=None, config_dir=None):
    import params
    env.set_params(params)
    setup_flink(env, "client", upgrade_type=upgrade_type, action='config')

  def status(self, env):
    raise ClientComponentHasNoStatus()


if __name__ == "__main__":
  FlinkClient().execute()
