#!/usr/bin/env bash

SPARK_DIR="./spark/setup"
KAFKA_DIR="./kafka/setup"
echo "Checking dependencies..."
if [ "$(ls -A $SPARK_DIR)" ]; then
     echo "Spark's dependencies found..."
else
    echo "Installing Spark's dependencies..."
    wget https://downloads.apache.org/spark/spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz && \
    mv spark-2.4.6-bin-hadoop2.7.tgz spark/setup;
fi
if [ "$(ls -A $KAFKA_DIR)" ]; then
     echo "Kafka's dependencies found..."
else
    echo "Installing Kafka's dependencies..."
    wget https://downloads.apache.org/kafka/2.4.1/kafka_2.12-2.4.1.tgz && \
    mv kafka_2.12-2.4.1.tgz kafka/setup;
fi

echo "starting ZooKeeper"

docker stop kafkaZK

docker container rm kafkaZK

docker run -e KAFKA_ACTION=start-zk --network tap --ip 10.0.100.22  -p 2181:2181 --name kafkaZK tap2:kafka &

echo "starting Kafka Server"

docker stop kafkaServer

docker container rm kafkaServer

docker run -e KAFKA_ACTION=start-kafka --network tap --ip 10.0.100.23  -p 9092:9092 --name kafkaServer tap2:kafka &

echo "starting LogStash"

docker stop LogStash

docker container rm LogStash

docker run --network tap --ip 10.0.100.11 --name LogStash tap2:logs &

echo "starting Python"

docker stop Python

docker container rm Python

docker run --network tap --ip 10.0.100.10 --name Python -e CHANNEL_TW=greekgodx tap2:python &

echo "starting ElasticSearch"

docker stop ElasticSearch

docker container rm ElasticSearch

docker run -t  -p 9200:9200 -p 9300:9300 --ip 10.0.100.51 --name ElasticSearch --network tap -e "discovery.type=single-node"  tap2:es &

echo "starting kibana"

docker stop Kibana

docker container rm Kibana

docker run -p 5601:5601 --ip 10.0.100.52 --name Kibana --network tap tap2:kibana &

echo "starting Spark"

spark/sparkSubmitPython.sh process.py "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.elasticsearch:elasticsearch-hadoop:7.7.0" &


echo "Waiting for Kibana to start WebServer..."

while ! nc -z 10.0.100.52 5601; do
  printf '.'
  sleep 1
done

echo "Kibana launched"
sleep 15

xdg-open http://localhost:5601/