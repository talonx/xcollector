#!/usr/bin/env bash

BUILD_PROPS=build.props

TOKEN=`grep token= ${BUILD_PROPS} | cut -d'=' -f2`

if [[ -z "${TOKEN// }" ]]
then
  echo "Please put your token in ${BUILD_PROPS} and stop/restart your VM"
  exit 1
fi

sed -i "s/access_token:.*$/access_token: ${TOKEN}/g" xcollector.yml
