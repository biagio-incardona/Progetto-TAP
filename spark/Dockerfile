FROM openjdk:8-jre

ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=2.4.6
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH

ADD setup/spark-${SPARK_VERSION}-bin-hadoop2.7.tgz /opt

RUN apt-get update && apt-get -y install bash python python-pip

RUN pip install pyspark numpy elasticsearch kafka-python vaderSentiment
RUN pip install -U spacy

#medium version ~ 100 MB
#RUN python -m spacy download en_core_web_md

#large version ~ 800 MB, I've not enough GBs :(
RUN python -m spacy download en_core_web_lg


# Create Sym Link 
RUN ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop2.7 ${SPARK_DIR} 

ADD python/*  /opt/tap/
# Add Spark Manager
ADD spark-manager.sh $SPARK_DIR/bin/spark-manager

WORKDIR ${SPARK_DIR}
ENTRYPOINT [ "bin/spark-manager" ]
