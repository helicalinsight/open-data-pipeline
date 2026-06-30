## Class: Connection

Connection class stores connection information for all user connections loaded in the chat

## Function: get_by_file_name

Returns the connection details based on file name

**Parameters:**
- **file_name**
  - **Type:** str
  - **Description:** file_name for which connection details are needed, if file is users.csv, file_name is users.csv

**Output:**
```json
{
    "file_id": <file_id>,
    "file_name": <file_name>,
    "file_type": <file_type>,
    "full_name": <full_name>
}
```

**Examples:**
```
# Assuming I have added a file users.csv to the chat
connection = Connection.get_by_file_name("users.csv")
```

## Function: get_by_source_name

Returns the connection details based on source name

**Parameters**
- **source_name**
  - **Type:** str
  - **Description:** source_name which was used at the time of connection creation

**Output:**
```json
{
    'connection_id': <connection-id>,
    'host': <host>,
    'port': <port>,
    'user': <user>,
    'password': <password>,
    'database': <database name>,
    'dbtype': <database type>
}
```

**Examples:**
```python
# Assuming I have created a connection to my database using connection name "my_conn"
connection = Connection.get_by_source_name("my_conn")
```

## Function: get

Returns the connection details based on id

**Parameters:**
- **id**
  - **Type:** str
  - **Description:** id of the file or connection_id for the database

**Examples:**
```python
details = Connection.get(id)
```

## Function: items

Returns all the connection details as a list of key-value pairs

**Parameters:**

No Parameters required

**Examples:**
```python
details: List[Dict] = Connection.items()
```

## Function: keys

Returns list of all file ids / connection ids

**Parameters:**

No Parameters required

**Examples:**
```python
keys = Connection.keys()
```

## Class: JobArguments

**Documentation:** This is the class which is used to fetch, update, delete or create new job arguments.


## Function: get

Fetches the dictionary based on the given key and returns the corresponding dictionary.

**Parameters:**
- **config_name**
    - **Type:** str
    - **Description:** The name of the key that has to be fetched.

**Examples:** 
- **example_1:**
```python
JobArguments.get()
```

**output:**
```json
{"__read_file__": {"mode": "append"}, "__read_table__": {"mode": "append"}}
```

- **example_2:**
```python
JobArguments.get("__read_file__")
```

**output:**
```json
{"__read_file__": {"mode": "append"}}
```

## Function: create

creates a new key value pair by taking key and its value as input

**Parameters:**
- **config_name**
    - **Type:** str
    - **Description:** The name of the key that has to be created.
- **config_value**
    - **Type:** str
    - **Description:** The value that has to be created.

**Examples:** 
- **example_1:**
```python
JobArguments.create(config_key="config", config_value="true")
```

**output:**
```json
{"config": "true"}
```

## Function: update

updates the existing dictionary by taking key and its value as input

**Parameters:**
- **config_name**
    - **Type:** str
    - **Description:** The name of the key that has to be updated.
- **config_value**
    - **Type:** str
    - **Description:** The value that has to be updated.

**Examples:** 
- **example_1:**
```python
JobArguments.update(config_name="__read_file__", config_value={"mode": "overwrite"})
```

**output:**
```json
{"__read_file__": {"mode": "overwrite"}}
```

## Function: delete

Deletes the exisiting dictionary based on the key/config_name  given.

**Parameters:**
- **config_name**
    - **Type:** str
    - **Description:** The name of the key that has to be deleted.

**Examples:** 
- **example_1:**
```python
JobArguments.delete(config_name:"__config__")
```

**output:**
```json
{"__read_file__": {"mode": "append"}}
```

## Class: DataframeInformation

**Documentation:** This is the class which is used to fetch, update, delete or create new dataframes.


## Function: get

Fetches the dataframe information based on the given id or alias

**Parameters:**
- **id**
    - **Type:** str
    - **Description:** The id of the dataframe that has to be fetched.
- **alias**
    - **Type:** str
    - **Description:** The alias of the dataframe that has to be fetched.

**Examples:** 
- **example_1:**
```python
DataframeInformation.get()
```

**output:**
```json
{"11223344": {"df": df, "alias": "students"}, "55667788": {"df": df, "alias": "teachers"}}
```

- **example_2:**
```python
DataframeInformation.get(id="11223344")
```

**output:**
```
returns dataframe
```

## Function: update

Updates the dataframe based on given id or alias and dataframe. 
if the id or alias doen't exist raises exception/key error

**Parameters:**
- **id**
    - **Type:** str
    - **Description:** The id of the dataframe that has to be updated.
- **alias**
    - **Type:** str
    - **Description:** The alias of the dataframe that has to be updated.
- **dataframe**
    - **Type:** Dataframe
    - **Description:** The new dataframe that has to be updated.


**Examples:** 
- **example_1:**
```python
DataframeInformation.update(id="11223344", alias="students", dataframe=df1)
```

**output:**
```
True
```

- **example_2:**
```python
      DataframeInformation.update(alias="students", dataframe=df1)
```

**output:**
```
True
```

## Function: create

Creates a new dictionary with id, alias and dataframe.

**Parameters:**
- **id**
    - **Type:** str
    - **Description:** The id of the dataframe that has to be created.
- **alias**
    - **Type:** str
    - **Description:** The alias of the dataframe that has to be created.
- **dataframe**
    - **Type:** Dataframe
    - **Description:** The new dataframe that has to be created.


**Examples:** 
- **example_1:**
```python
DataframeInformation.create(id="123456", alias="sample", dataframe=df)
```

**output:**
```
True
```

- **example_2:**
```python
DataframeInformation.create(alias="sample", dataframe=df)
```

**output:**
```
True
```

## Function: delete

Deletes the dictionary based on the given id or alias.

**Parameters:**
- **id**
    - **Type:** str
    - **Description:** The id of the dataframe that has to be deleted.
- **alias**
    - **Type:** str
    - **Description:** The alias of the dataframe that has to be deleted.


**Examples:** 
- **example_1:**
```python
DataframeInformation.delete(alias="students")
```

**output:**
```
True
```
- **example_2:**
```python
DataframeInformation.delete(id="11223344")
```

**output:**
```
True
```

## Function: convert_to_pandas

Takes spark dataframe as input and converts it to pandas dataframe and returns pandas dataframe

**Parameters:**
- **dataframe**
    - **Type:** dataframe
    - **Description:** The dataframe that has to be converted to pandas.

**Examples:** 
- **example_1:**
```python
DataframeInformation.convert_to_pandas(dataframe)
```

**output:**
```
Pandas dataframe
```

## Function: convert_to_spark

Takes pandas dataframe as input and converts it to spark dataframe and returns spark dataframe

**Parameters:**
- **dataframe**
    - **Type:** dataframe
    - **Description:** The dataframe that has to be converted to spark.

**Examples:** 
- **example_1:**
```python
DataframeInformation.convert_to_spark(dataframe)
```

**output:**
```
Spark dataframe
```

## Class: ReadOrWriteFiles

**Documentation:** This is the class to read or write csv, excel and json files.
To read csv, json and excel files we can also specify kwargs 
some useful links to provide kwargs are as below
- [Read csv kwargs for pandas engine](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html)
- [Read csv kwargs for spark engine](https://spark.apache.org/docs/latest/sql-data-sources-csv.html)
- [Read excel kwargs for pandas engine](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html)
- [Read excel kwargs for spark engine](https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/api/pyspark.pandas.read_excel.html)
- [Write csv kwargs for pandas engine](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)
- [Write csv kwargs for spark engine](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.html#pyspark.sql.DataFrameWriter)
- [Write excel kwargs for pandas engine](https://pandas.pydata.org/pandas-docs/version/0.20/generated/pandas.DataFrame.to_excel.html)
- [Write excel kwargs for spark engine](https://github.com/crealytics/spark-excel#options)
- [Read json kwargs documentation](https://docs.python.org/3/library/json.html#json.load)
- [Write json kwargs documentation](https://docs.python.org/3/library/json.html#json.dump)

**Examples**
- **example_1:**

```python
ReadOrWriteFiles.read_csv(engine="pandas", file_name="students_write.csv", **kwargs)
```

- **example_2:**
```python
kwargs = {
                "sheet_name": "Sheet1",
                "usecols": "A:C",
                "skiprows": 1
            }
ReadOrWriteFiles.read_excel(engine="pandas", file_name="students.xls", **kwargs)
```

- **example_3:**
```python
ReadOrWriteFiles.write_csv(engine="spark", file_name="students_write.csv", **kwargs)
```
- **example_4:**
```python
ReadOrWriteFiles.write_json(file_name="students.json", **kwargs)
```

## Function: read_csv

Reads the csv file based on the given engine and file name,
Returns dataframe based on the engine given

**Parameters:**
- **engine**
    - **Type:** str
    - **Description:** The type of engine to use like pandas or spark.
- **file_name**
    - **Type:** str
    - **Description:** The name of the file to be read.
- **kwargs**
    - **Type:** dict
    - **Description:** In case any configuration has to be passed(Optional).

**Examples:** 
- **example_1:**
```python
ReadOrWriteFiles.read_csv(engine="pandas", file_name="students_write.csv")
```

**output:**
```
dataframe
```

## Function: write_csv

Writes the csv file by taking engine, dataframe and file name

**Parameters:**
- **engine**
    - **Type:** str
    - **Description:** The type of engine to use like pandas or spark.
- **file_name**
    - **Type:** str
    - **Description:** The name of the file to write.
- **dataframe**
    - **Type:** dataframe
    - **Description:** The dataframe to write to csv file.
- **kwargs**
    - **Type:** dict
    - **Description:** In case any configuration has to be passed(Optional).

**Examples:** 
- **example_1:**
```python
ReadOrWriteFiles.write_csv(engine="pandas", file_name="students_write.csv", dataframe = pandas dataframe)
```

**output:**
```
dataframe
```

## Function: read_excel

Reads the excel file based on the given engine and file name, 
Returns dataframe based on the engine given

**Parameters:**
- **engine**
    - **Type:** str
    - **Description:** The type of engine to use like pandas or spark.
- **file_name**
    - **Type:** str
    - **Description:** The name of the file to be read.
- **kwargs**
    - **Type:** dict
    - **Description:** In case any configuration has to be passed(Optional).

**Examples:** 
- **example_1:**
```python
ReadOrWriteFiles.read_excel(engine="pandas", file_name="students_write.csv")
```

**output:**
```
dataframe
```

## Function: write_excel

Writes the excel file by taking engine, dataframe and file name, additionally it accepts kwargs if any specific configuration has to be passed

**Parameters:**
- **engine**
    - **Type:** str
    - **Description:** The type of engine to use like pandas or spark.
- **file_name**
    - **Type:** str
    - **Description:** The name of the file to write.
- **dataframe**
    - **Type:** dataframe
    - **Description:** The dataframe to write to excel file.
- **kwargs**
    - **Type:** dict
    - **Description:** In case any configuration has to be passed(Optional).

**Examples:** 
- **example_1:**
```python
      ReadOrWriteFiles.write_excel(engine="pandas", file_name="students_write.csv", dataframe = pandas dataframe)
```

**output:**
```
dataframe
```

## Function: read_json

Reads the json file based on the given file name and returns json data.

**Parameters:**
- **file_name**
    - **Type:** str
    - **Description:** The name of the file to be read.

**Examples:** 
- **example_1:**
```python
ReadOrWriteFiles.read_json(file_name="students.json")
```

**output:**
```
json_data
```


## Function: write_json

Writes the json file by taking  file name and json data as input, additionaly it takes configuration/kwargs if needed.

**Parameters:**
- **file_name**
    - **Type:** str
    - **Description:** The name of the file to write.
- **json_data**
    - **Type:** dict
    - **Description:** The json_data to write to json file.
- **kwargs**
    - **Type:** dict
    - **Description:** In case any configuration has to be passed(Optional).

**Examples:** 
- **example_1:**
```python
ReadOrWriteFiles.write_json(file_name="students_data.json", json_data=json_data)
```

**output:**
```
True
```


## Class: AodAudit

**Documentation:** This class is used to allow usage tracking for the function called. This creates metadata needed to output usage under "Audit" section.

## Function: record

Allows to decorate any function and record usage for Auditing.

**How to call:**
1. Suppose you have to call spark inbuilt function `spark.read.csv`
2. Calling `AodAudit.record(spark.read.csv)` gives a decorated function for using
3. output = `AodAudit.record(spark.read.csv)(csv_file_path, old_df=None, step_name='read')`. Here, the args passed (`csv_file_path` are passed as it is to the decorated function and the kwargs `old_df` and `step_name` help to capture usage, you can pass `step_name='manual'` if unsure). The output is in same format as expected from `spark.read.csv(csv_file_path)`.

**Examples:**
- **example_1:**
```python
df = AodAudit.record(spark.read.options(**{"header": "true", "inferSchema": "true"}).csv)(csv_file_path, old_df=None, step_name='read')
```


## Class: CustomSparkContext

**documentation:** Custom spark context that extends the functionality of the default spark context

## Function: read_csv

Read csv file using custom spark context

**Parameters**
- **path**
    - **type:** str
    - **description:** path of csv file to load

- **`**kwargs`**
    - **type:** kwargs
    - **description:** named parameters to pass as options for reading

**Examples:**
- **example_1:**
```python
df = CustomSparkContext.read_csv(csv_file_path)
print (df._df)
```
