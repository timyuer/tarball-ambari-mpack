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


# 配置epel源
yum -y install epel-release
# 安装ansible
yum -y install ansible

# 修改/etc/ansible/ansible.cfg
# [defaults]
# interpreter_python=/usr/bin/python3

# ------------------ 离线安装 ------------------ #
# 步骤一、找一台能连接互联网并且与内网服务器系统一致的服务器，下载ansible安装包以及所有依赖包
# yum install -y  yum-utils epel-release
# mkdir /root/ansible
# yum install -y --downloadonly --downloaddir=/root/ansible ansible

# 步骤二、打包所有下载的rpm包
# 将下载的离线包目录打包成ansible.tar.gz。
# cd  /root
# tar -zcvf ansible.tar.gz ./ansible

# 步骤三、安装ansible
# 通过U盘或网络拷贝到企业环境服务器，解压缩并执行安装。
# tar -zxvf ansible.tar.gz
# cd ./ansible
# yum localinstall *.rpm
# ansible --version
# ------------------ 离线安装 ------------------ #

# ------------------ 配置ansible ------------------ #
# vim /etc/ansible/hosts
# [master]
# 10.18.18.215 ansible_ssh_user="root" ansible_ssh_pass="Zxyw13579@#" ansible_ssh_port=52222

# [slave]
# 10.18.18.[216:223]

# [slave:vars]
# ansible_ssh_user="root"
# ansible_ssh_pass="Zxyw13579@#"
# ansible_ssh_port=52222
# --- 配置完成后，可以通过ansible all -m ping 测试是否配置成功 --- #

ansible all -m copy -a 'src=/etc/hosts dest=/etc'

ansible-playbook main.yml \
-e timeserver=bdp01.jndv.org \
-e java_url="http://bdp01.jndv.org/BDP/base/zulu8.78.0.19-ca-jdk8.0.412-linux_x64.tar.gz" \
-e mysql_driver_url="http://bdp01.jndv.org/BDP/base/mysql-connector-java-5.1.49.jar" \
-e ambari_url="http://bdp01.jndv.org/HDP3.3.2.0-011/2.7.8.0-211/" \
-e mysql_image_url="http://bdp01.jndv.org/BDP/base/mysql-5.7.44.tar" \
-e curl_url="http://bdp01.jndv.org/BDP/base/curl-7.79.1-oe2203sp4.tar.gz" \
-e 'ansible_python_interpreter=/usr/bin/python3'

# ------------------ centos7 ------------------ #
# ansible-playbook main.yml \
# -e timeserver=bdp01.jndv.org \
# -e java_url="http://bdp01.jndv.org/BDP/base/zulu8.78.0.19-ca-jdk8.0.412-linux_x64.tar.gz" \
# -e mysql_url="http://bdp01.jndv.org/BDP/base/mysql-5.7.44-1.el7.x86_64.rpm-bundle.tar" \
# -e mysql_driver_url="http://bdp01.jndv.org/BDP/base/mysql-connector-java-5.1.49.jar" \
# -e ambari_url="http://bdp01.jndv.org/HDP3.3.2.0-011/2.7.8.0-211/"


# ------------------ openEuler-22.03 ------------------ #
# ansible-playbook main.yml \
# -e timeserver=bdp01.jndv.org \
# -e java_url="http://192.168.1.80:81/BDP/base/zulu8.78.0.19-ca-jdk8.0.412-linux_x64.tar.gz" \
# -e mysql_image_url="http://192.168.1.80:81/BDP/base/mysql-5.7.44.tar" \
# -e mysql_driver_url="http://192.168.1.80:81/BDP/base/mysql-connector-java-5.1.49.jar" \
# -e ambari_url="http://192.168.1.80:81/HDP3.3.2.0-011/2.7.8.0-211/" \
# -e 'ansible_python_interpreter=/usr/bin/python3' \
# -e curl_url="http://192.168.1.80:81/BDP/base/curl-7.79.1-oe2203sp4.tar.gz"


# ------------------ rockylinux-9 ------------------ #
# ansible-playbook main.yml \
# -e timeserver=bdp01.jndv.org \
# -e java_url="http://192.168.1.80:81/BDP/base/zulu8.78.0.19-ca-jdk8.0.412-linux_x64.tar.gz" \
# -e mysql_image_url="http://192.168.1.80:81/BDP/base/mysql_5.7.44.tar" \
# -e mysql_driver_url="http://192.168.1.80:81/BDP/base/mysql-connector-java-5.1.49.jar" \
# -e ambari_url="http://192.168.1.80:81/HDP3.3.2.0-011/2.7.8.0-211/" \
# -e 'ansible_python_interpreter=/usr/bin/python3'