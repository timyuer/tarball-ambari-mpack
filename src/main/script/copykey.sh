#!/bin/bash

# ------------ 依赖包 ------------
# yum install -y tcl expect
# -------------------------------
# 创建ssh key，将id_rsa和id_rsa.pub文件分发到各台主机上面。
# 1.创建主机配置文件
# host文件格式
# 192.168.1.10 root 123456
# 192.168.1.20 root 123456
# 192.168.1.30 root 123456
# 2.编写copykey.sh脚本,自动生成密钥并分发key.
# copykey.sh

yum install expect -y

# 判断id_rsa密钥文件是否存在
if [ ! -f ~/.ssh/id_rsa ]; then
  ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa
else
  echo "id_rsa has created ..."
fi

#分发到各个节点,这里分发到host文件中的主机中.
while read line; do
  user=$(echo $line | cut -d " " -f 2)
  ip=$(echo $line | cut -d " " -f 1)
  passwd=$(echo $line | cut -d " " -f 3)

  expect <<EOF
      set timeout 120
      spawn ssh-copy-id $user@$ip
      expect {
        "yes/no" { send "yes\n";exp_continue }
        "password" { send "$passwd\n" }
        "Password" { send "$passwd\n" }
      }
      expect "password" { send "$passwd\n" }
EOF
done <host