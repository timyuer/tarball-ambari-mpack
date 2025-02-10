<!--
  ~ Licensed to the Apache Software Foundation (ASF) under one
  ~ or more contributor license agreements.  See the NOTICE file
  ~ distributed with this work for additional information
  ~ regarding copyright ownership.  The ASF licenses this file
  ~ to you under the Apache License, Version 2.0 (the
  ~ "License"); you may not use this file except in compliance
  ~ with the License.  You may obtain a copy of the License at
  ~
  ~   http://www.apache.org/licenses/LICENSE-2.0
  ~
  ~ Unless required by applicable law or agreed to in writing,
  ~ software distributed under the License is distributed on an
  ~ "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
  ~ KIND, either express or implied.  See the License for the
  ~ specific language governing permissions and limitations
  ~ under the License.
-->

# Ambari Management Pack

关于安装包的说明请参考[这里](src/main/package/README.md)

## Installing Management Pack
```bash
ambari-server install-mpack --mpack=/opt/tarball-ambari-mpack-1.0.0.tar.gz --verbose

ambari-server restart
```

## Uninstall Management Pack
```bash
ambari-server uninstall-mpack --mpack-name=tarball-ambari-mpack --verbose

ambari-server restart
```

## mpack 升级
```bash
ambari-server upgrade-mpack --mpack=/opt/tarball-ambari-mpack-1.0.0.tar.gz

ambari-server restart
```

## License
```bash
# license检查
docker run --rm -it -v "$(pwd)":/github/workspace apache/skywalking-eyes header check
# license修复
docker run --rm -it -v "$(pwd)":/github/workspace apache/skywalking-eyes header fix
```
