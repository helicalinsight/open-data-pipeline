import unittest
from pyspark.sql import SparkSession
import os

class TestSetup(unittest.TestCase):
    def set_up_spark():
        spark = SparkSession.builder \
            .appName("TestDB") \
            .config("spark.jars.packages", "com.crealytics:spark-excel_2.12:0.13.5,org.apache.poi:poi:4.1.2,org.apache.poi:poi-ooxml:4.1.2,org.apache.poi:poi-ooxml-schemas:4.1.2,org.apache.xmlbeans:xmlbeans:3.1.0,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0,org.firebirdsql.jdbc:jaybird:5.0.4.java11,mysql:mysql-connector-java:8.0.13,org.postgresql:postgresql:42.7.1,com.amazon.redshift:redshift-jdbc42:2.1.0.26,net.snowflake:snowflake-jdbc:3.13.30,net.snowflake:spark-snowflake_2.12:2.12.0-spark_3.3,com.microsoft.sqlserver:mssql-jdbc:9.2.1.jre11,org.apache.hadoop:hadoop-aws:3.3.3,com.amazonaws:aws-java-sdk-bundle:1.12.262,com.couchbase.client:spark-connector_2.12:3.3.6,com.databricks:databricks-jdbc:2.7.3") \
            .getOrCreate()
        return spark

