ansible-playbook -i conf/hosts -e @conf/config.yml playbooks/site.yml

# aarch64
# ansible-playbook -i conf/hosts -e @conf/config-aarch64.yml playbooks/site.yml