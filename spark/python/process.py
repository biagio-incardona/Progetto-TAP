from __future__ import print_function

import sys
import json
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.streaming import StreamingContext
import pyspark
from datetime import datetime
import time
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql.session import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoderEstimator, VectorAssembler
from pyspark.ml.feature import StopWordsRemover, Word2Vec, RegexTokenizer
from pyspark.ml.classification import LogisticRegression
from pyspark.sql import Row
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.classification import NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import spacy
from collections import Counter
from string import punctuation

sid = SentimentIntensityAnalyzer()

#if you've downloaded the medium version use
#nlp = spacy.load("en_core_web_md")

#if you've downloaded the largest version use
nlp = spacy.load("en_core_web_lg")

get_twitch_schema = tp.StructType([
    tp.StructField(name = 'username', dataType = tp.StringType(),  nullable = True),
    tp.StructField(name = 'timestamp', dataType = tp.LongType(),  nullable = True),
    tp.StructField(name = 'mex', dataType = tp.StringType(),  nullable = True),
    tp.StructField(name = 'engagement', dataType = tp.FloatType(), nullable = True),
    tp.StructField(name = 'source', dataType = tp.StringType(),  nullable = True)
])

def get_sentiment(text):
    value = sid.polarity_scores(text)
    value = value['compound']
    return value


def get_keyword(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN'] # 1
    doc = nlp(text.lower()) # 2
    for token in doc:
        # 3
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        # 4
        if(token.pos_ in pos_tag):
            result.append(token.text)

    back = [x for x in Counter(result).most_common(1)]       
    if len(back) == 0:
        return None 
    return back[0][0]

def process(key, rdd):
    global spark
    twitch_chat = rdd.map(lambda (key, value): json.loads(value)).map(
        lambda json_object:(
            json.loads(json_object["message"].encode("ascii", "ignore"))["message"],
            json.loads(json_object["message"].encode("ascii", "ignore"))["username"],
            float(json.loads(json_object["message"].encode("ascii", "ignore"))["engagement"]),
            long(json.loads(json_object["message"].encode("ascii", "ignore"))["timestamp"]),
            json.loads(json_object["message"].encode("ascii", "ignore"))["source"]
        )
    )
    twitch_message = twitch_chat.collect()
    if not twitch_message:
        print("No Messages")
        return
    mex = twitch_message[0][0]
    mex2 = mex
    mex = mex.encode("ascii", "ignore")
    sentiment = get_sentiment(mex)
    keyword = get_keyword(mex2)
    if keyword is None:
        print("Only emoticons not recognized")
        return

    rowRdd = twitch_chat.map(lambda t:
        Row(
            mex = t[0], username = t[1],
            engagement = t[2], timestamp = t[3],
            source = t[4]
        )
    )

    dataFrame = spark.createDataFrame(rowRdd, schema = get_twitch_schema)    
    
    new = dataFrame.rdd.map(lambda x:
        {
            'username' : x['username'],
            'timestamp' : x['timestamp'],
            'mex' : x['mex'],
            'engagement' : x['engagement'],
            'source' : x['source'],
            'mex_sentiment' : sentiment,
            'keyword' : keyword
        }
    )

    final_rdd = new.map(json.dumps).map(lambda x: ('key', x))
    final_rdd.saveAsNewAPIHadoopFile(
        path='-',
        outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
        keyClass="org.apache.hadoop.io.NullWritable",
        valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
        conf=es_write_conf
    )
    
    

sc = SparkContext(appName="SparkSentimentTopicES")
spark = SparkSession(sc)
sc.setLogLevel("WARN")
ssc = StreamingContext(sc, 1)

conf = SparkConf(loadDefaults=False)
conf.set("es.index.auto.create", "true")

brokers="10.0.100.23:9092"
topic = "data"

kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
kvs.foreachRDD(process)

mapping = {
    "mappings": {
        "properties": {
            "timestamp": {
                "type": "date"
            }
        }
    }
}

from elasticsearch import Elasticsearch
elastic_host="10.0.100.51"
elastic_index="data"
elastic_document="_doc"
elastic_port = '9200'
elastic_is_json = "yes"

es_write_conf = {
    "es.nodes" : elastic_host,
    "es.port" : elastic_port,
    "es.resource" : '%s/%s' % (elastic_index,elastic_document),
    "es.input.json" : elastic_is_json
}

elastic = Elasticsearch(hosts=[elastic_host])

response = elastic.indices.create(
    index=elastic_index,
    body=mapping,
    ignore=400 # ignore 400 already exists code
)

if 'acknowledged' in response:
    if response['acknowledged'] == True:
        print ("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])

# catch API error response
elif 'error' in response:
    print ("ERROR:", response['error']['root_cause'])
    print ("TYPE:", response['error']['type'])



ssc.start()
ssc.awaitTermination()
