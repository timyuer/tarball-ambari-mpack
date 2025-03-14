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
import shutil
import glob

from resource_management.libraries.script.script import Script
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.functions.copy_tarball import (
    copy_to_hdfs,
    get_tarball_paths,
)
from resource_management.libraries.functions import format
from resource_management.core.resources.system import File, Execute
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.check_process_status import (
    check_process_status,
)
from resource_management.libraries.functions.constants import StackFeature
from resource_management.libraries.functions.show_logs import show_logs
from resource_management.core.shell import as_sudo, call
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management.core.logger import Logger


def doris_service(name, upgrade_type=None, action=None):
    import params

    if action == "start" and name == "fe":
        File(params.fe_pid_file, action="delete")

        fe_no_op_test = (
            as_sudo(["test", "-f", params.fe_pid_file])
            + " && "
            + as_sudo(["pgrep", "-F", params.fe_pid_file])
        )
        try:
            # register follower before start fe
            fe_maser_host, fe_list = get_fe_list()
            if params.hostname in fe_list:
                Logger.info("This host is already in the FRONTENDS list")
                # start fe
                Execute(
                    format("{fe_bin_dir}/start_fe.sh --daemon"),
                    user=params.doris_user,
                    not_if=fe_no_op_test,
                    environment={"JAVA_HOME": params.java_home},
                )
            else:
                Logger.info("This host is not in the FRONTENDS list, add it")
                register_follower()

                # start fe
                Execute(
                    format("{fe_bin_dir}/start_fe.sh --helper {fe_maser_host}:{edit_log_port} --daemon"),
                    user=params.doris_user,
                    not_if=fe_no_op_test,
                    environment={"JAVA_HOME": params.java_home},
                )


        except:
            show_logs(params.doris_fe_log_dir, user=params.doris_user)
            raise

    elif action == "stop" and name == "fe":
        try:
            Execute(
                format("{fe_bin_dir}/stop_fe.sh"),
                user=params.doris_user,
                environment={"JAVA_HOME": params.java_home},
                ignore_failures=False,
            )
        except:
            show_logs(params.doris_fe_log_dir, user=params.doris_user)
            raise

        File(params.fe_pid_file, action="delete")

    elif action == "start" and name == "be":
        File(params.be_pid_file, action="delete")

        be_no_op_test = (
            as_sudo(["test", "-f", params.be_pid_file])
            + " && "
            + as_sudo(["pgrep", "-F", params.be_pid_file])
        )
        try:
            # register backend before start be
            register_be()

            # start be
            Execute(
                format("{be_bin_dir}/start_be.sh --daemon"),
                user=params.doris_user,
                not_if=be_no_op_test,
                environment={"JAVA_HOME": params.java_home},
            )
        except:
            show_logs(params.doris_be_log_dir, user=params.doris_user)
            raise

    elif action == "stop" and name == "be":
        try:
            Execute(
                format("{be_bin_dir}/stop_be.sh"),
                user=params.doris_user,
                environment={"JAVA_HOME": params.java_home},
                ignore_failures=True,
            )
        except:
            show_logs(params.doris_be_log_dir, user=params.doris_user)
            raise

        File(params.be_pid_file, action="delete")

    elif action == "register_be" and name == "be":
        register_be()

    elif action == "get_fe_master" and name == "fe":
        get_fe_master()

    elif action == "get_be_list" and name == "fe":
        get_be_list()


def register_be():
    import params
    from doris_tool import DorisTool
    try:
        # init DorisTool
        db = DorisTool(
            host=format("{fe_host}"),
            user="root",
            password="",
            port = int(format("{query_port}")),
            database="mysql"
        )
        # connect to database
        db.connect()

        be_list = get_be_list()
        if params.hostname in be_list:
            Logger.info("This host is already in the backend list")
        else:
            Logger.info("This host is not in the backend list, add it")
            sql = format("ALTER SYSTEM ADD BACKEND '{hostname}:{heartbeat_service_port}'")
            Logger.info("add_be: " + sql)
            db.execute_update(sql)
    finally:
        # close database connection
        db.close()

def get_be_list():
    import params
    import json
    from doris_tool import DorisTool
    be_list = []
    try:
        # init DorisTool
        db = DorisTool(
            host=format("{fe_host}"),
            user="root",
            password="",
            port = int(format("{query_port}")),
            database="mysql"
        )
        # connect to database
        db.connect()

        sql = "SHOW BACKENDS"
        Logger.info("get_be_list: " + sql)
        result = db.execute_query(sql)
        Logger.info("query result:" + json.dumps(result, indent=4))
        for row in result:
            json_dict = json.loads(json.dumps(row))
            be_list.append(json_dict['Host'])
    except:
        Logger.error("Connect {0} Failed !!!".format(params.fe_host))
        raise
    finally:
        # close database connection
        db.close()
    return be_list


def get_fe_master():
    fe_maser_host, fe_list = get_fe_list()
    return fe_maser_host

def get_fe_list():
    import params
    import json
    from doris_tool import DorisTool
    fe_list = []
    fe_master_host = params.fe_host
    try:
        # init DorisTool
        db = DorisTool(
            host=format("{fe_host}"),
            user="root",
            password="",
            port = int(format("{query_port}")),
            database="mysql"
        )
        # connect to database
        db.connect()

        sql = "SHOW FRONTENDS"
        Logger.info("get_fe_master: " + sql)
        result = db.execute_query(sql)
        Logger.info("query result:" + json.dumps(result, indent=4))
        for row in result:
            json_dict = json.loads(json.dumps(row))
            fe_list.append(json_dict['Host'])
            IsMaster = json_dict['IsMaster']
            if IsMaster == "true":
                Logger.info("Master: " + json_dict['Host'])
                fe_master_host = json_dict['Host']
    except:
        Logger.error("Connect {0} Failed !!!".format(params.fe_host))
        raise
    finally:
        # close database connection
        db.close()
    
    return (fe_master_host, fe_list)


def register_follower():
    import params
    from doris_tool import DorisTool
    try:
        # init DorisTool
        db = DorisTool(
            host=format("{fe_host}"),
            user="root",
            password="",
            port = int(format("{query_port}")),
            database="mysql"
        )
        # connect to database
        db.connect()

        fe_maser_host, fe_list = get_fe_list()
        if params.hostname == fe_maser_host:
            Logger.info("This host is the master, no need to register follower")
            return

        if params.hostname in fe_list:
            Logger.info("This host is already in the FRONTENDS list")
        else:
            Logger.info("This host is not in the FRONTENDS list, add it")

            sql = format("ALTER SYSTEM ADD FOLLOWER '{hostname}:{edit_log_port}'")
            Logger.info("register_follower: " + sql)
            db.execute_update(sql)
    finally:
        # close database connection
        db.close()
