#!/bin/bash

SPARK_WORKLOAD=$1

echo "SPARK_WORKLOAD: $SPARK_WORKLOAD"

if [ "$SPARK_WORKLOAD" == "master" ];
then
  cd /opt/spark/bin && ./spark-class org.apache.spark.deploy.master.Master --ip open-data-pipeline-spark-master --port 7077 --webui-port 8080
elif [ "$SPARK_WORKLOAD" == "worker" ];
then
  cd /opt/spark/bin && ./spark-class org.apache.spark.deploy.worker.Worker --webui-port 8080  spark://open-data-pipeline-spark-master:7077
fi