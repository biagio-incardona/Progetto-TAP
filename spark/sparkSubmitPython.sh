#!/usr/bin/env bash
# Stop
docker stop sparkSubmit

# Remove previuos container 
docker container rm sparkSubmit

docker run -e SPARK_ACTION=spark-submit-python -p 4040:4040 --network tap --name sparkSubmit tap2:spark $1 $2
