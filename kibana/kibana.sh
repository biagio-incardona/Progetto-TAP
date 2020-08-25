#!/usr/bin/env bash
# Stop
docker stop kibana

#  Remove previuos container 
docker container rm kibana

# Build
docker build . --tag tap2:kibana

docker stop kibana
docker run -p 5601:5601 --ip 10.0.100.52 --network tap tap2:kibana
