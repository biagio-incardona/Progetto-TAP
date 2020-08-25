FROM openjdk:8-jre-alpine
MAINTAINER Biagio Incardona
ENV PATH /opt/logstash/bin:$PATH


RUN apk update && \
	apk add --no-cache wget bash && \
	cd ~ && \
	wget http://download.elastic.co/logstash/logstash/logstash-2.4.0.tar.gz && \
	tar -zxvf logstash-2.4.0.tar.gz && \
	rm logstash-2.4.0.tar.gz && \
	mv logstash-2.4.0 /logstash

ADD start-logst.sh /opt/logstash/bin/start-logst
# Copy All conf here
ADD conf/* /opt/logstash/conf/

EXPOSE 5001
EXPOSE 5002

ENTRYPOINT [ "/opt/logstash/bin/start-logst" ]

