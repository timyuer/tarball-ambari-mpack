# 一、初始化进行免密和更新hostname
使用ftp拷贝scripts到bdp01服务器，第一第二步骤要用到，执行完可以删掉


这是免密和更新hostname脚本，
copykey.sh是免密脚本，免密脚本需要创建host文件
直接执行sh copykey.sh即可

updatehostname.sh是更新hostname脚本，需要更新/etc/hosts文件
直接执行sh updatehostname.sh即可

执行完以上脚本需要重启所有服务器！！！

# 二、执行ansible脚本
```bash
yum install ansible -y
```

进入ansible目录
修改conf里面的hosts文件，如果总数是6台机器就不用动


修改config.yaml（x86架构）或者config-aarch64.yml（arm架构）

如果是测试环境不用修改
如果是生产环境需要在bdp01安装http
```bash
yum install httpd
systemctl start httpd && systemctl enable httpd
```

然后需要拷贝http://repo.jndv.org/bdp/文件夹到bdp01下面/var/www/html/

然后执行run.sh，如果是arm需要注释掉run.sh里面的x86的部分

# 三、设置mysql
执行完成之后在bdp01直接执行以下脚本
```bash
MYSQL_PASSWORD='i@1LH*I%Wju9'
docker exec mysql bash -c "mysql -uroot -p\"${MYSQL_PASSWORD}\" -e \"CREATE USER 'ambari'@'%' IDENTIFIED BY 'ambari'\""
docker exec mysql bash -c "mysql -uroot -p\"${MYSQL_PASSWORD}\" -e \"GRANT ALL PRIVILEGES ON *.* TO 'ambari'@'%';\""
docker exec mysql bash -c "mysql -uroot -p\"${MYSQL_PASSWORD}\" -e \"CREATE DATABASE ambari\""
docker cp /var/lib/ambari-server/resources/Ambari-DDL-MySQL-CREATE.sql mysql:/opt/Ambari-DDL-MySQL-CREATE.sql
docker exec mysql bash -c "mysql -uroot -p\"${MYSQL_PASSWORD}\" --database=ambari < /opt/Ambari-DDL-MySQL-CREATE.sql"
docker exec mysql bash -c "mysql -uroot -p\"${MYSQL_PASSWORD}\" -e \"FLUSH PRIVILEGES\""
```
# 四、设置ambari-server
```bash
# 快速设置ambari
dbhost=bdp01.jndv.org
ambari-server setup --jdbc-db=mysql --jdbc-driver=/usr/share/java/mysql-connector-java.jar -s
ambari-server setup --java-home=/usr/local/java --database=mysql --databasehost=${dbhost} --databaseport=3306 --databasename=ambari --databaseusername=ambari --databasepassword='ambari' -s
```

# 五、安装mpack
然后将/var/www/html/bdp/tarball-ambari-mpack-1.0.0.tar.gz拷贝到/opt/目录下面

```bash
# scp -r /www/repo/bdp/ 192.168.1.71:/var/www/html/ 这个只能测试环境用，生产环境需要ftp
cp /var/www/html/bdp/tarball-ambari-mpack-1.0.0.tar.gz /opt/
# 安装mpack
ambari-server install-mpack --mpack=/opt/tarball-ambari-mpack-1.0.0.tar.gz
# 重启ambari-server
ambari-server restart
```

# 六、安装大数据平台
进入网页
http://bdp01.jndv.org:8080
账号密码 admin/admin

![第1步](picture/b57923aa-a5b2-43a6-a47e-c0a7da369abc.png)
![第2步](picture/image.png)

repo地址填http://repo.jndv.org/bdp/x86_64/或者http://repo.jndv.org/bdp/aarch64/

![第3步](picture/1ff62a41-b685-41e6-848d-38e7f45bf7b5.png)
![第4步](picture/d7aacb7a-6fdb-4bf0-8015-948ed855c7ab.png)
![第5步](picture/e9a9c979-584c-485c-aafd-3cd4e0da9b6a.png)
![第6步](picture/efd0382c-b6a7-450e-8381-7818cb8b9a90.png)

第7步需要
kafka-broker选择bdp04,bdp05,bdp06
frontend选择bdp06
其他不用动

![第7步](picture/c54e627f-89c6-46df-8194-d17405544b89.png)

第8步,需要
datanode和nodemanager全部勾选，
Backend选择bdp03,bdp04,bdp05
其他不用动

![第8步](picture/fec605bc-9aae-42f4-9b7d-5fe0964b79bb.png)

![第9步](picture/8bd66d33-9757-4147-b755-5637ac91727e.png)

如果挂载磁盘在根目录就不用改，如果挂载到/opt/就改一下
![第10步](picture/d3f3fe15-e6d5-4134-a95d-040cd855c1b0.png)

![第11步](picture/998273cc-498f-4efa-b1ce-252251e059d3.png)
![第12步](picture/a82d187f-0ac8-46a2-9976-3d4d000955c7.png)
![第13步](picture/a597f853-e1a7-4429-bf7f-3cd60aeddbe4.png)
![第14步](picture/2b2dff39-bb20-4811-8634-56fb0c28c1f5.png)
等待安装完成，没有报错就可以了
![第15步](picture/8514c755-282d-4aee-bff2-ebb1cbdb5e1f.png)


后面可以自行设置防火墙，但是集群内部服务器必须设置白名单