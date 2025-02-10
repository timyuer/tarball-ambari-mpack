-- mysql -uroot -p

CREATE DATABASE dolphinscheduler DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

-- 修改 {user} 和 {password} 为你希望的用户名和密码
GRANT ALL PRIVILEGES ON dolphinscheduler.* TO '{user}'@'%' IDENTIFIED BY '{password}';
GRANT ALL PRIVILEGES ON dolphinscheduler.* TO '{user}'@'localhost' IDENTIFIED BY '{password}';

flush privileges;
-- 初始化数据库
bash tools/bin/upgrade-schema.sh