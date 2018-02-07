[![Latest release](https://img.shields.io/github/release/apptuitai/xcollector.svg)](https://github.com/ApptuitAI/xcollector/releases/latest) [![Build Status](https://api.travis-ci.org/ApptuitAI/xcollector.svg?branch=apptuit-master)](https://travis-ci.org/ApptuitAI/xcollector) 
# XCollector
XCollector is a pluggable data collection framework for reporting metrics to  [apptuit.ai](https://apptuit.ai). It comes with built-in collectors for collecting server metrics. It provides a very simple framework to easily add support for collecting metrics from other services and APIs.

It is a fork of [tcollector](https://github.com/OpenTSDB/tcollector) with support for:
* Reporting metrics to Apptuit
* Extracting metrics from log files (nginx, tomcat)
* Semantic naming conventions for metrics
* RPM and Debian packages for easy installation
* Simple YML based configuration

### Installation
XCollector is available via debian & yum repositories

To install using the installation script and `wget`, run (**replace PASTE_ACCESS_TOKEN_HERE with your Apptuit API access token**):
```bash
XC_ACCESS_TOKEN=PASTE_ACCESS_TOKEN_HERE bash -c "$(wget -qO- https://git.io/get-xcollector)"
```

Alternately, to install using the installation script and `curl`, run (**replace PASTE_ACCESS_TOKEN_HERE with your Apptuit API access token**):
```bash
XC_ACCESS_TOKEN=PASTE_ACCESS_TOKEN_HERE bash -c "$(curl -Ls  https://git.io/get-xcollector)"
```

Detailed installation instructions are available on the [Installation](https://github.com/ApptuitAI/xcollector/wiki/Installation) Wiki 

### Development
The master branch is [apptuit-master](https://github.com/ApptuitAI/xcollector/tree/apptuit-master).

### Attributions
xcollector includes...

 * [tcollector](https://github.com/OpenTSDB/tcollector)
 * [python-ssllabs](https://github.com/takeshixx/python-ssllabs)
 * [Grok Exporter](https://github.com/fstab/grok_exporter)
