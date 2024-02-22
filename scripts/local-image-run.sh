#!/bin/bash

docker run --rm --name my-judaica-update --mount type=bind,source=${PWD},target=/app -it drs2-judaica-update