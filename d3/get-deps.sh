#!/bin/bash
mkdir -p html/d3
pushd html/d3
curl -L -O https://github.com/d3/d3/releases/download/v3.5.17/d3.zip
unzip d3.zip
rm -f d3.zip LICENSE
popd
