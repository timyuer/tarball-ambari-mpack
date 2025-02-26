#!/bin/bash
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


# 修改hostname
# 1.创建主机配置文件
# /etc/hosts文件格式
# 192.168.1.131 bdp131 bdp131.jndv.org
# 192.168.1.132 bdp132 bdp132.jndv.org
# 192.168.1.133 bdp133 bdp133.jndv.org
# 2.编写copykey.sh脚本,修改hostname.
# udpate_hostname.sh

yum install expect -y

#分发到各个节点,这里分发到host文件中的主机中.
while read line; do
    hostname=$(echo $line | cut -d " " -f 2)
    ip=$(echo $line | cut -d " " -f 1)
    # 排除localhost和空行
    if ! [[ ${line} =~ 'localhost' || -z ${line} ]]; then
        echo 'line: '$line
        expect <<EOF
        set timeout 120
        spawn ssh $ip "echo $hostname > /etc/hostname"
        expect {
            "yes/no" { send "yes\n";exp_continue }
        }
EOF
    fi
done </etc/hosts
