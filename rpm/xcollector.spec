# Put the RPM in the current directory.
%define _rpmdir .
# Don't check stuff, we know exactly what we want.
%undefine __check_files

%global tcollectordir /usr/local/xcollector
%global collectorsdir %{tcollectordir}/collectors
%global rootdir       %{_srcrpmdir}/..
%global eosdir        %{rootdir}/eos
%global srccollectors %{rootdir}/collectors
%global py2_sitelib   /usr/lib/python2.7/site-packages
%global grokexpdir    %{tcollectordir}/grok_exporter-0.2.1.linux-amd64
%global grokexprootdir %{rootdir}/grok_exporter-0.2.1.linux-amd64

BuildArch:      x86_64
Name:           xcollector
Group:          System/Monitoring
Version:        @PACKAGE_VERSION@
Release:        @RPM_REVISION@
Distribution:   buildhash=@GIT_FULLSHA1@
License:        LGPLv3+
Summary:        Variant of tcollector that pushes metrics to Apptuit
URL:            http://apptuit.ai/xcollector.html
Provides:       xcollector = @PACKAGE_VERSION@-@RPM_REVISION@_@GIT_SHORTSHA1@
Requires:       python(abi) >= @PYTHON_VERSION@
Requires:       python-devel
Requires:       MySQL-python
Requires:       python-requests
Requires:       PyYAML

%description
The xcollector package includes the basic collector and
all of the dependencies these collectors need.

%install
mkdir -p %{buildroot}/%{collectorsdir}/0/
mkdir -p %{buildroot}/etc/init.d/

# set homedir in init script
%{__perl} -pe "s|HOMEDIR|%{tcollectordir}|;" -i %{rootdir}/rpm/initd.sh
# Install the init.d
%{__install} -m 0755 -D %{rootdir}/rpm/initd.sh %{buildroot}/etc/init.d/xcollector

# Install Base files
mkdir -p %{buildroot}%{tcollectordir}/bbm/lib/
mkdir -p %{buildroot}%{tcollectordir}/conf/
mkdir -p %{buildroot}%{tcollectordir}/collectors/lib/
mkdir -p %{buildroot}%{tcollectordir}/collectors/lib/bbm/
mkdir -p %{buildroot}%{tcollectordir}/collectors/etc/
mkdir -p %{buildroot}%{grokexpdir}/patterns/
#%{__install} -m 0755 -D %{rootdir}/bbm/lib/* %{buildroot}%{tcollectordir}/bbm/lib/
%{__install} -m 0755 -D %{grokexprootdir}/grok_exporter %{buildroot}%{grokexpdir}/
%{__install} -m 0755 -D %{grokexprootdir}/patterns/* %{buildroot}%{grokexpdir}/patterns/
%{__install} -m 0755 -D %{rootdir}/conf/* %{buildroot}%{tcollectordir}/conf/
%{__install} -m 0755 -D %{srccollectors}/__init__.py %{buildroot}%{tcollectordir}/collectors/
%{__install} -m 0755 -D %{srccollectors}/lib/bbm/* %{buildroot}%{tcollectordir}/collectors/lib/bbm/
%{__install} -m 0755 -D %{srccollectors}/lib/*py* %{buildroot}%{tcollectordir}/collectors/lib/
%{__install} -m 0755 -D %{srccollectors}/etc/* %{buildroot}%{tcollectordir}/collectors/etc/
%{__install} -m 0755 -D %{rootdir}/tcollector.py %{buildroot}%{tcollectordir}/xcollector.py

# Install Collectors
%{__install} -m 0755 -D %{srccollectors}/0/* %{buildroot}%{collectorsdir}/0/

# Install EOS files
%{__install} -m 0755 -D %{eosdir}/collectors/agent*.sh %{buildroot}/%{collectorsdir}/0/
%{__install} -m 0755 -D %{eosdir}/collectors/eos.py %{buildroot}/%{collectorsdir}/0/
mkdir -p %{buildroot}/usr/bin/
%{__install} -m 0755 -D %{eosdir}/tcollector %{buildroot}/usr/bin/
mkdir -p %{buildroot}/%{py2_sitelib}/
%{__install} -m 0755 -D %{eosdir}/tcollector_agent.py %{buildroot}/%{py2_sitelib}/


%files
%dir %{tcollectordir}
%attr(755, -, -) /etc/init.d/xcollector
%{tcollectordir}/collectors/__init__.py
%dir %{tcollectordir}/collectors/lib/
%{tcollectordir}/collectors/lib/__init__.py
%{tcollectordir}/collectors/lib/utils.py
#%{tcollectordir}/collectors/lib/hadoop_http.py
%dir %{tcollectordir}/collectors/etc/
%{tcollectordir}/collectors/etc/__init__.py
%{tcollectordir}/collectors/etc/config.py
%{tcollectordir}/collectors/etc/yaml_conf.py
#%{tcollectordir}/collectors/etc/flume_conf.py
#%{tcollectordir}/collectors/etc/g1gc_conf.py
#%{tcollectordir}/collectors/etc/graphite_bridge_conf.py
%{tcollectordir}/collectors/etc/grok_exporter_conf.py
#%{tcollectordir}/collectors/etc/jolokia_conf.py
%{tcollectordir}/collectors/etc/mysqlconf.py
%{tcollectordir}/collectors/etc/metric_naming.py
#%{tcollectordir}/collectors/etc/postgresqlconf.py
#%{tcollectordir}/collectors/etc/udp_bridge_conf.py
#%{tcollectordir}/collectors/etc/zabbix_bridge_conf.py
%{tcollectordir}/conf/grok.yml %config(noreplace)
%{tcollectordir}/conf/grok_nginx.yml %config(noreplace)
%{tcollectordir}/conf/grok_tomcat.yml %config(noreplace)
%{tcollectordir}/conf/mysql.yml %config(noreplace)
%{tcollectordir}/conf/xcollector.yml %config(noreplace)
%{tcollectordir}/xcollector.py
%{tcollectordir}/collectors/0/dfstat.py
%{tcollectordir}/collectors/0/ifstat.py
%{tcollectordir}/collectors/0/iostat.py
%{tcollectordir}/collectors/0/netstat.py
%{tcollectordir}/collectors/0/procnettcp.py
%{tcollectordir}/collectors/0/procstats.py
#%{tcollectordir}/collectors/0/smart_stats.py
%{tcollectordir}/collectors/0/mysql.py
%{tcollectordir}/collectors/0/memcache.py
%{tcollectordir}/collectors/0/grok_exporter.py
%{grokexpdir}/grok_exporter
%{grokexpdir}/patterns/aws
%{grokexpdir}/patterns/bacula
%{grokexpdir}/patterns/bro
%{grokexpdir}/patterns/exim
%{grokexpdir}/patterns/firewalls
%{grokexpdir}/patterns/grok-patterns
%{grokexpdir}/patterns/haproxy
%{grokexpdir}/patterns/java
%{grokexpdir}/patterns/junos
%{grokexpdir}/patterns/linux-syslog
%{grokexpdir}/patterns/mcollective
%{grokexpdir}/patterns/mcollective-patterns
%{grokexpdir}/patterns/mongodb
%{grokexpdir}/patterns/nagios
%{grokexpdir}/patterns/nginx-access-log
%{grokexpdir}/patterns/postgresql
%{grokexpdir}/patterns/rails
%{grokexpdir}/patterns/redis
%{grokexpdir}/patterns/ruby
%{grokexpdir}/patterns/tomcat-access-log

%post
chkconfig --add xcollector
if [ ! -L "/etc/xcollector" ]
then
  ln -s %{tcollectordir}/conf /etc/xcollector
fi

%postun
# $1 --> if 0, then it is a deinstall
# $1 --> if 1, then it is an upgrade
if [ $1 -eq 0 ] ; then
    # This is a removal, not an upgrade
    #  $1 versions will remain after this uninstall

    # Clean up collectors
    rm -f /etc/init.d/xcollector
    rm -rf %{tcollectordir}
fi

%package collectors
Summary: The linux OpenTSDB collectors
Group: System/Monitoring
Requires: tcollector >= 1.2.1
%description collectors


%files collectors
%{tcollectordir}/collectors/0/dfstat.py
%{tcollectordir}/collectors/0/ifstat.py
%{tcollectordir}/collectors/0/iostat.py
%{tcollectordir}/collectors/0/netstat.py
%{tcollectordir}/collectors/0/procnettcp.py
%{tcollectordir}/collectors/0/procstats.py
%{tcollectordir}/collectors/0/smart_stats.py

%postun collectors
# $1 --> if 0, then it is a deinstall
# $1 --> if 1, then it is an upgrade
if [ $1 -eq 0 ] ; then
    # This is a removal, not an upgrade
    #  $1 versions will remain after this uninstall

    # Clean up collectors
    rm -f %{tcollectordir}/collectors/0/dfstat.py
    rm -f %{tcollectordir}/collectors/0/ifstat.py
    rm -f %{tcollectordir}/collectors/0/iostat.py
    rm -f %{tcollectordir}/collectors/0/netstat.py
    rm -f %{tcollectordir}/collectors/0/procnettcp.py
    rm -f %{tcollectordir}/collectors/0/procstats.py
    rm -f %{tcollectordir}/collectors/0/smart_stats.py
fi

%package eos
Summary: Linux Collectors and Arista EOS Collectors
Group: System/Monitoring
Requires: tcollector
Requires: EosSdk >= 1.5.1
Obsoletes: tcollectorAgent <= 1.0.2

%description eos
The tcollector-eos subpackage provides files that leverage the EOSSDK to
gather statistics from EOS.  It should be used in conjunction with
the tcollector package and optionally the tcollector-collectors subpackage. If
you run make swix, all three packages will be included.

%files eos
%attr(755, -, -) /usr/bin/tcollector
%{tcollectordir}/collectors/0/agentcpu.sh
%{tcollectordir}/collectors/0/agentmem.sh
%{tcollectordir}/collectors/0/eos.py
%{py2_sitelib}/tcollector_agent.py


%postun eos
# $1 --> if 0, then it is a deinstall
# $1 --> if 1, then it is an upgrade
if [ $1 -eq 0 ] ; then
    # This is a removal, not an upgrade
    #  $1 versions will remain after this uninstall

    # Clean up eos
    rm -f /usr/bin/tcollector
    rm -f %{tcollectordir}/collectors/0/agentcpu.sh
    rm -f %{tcollectordir}/collectors/0/agentmem.sh
    rm -f %{tcollectordir}/collectors/0/eos.py
    rm -f %{py2_sitelib}/tcollector_agent.py*

fi
