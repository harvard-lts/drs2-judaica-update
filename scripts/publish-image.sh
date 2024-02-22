#!/bin/bash

docker build --platform linux/amd64 -t artifactory.huit.harvard.edu/lts/drs-judaica-update:1.0.0 . -f Dockerfile
docker image push artifactory.huit.harvard.edu/lts/drs-judaica-update:1.0.0