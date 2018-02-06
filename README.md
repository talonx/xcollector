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

To install using wget, run:
```bash
XC_ACCESS_TOKEN=your_access_token bash -c "$(wget -qO- https://git.io/get-xcollector)"
```
To install using curl, run:
```bash
XC_ACCESS_TOKEN=your_access_token bash -c "$(curl -Ls  https://git.io/get-xcollector)"
```
Detailed installation instructions are available on the [Installation](https://github.com/ApptuitAI/xcollector/wiki/Installation) Wiki 

### Development
The master branch is [apptuit-master](https://github.com/ApptuitAI/xcollector/tree/apptuit-master).

### Attributions
xcollector includes...

 * [tcollector](https://github.com/OpenTSDB/tcollector)
 * [python-ssllabs](https://github.com/takeshixx/python-ssllabs)
 * [Grok Exporter](https://github.com/fstab/grok_exporter)
