# Ambari Management Pack



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
