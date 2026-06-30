import unittest
from spark_server.pipeline.processor import *
from pyspark.sql import SparkSession
from spark_server.configurations.baseConfig.config import localDirectory

class TestProcessor(unittest.TestCase):
    # creating the instance of the class Processor
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("TestProcessor").config("spark.jars.packages", "org.postgresql:postgresql:42.7.1").getOrCreate()
        cls.pipeline_processor = Processor()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_process_read_files_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertTrue("6651805f1577224b6b08aa6d" in  dataframes.keys())
        self.assertIsNotNone(dataframes["6651805f1577224b6b08aa6d"]["df"])

    def test_process_read_tables_in_pipeline(self):
        pipeline = [{"function": "read_tables", "parameters":  {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor"}, "output": {"df_id": "65dc3fb832b5b2a5665841fb"}}]
        connection_id = {
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "postgres",
                    "sourceName": "Postgres Connector 2",
                    "host": "57.128.161.235",
                    "port": "5432",
                    "username": "airflow",
                    "password": "Helical@1234",
                    "database": "sakila"
                }
            }
        }
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertTrue("65dc3fb832b5b2a5665841fb" in dataframes.keys())
        self.assertIsNotNone(dataframes["65dc3fb832b5b2a5665841fb"]["df"])

    def test_process_export_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}},
                    {'function': 'export', 'parameters': {"export_name": "output", "user_id": "6641ad931a3ba5058c56af19", "chat_id": "665e937aaea87247ea567131", "df_id": "6651805f1577224b6b08aa6d"}, 'output': None}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        base_path=localDirectory._path
        expected_path = os.path.join(base_path, "6641ad931a3ba5058c56af19", "output", "123", "456")
        #expected_path = f"{self.base_path}/spark_server/SCHEDULED_OUTPUT/output"
        self.assertTrue(any(filename.startswith("part-") and filename.endswith(".csv") for filename in
                            os.listdir(expected_path)))

    def test_process_export_table_in_pipeline(self):
        pipeline = [{"function": "read_tables", "parameters": {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor"}, "output": {"df_id": "65dc3fb832b5b2a5665841fb"}},
                    {"function": "export_table", "parameters": {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.test", "df_id": "65dc3fb832b5b2a5665841fb"}}]
        connection_id = {
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "postgres",
                    "sourceName": "Postgres Connector 2",
                    "host": "57.128.161.235",
                    "port": "5432",
                    "username": "airflow",
                    "password": "Helical@1234",
                    "database": "sakila"
                }
            }
        }
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        pipeline = [{"function": "read_tables", "parameters": {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor2"}, "output": {"df_id": "65dc3fb832b5b2a5665841fc"}}]
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertTrue("65dc3fb832b5b2a5665841fc" in dataframes.keys())
        self.assertIsNotNone(dataframes["65dc3fb832b5b2a5665841fc"]["df"])

    def test_process_union_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        file_path2 = os.path.join(base_path, "test_files", "file2.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}}, {'function': 'read_files', 'parameters': {'file_id': 'e8ea0c4d-28c5-4f00-9d69-54a1aee43ffb', 'file_name': 'file2'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}}, {'function': 'union', 'parameters': {'groups': [{'columns': None}], 'df_id': ['6651805f1577224b6b08aa6d', '6651805f1577224b6b08aa6e'], 'file_names': ['file1', 'Studenfile2ts_1'], 'file_id': None}, 'output': {'df_id': '6651809b1577224b6b08aa6f'}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}},"e8ea0c4d-28c5-4f00-9d69-54a1aee43ffb":{"type":"file","details":{"file_name":"file2.csv","file_type":"csv","file_path":file_path2}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertTrue("6651809b1577224b6b08aa6f" in dataframes.keys())
        self.assertIsNotNone(dataframes["6651809b1577224b6b08aa6f"])

    def test_process_join_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        file_path2 = os.path.join(base_path, "test_files", "file2.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}}, {'function': 'read_files', 'parameters': {'file_id': 'e8ea0c4d-28c5-4f00-9d69-54a1aee43ffb', 'file_name': 'file2'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "joins", "parameters": {"df_id": ["6651805f1577224b6b08aa6d", "6651805f1577224b6b08aa6e"],
                                            "groups": [{"join_type": "inner", "left_on": ["id"], "right_on": ["id"]}],
                                            "file_names": ["file1", "file2"]},
                     "output": {"df_id": "65dc40ccdf5fea2a545e4156"}}
                    ]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"Students.csv","file_type":"csv","file_path":file_path1}},"e8ea0c4d-28c5-4f00-9d69-54a1aee43ffb":{"type":"file","details":{"file_name":"file2.csv","file_type":"csv","file_path":file_path2}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(['id_file1', 'name_file1', 'age_file1', 'join_date_file1', 'id_file2', 'name_file2', 'age_file2', 'join_date_file2'],
                         dataframes["65dc40ccdf5fea2a545e4156"]["df"].columns)

    def test_process_add_columns_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}},
                    {"function": "add_columns", "parameters": {"groups": [{"columns": ["school"], "default": "MNS"}], "df_id": "6651805f1577224b6b08aa6d"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(['id', 'name', 'age', 'join_date', 'school'], dataframes["6651805f1577224b6b08aa6d"]["df"].columns)

    def test_process_aggregations_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "aggregate", "parameters": {"groups": [{"columns": ["marks"],"destination_columns": ["sum_marks"],
                    "agg": ["sum"],"group_by": ["name"]}], "df_id": "6651805f1577224b6b08aa6e"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(['name', 'sum_marks'], dataframes["6651805f1577224b6b08aa6e"]["df"].columns)

    def test_process_aggregations_with_output_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "aggregate", "parameters": {"groups": [{"columns": ["marks"],"destination_columns": ["sum_marks"],
                    "agg": ["sum"],"group_by": ["name"]}], "df_id": "6651805f1577224b6b08aa6e"}, "output": {"df_id": "6686988068353bd18b8593dc"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(['name', 'sum_marks'], dataframes["6686988068353bd18b8593dc"]["df"].columns)

    def test_process_arithmetic_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "expression", "parameters": {"groups": [{"query": "marks+20", "destination_column": "marks_total"}], "df_id": "6651805f1577224b6b08aa6e"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(['name', 'marks', 'marks_total'], dataframes["6651805f1577224b6b08aa6e"]["df"].columns)

    def test_process_cast_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "typecast", "parameters": {"groups": [{"columns": ["marks"], "new_type": "float"}], "df_id": "6651805f1577224b6b08aa6e"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(['name', 'marks'], dataframes["6651805f1577224b6b08aa6e"]["df"].columns)
        self.assertEqual(FloatType(), dataframes["6651805f1577224b6b08aa6e"]["df"].schema['marks'].dataType)

    def test_process_concat_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "concat", "parameters": {"groups": [{"columns": ["name", "marks"], "separator": ":", "destination_column": "name_marks"}], "df_id": "6651805f1577224b6b08aa6e"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(["name", "marks", 'name_marks'], dataframes["6651805f1577224b6b08aa6e"]["df"].columns)
    
    def test_process_correlation_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}},
                    {"function": "correlation", "parameters": {"groups": [{"columns": ["id", "age"],  "destination_column":"id_age_correlation"}], "df_id": "6651805f1577224b6b08aa6d"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        config = {'__read_files__0': {'inferSchema': True}}  # adding this because df will have all string columns without this
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf, config)
        self.assertEqual(["id", "name", "age", "join_date", "id_age_correlation"], dataframes["6651805f1577224b6b08aa6d"]["df"].columns)

    def test_process_filter_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "filter_value", "parameters": {"groups": [{"columns": ["name"], "expr":"equals", "value":["Science"]}], "df_id": "6651805f1577224b6b08aa6e"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(2, dataframes["6651805f1577224b6b08aa6e"]["df"].count())

    def test_process_filter_with_output_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "filter_value", "parameters": {"groups": [{"columns": ["name"], "expr":"equals", "value":["Science"]}], "df_id": "6651805f1577224b6b08aa6e"}, "output": {"df_id": "6686988068353bd18b8593dc"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(2, dataframes["6686988068353bd18b8593dc"]["df"].count())
    
    def test_process_rename_columns_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}},
                    {"function": "rename_columns", "parameters": {"groups": [{"old_name": "id", "new_name": "student_id"}], "df_id": "6651805f1577224b6b08aa6d"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(['student_id', 'name', 'age', 'join_date'], dataframes["6651805f1577224b6b08aa6d"]["df"].columns)
    
    def test_process_sql_operations_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "sql", "parameters": {"groups": [{"query": "SELECT * FROM df where marks >= 75 order by name"}], "df_id": "6651805f1577224b6b08aa6e"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(2, dataframes["6651805f1577224b6b08aa6e"]["df"].count())

    def test_process_sql_operations_with_output_in_pipeline(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path4 = os.path.join(base_path, "test_files", "file4.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f4', 'file_name': 'file4'}, 'output': {'df_id': '6651805f1577224b6b08aa6e'}},
                    {"function": "sql", "parameters": {"groups": [{"query": "SELECT * FROM df where marks >= 75 order by name"}], "df_id": "6651805f1577224b6b08aa6e"}, "output": {"df_id": "6686988068353bd18b8593dc"}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f4":{"type":"file","details":{"file_name":"file4.csv","file_type":"csv","file_path":file_path4}}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertEqual(2, dataframes["6686988068353bd18b8593dc"]["df"].count())
    
    def test_process_read_files_in_pipeline_with_config(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "hadoop_local", "flat_files", "file1_with_semicolon.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1_with_semicolon'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1_with_semicolon.csv","file_type":"csv","file_path":file_path1}}}
        config = {'__read_files__0': {'delimiter': ";"}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf, config)
        self.assertTrue("6651805f1577224b6b08aa6d" in  dataframes.keys())
        self.assertIsNotNone(dataframes["6651805f1577224b6b08aa6d"]["df"])

    def test_process_read_tables_in_pipeline_with_config(self):
        pipeline = [{"function": "read_tables", "parameters":  {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor"}, "output": {"df_id": "65dc3fb832b5b2a5665841fb"}}]
        connection_id = {
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "postgres",
                    "sourceName": "Postgres Connector 2",
                    "host": "57.128.161.235",
                    "port": "5432",
                    "username": "airflow",
                    "password": "Helical@1234",
                    "database": "sakila"
                }
            }
        }
        config = {'__read_tables__0': {'dbtable': '(select first_name from actor) as test'}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf, config)
        self.assertTrue("65dc3fb832b5b2a5665841fb" in dataframes.keys())
        self.assertEqual(dataframes["65dc3fb832b5b2a5665841fb"]["df"].columns, ["first_name"])

    def test_process_export_in_pipeline_with_config(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}},
                    {'function': 'export', 'parameters': {"export_name": "output", "user_id": "6641ad931a3ba5058c56af19", "chat_id": "665e937aaea87247ea567131", "df_id": "6651805f1577224b6b08aa6d"}, 'output': None}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}}}
        config = {'__export__': {'delimiter': ";"}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf, config)
        base_path=localDirectory._path
        expected_path = os.path.join(base_path, "6641ad931a3ba5058c56af19", "output", "123", "456")
        #expected_path = f"{self.base_path}/spark_server/SCHEDULED_OUTPUT/output"
        self.assertTrue(any(filename.startswith("part-") and filename.endswith(".csv") for filename in
                            os.listdir(expected_path)))

    def test_process_export_table_in_pipeline_with_config(self):
        pipeline = [{"function": "read_tables", "parameters": {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor"}, "output": {"df_id": "65dc3fb832b5b2a5665841fb"}},
                    {"function": "export_table", "parameters": {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.test", "df_id": "65dc3fb832b5b2a5665841fb"}}]
        connection_id = {
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "postgres",
                    "sourceName": "Postgres Connector 2",
                    "host": "57.128.161.235",
                    "port": "5432",
                    "username": "airflow",
                    "password": "Helical@1234",
                    "database": "sakila"
                }
            }
        }
        config = {'__export__': {'mode': 'append'}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf, config)
        pipeline = [{"function": "read_tables", "parameters": {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor2"}, "output": {"df_id": "65dc3fb832b5b2a5665841fc"}}]
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf)
        self.assertTrue("65dc3fb832b5b2a5665841fc" in dataframes.keys())
        self.assertIsNotNone(dataframes["65dc3fb832b5b2a5665841fc"]["df"])

    def test_process_pytool_in_pipeline_add_df(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}},
                    {'function': 'pytool', 'parameters': {'code': """import pandas as pd

# Create a dictionary of data
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType
from pyspark.sql.functions import to_date
from datetime import date

# Create a Spark session
spark = SparkSession.builder \
    .appName("CreateDataFrameExample") \
    .getOrCreate()

# Define the data
data = [
    (1, "Smith", 25, date(2022, 5, 20)),
    (2, "Tom", 27, date(2022, 8, 10)),
    (5, "Pam", 35, date(2022, 9, 5)),
    (6, "Edward", 40, date(2022, 7, 20))
]

# Define the schema
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("join_date", DateType(), True)
])

# Create the DataFrame
df = spark.createDataFrame(data, schema=schema)

# Show the DataFrame schema
df.printSchema()

# Show the DataFrame content
df.show()
DataframeInformation.create(id="1", alias="new", dataframe=df)
"""}}]
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}}}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, {})
        self.assertTrue("1" in dataframes.keys())
        
    def test_process_pytool_in_pipeline_add_job_args(self):
        base_path = os.path.abspath(os.path.join(__file__, "../../.."))
        file_path1 = os.path.join(base_path, "test_files", "file1.csv")
        config = {'__pytool__1': {'mode': 'append'}}
        pipeline = [{'function': 'read_files', 'parameters': {'file_id': 'fd85ee69-46f5-438b-a1b0-1b4f9581f6f1', 'file_name': 'file1'}, 'output': {'df_id': '6651805f1577224b6b08aa6d'}},
                    {'function': 'pytool', 'parameters': {'code': """import pandas as pd

JobArguments.update("__pytool__1", {"test": "test"})
"""}}]
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        connection_id = {"fd85ee69-46f5-438b-a1b0-1b4f9581f6f1":{"type":"file","details":{"file_name":"file1.csv","file_type":"csv","file_path":file_path1}}}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf, config)
        self.assertTrue("test" in config["__pytool__1"].keys())
        self.assertTrue("6651805f1577224b6b08aa6d" in dataframes.keys())

    def test_process_pytool_in_pipeline_overwrite_read_tables_query(self):
        pipeline = [{'function': 'pytool', 'parameters': {'code': """import pandas as pd

JobArguments.update("__read_tables__1", {"dbtable": '(select last_name from actor) as test'})
"""}}, {"function": "read_tables", "parameters":  {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor"}, "output": {"df_id": "65dc3fb832b5b2a5665841fb"}}]
        connection_id = {
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "postgres",
                    "sourceName": "Postgres Connector 2",
                    "host": "57.128.161.235",
                    "port": "5432",
                    "username": "airflow",
                    "password": "Helical@1234",
                    "database": "sakila"
                }
            }
        }
        config = {'__read_tables__1': {'dbtable': '(select first_name from actor) as test'}}
        schedule_conf = {"schedule_id":"123", "run_id": "456"}
        dataframes = self.pipeline_processor.process(pipeline, connection_id, self.spark, schedule_conf, config)
        self.assertTrue("65dc3fb832b5b2a5665841fb" in dataframes.keys())
        self.assertEqual(dataframes["65dc3fb832b5b2a5665841fb"]["df"].columns, ["last_name"])


if __name__ == "__main__":
    unittest.main()
