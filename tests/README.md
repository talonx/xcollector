## Run Test Virtual Machines for running xcollector
The scripts in this directory launch test VMs of different Linux flavors and install a software stack in them. The latest version of xcollector is taken from the local deb/rpm dist directories and installed as well. This is to quickly get a testable setup of xcollector up and running with default settings.

Currently supported Linux versions

* Centos 6.9

Current software stack

* Apache Tomcat
* JSPWiki
* nginx

## Prerequisites
You need vagrant installed on the machine where you are running this

## Running the VMs

* Build xcollector deb and rpm packages
* cd tests
* Create a file called build.props and put token=[your Apptuit token]
* Run `./launch_test_vm.sh`

This will

* Launch a VM (at the moment, just one with Centos 6.9)
* Install the software stack
* Install xcollector
* Start pushing data into Apptuit using the token specified

