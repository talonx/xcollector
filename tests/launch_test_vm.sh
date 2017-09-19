#!/usr/bin/env bash

cp ../rpm/dist/xcollector-0.6.5-1.x86_64.rpm xcollector.rpm
VAGRANT_VAGRANTFILE=Vagrantfile-centos69 VAGRANT_DOTFILE_PATH=.vagrant_centos69 vagrant up
VAGRANT_VAGRANTFILE=Vagrantfile-centos69 VAGRANT_DOTFILE_PATH=.vagrant_centos69 vagrant ssh -- "cd /vagrant; sudo ./install-centos.sh"
EXIT_CODE=$?
echo "Install process exit code ${EXIT_CODE}"
exit ${EXIT_CODE}
