#!/bin/bash

docker run --rm --name my-judaica-update --mount type=bind,source=${PWD},target=/app --mount type=bind,source=${PWD}/io,target=/app/io --mount type=bind,source=${PWD}/logs,target=/app/logs -it drs2-judaica-update:latest