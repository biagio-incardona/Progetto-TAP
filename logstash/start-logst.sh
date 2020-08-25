#!/bin/bash
set -v

ADVISE="Starting logstash"
COMMAND="/logstash/bin/logstash -f /opt/logstash/conf/ingestionToKafka.conf"

echo ${ADVISE}
${COMMAND}
