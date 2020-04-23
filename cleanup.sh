#!/bin/bash

# Perform cleanup after non-graceful shutdown
docker stop pyms-nist-server
docker container rm pyms-nist-server
docker system prune