#!/usr/bin/env bash

docker build spark/. --tag tap2:spark

echo "--------------------------------------------"

docker build elasticsearch/. --tag tap2:es

echo "--------------------------------------------"

docker build python/. --tag tap2:python

echo "--------------------------------------------"

docker build logstash/. --tag tap2:logs

echo "--------------------------------------------"

docker build kafka/. --tag tap2:kafka

echo "--------------------------------------------"

docker build kibana/. --tag tap2:kibana
