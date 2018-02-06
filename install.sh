#!/usr/bin/env bash

set -e

function setup_log () {
    logfile="xcollector-install.log"

    # location of named pipe is /tmp/pid.tmp
    named_pipe=/tmp/$$.tmp
    # delete the named pipe on exit
    trap "rm -f $named_pipe" EXIT
    # create the named pipe
    mknod $named_pipe p

    # Tee named pipe to both log and STDOUT
    tee <$named_pipe $logfile &
    # Direct all script output to named pipe
    exec 1>$named_pipe 2>&1

}

function print_message () {
    local log_level="info"
    local log_message=$1
    if [ $# == 2 ] ; then
        log_level=$1;
        log_message=$2;
    fi

    if [ "$log_level" == "info" ] ; then
        COLOR="34m";
    elif [ "$log_level" == "success" ] ; then
        COLOR="32m";
    elif [ "$log_level" == "warn" ] ; then
        COLOR="33m";
    elif [ "$log_level" == "error" ] ; then
        COLOR="31m";
    else #default color
        COLOR="0m";
    fi

    STARTCOLOR="\e[$COLOR";
    ENDCOLOR="\e[0m";

    printf "$STARTCOLOR%b$ENDCOLOR" "$log_message";

}

function get_os () {
    # Try lsb_release, fallback with /etc/issue then uname command
    KNOWN_DISTRIBUTION="(Debian|Ubuntu|RedHat|CentOS|openSUSE|Amazon|Arista|SUSE)"
    DISTRIBUTION=$(lsb_release -d 2>/dev/null | grep -Eo $KNOWN_DISTRIBUTION  || grep -Eo $KNOWN_DISTRIBUTION /etc/issue 2>/dev/null || grep -Eo $KNOWN_DISTRIBUTION /etc/Eos-release 2>/dev/null || uname -s)

    if [ $DISTRIBUTION = "Darwin" ]; then
        OS="Mac"
    elif [ -f /etc/debian_version -o "$DISTRIBUTION" == "Debian" -o "$DISTRIBUTION" == "Ubuntu" ]; then
        OS="Debian"
    elif [ -f /etc/redhat-release -o "$DISTRIBUTION" == "RedHat" -o "$DISTRIBUTION" == "CentOS" -o "$DISTRIBUTION" == "Amazon" ]; then
        OS="RedHat"
    # Some newer distros like Amazon may not have a redhat-release file
    elif [ -f /etc/system-release -o "$DISTRIBUTION" == "Amazon" ]; then
        OS="RedHat"
    # Arista is based off of Fedora14/18 but do not have /etc/redhat-release
    elif [ -f /etc/Eos-release -o "$DISTRIBUTION" == "Arista" ]; then
        OS="RedHat"
    # openSUSE and SUSE use /etc/SuSE-release
    elif [ -f /etc/SuSE-release -o "$DISTRIBUTION" == "SUSE" -o "$DISTRIBUTION" == "openSUSE" ]; then
        OS="SUSE"
    fi
    echo $OS
}

function install_debian () {
    print_message "Installing apt-transport-https\n"
    $sudo_cmd apt-get update || printf "'apt-get update' failed, dependencies might not be updated to latest version.\n"
    $sudo_cmd apt-get install -y apt-transport-https
    # Only install dirmngr if it's available in the cache
    # it may not be available on Ubuntu <= 14.04 but it's not required there
    cache_output=$(apt-cache search dirmngr)
    if [ ! -z "$cache_output" ]; then
        print_message "Installing dirmngr\n"
        $sudo_cmd apt-get install -y dirmngr
    fi

    print_message "Installing APT source list for XCollector\n"
    $sudo_cmd sh -c "echo 'deb https://dl.bintray.com/apptuitai/debian/ stable main' > /etc/apt/sources.list.d/apptuit.list"
    print_message "Installing GPG keys for XCollector\n"
    $sudo_cmd apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 379CE192D401AB61

    print_message "Updating XCollector repo\n"
    $sudo_cmd apt-get update -o Dir::Etc::sourcelist="sources.list.d/apptuit.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"
    print_message "Installing XCollector\n"
    $sudo_cmd apt-get install -y --force-yes xcollector
}

function install_redhat () {
    print_message "Installing YUM sources for Apptuit\n"
    $sudo_cmd sh -c "echo -e '[apptuit]\nname=Apptuit.AI\nbaseurl=https://dl.bintray.com/apptuitai/rpm\nenabled=1\ngpgcheck=0\nrepo_gpgcheck=0\n' > /etc/yum.repos.d/apptuit.repo"

    print_message "Installing XCollector\n"
    $sudo_cmd yum -y install xcollector
}

function update_config () {
    print_message "Updating access token in: /etc/xcollector/xcollector.yml\n"
    $sudo_cmd sh -c "sed -e 's/access_token:.*/access_token: $xc_access_token/' -i /etc/xcollector/xcollector.yml"

    if [ -n "$xc_global_tags" ]; then
        print_message "Updating tags in: /etc/xcollector/xcollector.yml\n"
        $sudo_cmd sh -c "/usr/local/xcollector/xcollector.py --set-option-tags $xc_global_tags"
    fi

}

function start_service () {
    restart_cmd="$sudo_cmd /etc/init.d/xcollector restart"
    if [ $(command -v service) ]; then
        restart_cmd="$sudo_cmd service xcollector restart"
    elif [ $(command -v invoke-rc.d) ]; then
        restart_cmd="$sudo_cmd invoke-rc.d xcollector restart"
    fi

    if $xc_install_only; then
       print_message  "warn" "XC_INSTALL_ONLY environment variable set: XCollector will not be started.
You can start it manually using the following command:\n\n\t$restart_cmd\n\n"
        post_complete
        exit
    fi

    print_message "Starting XCollector\n"
    eval $restart_cmd
}

function post_complete () {
    print_message "success" "Installation completed successfully\n"
}

function check_time_diff () {
    print_message "Verifying time offset\n"

    local server_header=""
    if [ $(command -v curl) ]; then
        server_header=$(curl -s --head https://www.google.com/humans.txt | grep '^\s*Date:\s*' | sed 's/\s*Date:\s*//g')
    elif [ $(command -v wget) ]; then
        server_header=$(wget -S --spider https://www.google.com/humans.txt 2>&1 | grep '^\s*Date:\s*' | sed 's/\s*Date:\s*//g')
    fi

    if [ "$server_header" == "" ]; then
        print_message "warn" "Couldn't connect to server to check time difference.
Please verify that the local server time is accurate manually.\n"
        return
    fi

    local server_time=$(date +"%s" -d "$server_header")
    local local_time=$(date +"%s")
    local time_delta=$(($local_time - $server_time))

    if [ $time_delta -ge 300 -o $time_delta -le -300 ]; then
        print_message "warn" "There is too much time difference between local time and Apptuit.
Metrics might now show up in the correct time window when you query\n"
    fi
}

setup_log

if [ -n "$XC_ACCESS_TOKEN" ]; then
    xc_access_token=$XC_ACCESS_TOKEN
fi


if [ -n "$XC_GLOBAL_TAGS" ]; then
    xc_global_tags=$XC_GLOBAL_TAGS
fi

if [ -n "$XC_INSTALL_ONLY" ]; then
    xc_install_only=true
else
    xc_install_only=false
fi

if [ ! $xc_access_token ]; then
    print_message "error" "Please set your Apptuit access-token in XC_ACCESS_TOKEN environment variable.\n"
    exit 1;
fi

if [ $(echo "$UID") = "0" ]; then
    sudo_cmd=''
else
    sudo_cmd='sudo'
fi

OS=$(get_os)
case $OS in
    RedHat)
        install_redhat
        ;;

    Debian)
        install_debian
        ;;

    *)
        print_message "error" "Your OS/distribution is not supported by this install script.\n"
        exit 1;
        ;;
esac

update_config
check_time_diff
start_service
#TODO run a query and verify metrics are posted
post_complete
