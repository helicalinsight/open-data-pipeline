
**To use new dataframe give dataframe alias in output :**
```yaml
output:
  dataframe_alias: students
  source_id: 669e3404fd5c32fb759d2b2c
```
## Function: add_columns

**Documentation:** This is function to add the columns..

**Parameters:**
- **column**
    - **Type:** list
    - **Description:** The column names to be added.
- **default**
    - **Type:** any
    - **Description:** The default value to add to the given column.

**Examples:** 
- **example_1:**
```yaml
-   function: add_columns
    output: null
    parameters:
      dataframe_alias: data1
      groups:
        - columns:
            - dob
          default: null
      source_id: 669e3404fd5c32fb759d2b2c
```
  ## Function: aggregate

**Documentation:** This is function to perform aggregations on the given columns.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The column names to perform aggregation.
- **agg**
    - **Type:** list
    - **Description:** The aggregation value which has to be performed.
- **destination_columns**
    - **Type:** list
    - **Description:** The destination column name to store aggregation result(optional).
- **group_by**
    - **Type:** list
    - **Description:** The group by column names(optional).

**Examples:** 
- **example_1:**
```yaml
-   function: aggregate
    output: null
    parameters:
        dataframe_alias: numeric_test_data
        groups:
        -   agg:
            - sum
            columns:
            - cost
            destination_columns:
            - sum_cost
            group_by: []
        source_id: 6667f8896t591f2396b14d7
```
## Function: concat

**Documentation:** This is function to perform concatenation on two columns, takes two columns as input and joins with the help of separator and stores in destination column.

**Parameters:**
- **source_column**
    - **Type:** list
    - **Description:** The column names to be concatenated.
- **separator**
    - **Type:** str
    - **Description:** The separator by which column has to be concatenated.
- **destination_columns**
    - **Type:** str
    - **Description:** Name of the the destination column where the result has to be stored.

**Examples:** 
- **example_1:**
```yaml
-   function: concat
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - firstname
            - lastname
          destination_column: full_name
          separator: ' '
      source_id: 669f484ef0926ea7d7b36533
```
## Function: correlation

**Documentation:** This is function to get the correlation value of two given columns and store it in destination column.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names to find correlation.
- **destination_column**
    - **Type:** str
    - **Description:** Name of the the destination column where the result has to be stored.

**Examples:** 
- **example_1:**
```yaml
-   function: correlation
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - min_salary
            - max_salary 
          destination_column: min_max_correlation
      source_id: 669f484ef0926ea7d7b36533
```

## Function: date_format

**Documentation:** This is function to change the date format in the given column.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names to whose date format has to be changed.
- **format**
    - **Type:** str
    - **Description:** The format to which the date column has to be changed.

**Examples:** 
- **example_1:**
```yaml
-   function: date_format
    output: null
    parameters:
      dataframe_alias: enrollments
      groups:
        - columns:
            - dob
          format: dd-mm-yy
      source_id: 669f4e7e941eaacfdedc79f0
```
## Function: deduplicate

**Documentation:** This is function to remove duplicates in the given columns.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names in which duplicates has to be removed.

**Examples:** 
- **example_1:**
```yaml
-   function: deduplicate
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - lastname
      source_id: 669f52faf0926ea7d7b3653a
```
## Function: drop_all_columns_except

**Documentation:** This is function to drop all columns except the given columns.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names which should not be dropped.

**Examples:** 
- **example_1:**
```yaml
-   function: drop_all_columns_except
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - public_id
      source_id: 669f52faf0926ea7d7b3653a
```
## Function: drop_columns

**Documentation:** This is function to drop all the given list of columns.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names which has to be dropped.

**Examples:** 
- **example_1:**
```yaml
-   function: drop_columns
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - public_id
      source_id: 669f52faf0926ea7d7b3653a
```
## Function: drop_na

**Documentation:** This is function to drop na values in the given columns.

**Parameters:**
- **subset**
    - **Type:** list
    - **Description:** The list of column names where na values should be dropped.

**Examples:** 
- **example_1:**
```yaml
-   function: drop_na
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - subset:
            - address
      source_id: 669f502ef0926ea7d7b36535
```

## Function: expression

**Documentation:** This is function to execute arithmetic operations.

**Parameters:**
- **query**
    - **Type:** str
    - **Description:** The query to execute.
- **destination_column**
    - **Type:** str
    - **Description:** The column name to store the result(optional).


**Examples:** 
- **example_1:**
```yaml
-   function: expression
    output: null
    parameters:
      dataframe_alias: data1
      groups:
        - destination_column: new_age
          query: age + 10
      source_id: 669e3404fd5c32fb759d2b2c
```

## Function: extract

**Documentation:** This is function to extract the component from the given column.

**Parameters:**
- **column**
    - **Type:** str
    - **Description:** The column name from which component has to be extracted.
- **component**
    - **Type:** str
    - **Description:** The value of the component.
- **destination_column**
    - **Type:** str
    - **Description:** The destination column name where the result has to be stored.

**Examples:** 
- **example_1:**
```yaml
-   function: extract
    output: null
    parameters:
        dataframe_alias: Enrollments
        groups:
        -   column: dob
            component:
            - year
            destination_column: dob_year
        source_id: 669f52faf0926ea7d7b3653a
```

## Function: fill_na

**Documentation:** This is function to fill na values in the given columns.

**Parameters:**
- **column**
    - **Type:** str
    - **Description:** The column name to perform fill na.
- **value**
    - **Type:** str
    - **Description:** The value that has to be filled.


**Examples:** 
- **example_1:**
```yaml
-   function: fill_na
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - column:
            - public_id
      value: 000
      source_id: 669f502ef0926ea7d7b36535
```

## Function: filter_value

**Documentation:** This is function to perform filter on the given column.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The column names to perform filter.
- **expr**
    - **Type:** str
    - **Description:** The expression to perform filter.
- **value**
    - **Type:** str
    - **Description:** The value that has to be filtered.

**Examples:** 
- **example_1:**
```yaml
-   function: filter_value
    output:
      dataframe_alias: filter_value_cqgiWUI1
      source_id: 669a776d253079a44ba240bf
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - age
          expr: not_equals
          value:
            - 16
      source_id: 669a75baab33f8e26effafca
```

## Function: joins

**Documentation:** This is function to join the files.

**Parameters:**
- **join_type**
    - **Type:** str
    - **Description:** The type of join to perform.
- **left_on**
    - **Type:** str
    - **Description:** The left on columns name.
- **right_on**
    - **Type:** str
    - **Description:** The right on columns name.
- **file_names**
    - **Type:** list
    - **Description:** The name of the files whose join has to be performed.

**Examples:** 
- **example_1:**
```yaml
-   function: joins
    output:
      dataframe_alias: joins_NluLtzAo
      source_id: 669f4861941eaacfdedc79e9
    parameters:
      dataframe_aliases:
        - courses
        - students
      file_names:
        - courses
        - students
      groups:
        - join_type: inner
          left_on:
            - student_id
          right_on:
            - student_id
      source_id:
        - 669f4813941eaacfdedc79e7
        - 669f4813941eaacfdedc79e8
```

## Function: lower_case

**Documentation:** This is function to apply lower case on the given column.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names to perform lower case.


**Examples:** 
- **example_1:**
```yaml
-   function: lower_case
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - firstname
      source_id: 669f52faf0926ea7d7b3653a
```
## Function: read_files

**Documentation:** This is a function to read the files.

**Parameters:**
- **file_id**
    - **Type:** str
    - **Description:** The id of the file to read.
- **file_name**
    - **Type:** str
    - **Description:** The name of the file.

**Examples:** 
- **example_1:**
```yaml
-   function: read_files
    output:
      dataframe_alias: data1
      source_id: 669e3404fd5c32fb759d2b2c
    parameters:
      file_id: 66a7ebc3-8889-4a41-aea9-e1f7eda1d26c
      file_name: Students     
```
## Function: delete_files

**Documentation:** This is a function to delete loaded file from chat.

**Parameters:**
- **source_id**
  - **Type:** str
  - **Description:** The source id for the cache file to be deleted. This can be taken from output of read_files/read_tables. This parameter accepts a single source_id and deletes the related cache file.

**Examples:**
- **example_1:**
```yaml
-   function: delete_files
    parameters:
      source_id: <source_id>
```

## Function: read

**Documentation:** This is function to read files (e.g., CSV, Parquet) from S3 based on file name and connection_id.

**Parameters:**
- **file_name**
    - **Type:** str
    - **Description:** The name of the file in the S3 bucket.
- **connection_id**
    - **Type:** str
    - **Description:** The connection id for the S3 bucket.
- **type**
    - **Type:** str  
    - **Description:** The file type (e.g., .csv, .parquet).
- **source_type**
    - **Type:** str  
    - **Description:** Should be set to "s3" to indicate the S3 data source.

**Examples:** 
- **example_1:**
```yaml
-   function: read
    output:
      dataframe_alias: 2017_Order_Data
      source_id: 669e2884941eaacfdedc798a
    parameters:
      connection_id: 654879fe22a09b96f228302b
      file_name: 2017_Order_Data.csv
      type: .csv
      source_type: s3 
```

## Function: read_tables

**Documentation:** This is function to read the tables based on the table_name and connection_id.

**Parameters:**
- **table_name**
    - **Type:** str
    - **Description:** The name of the table.
- **connection_id**
    - **Type:** str
    - **Description:** The connection id to which database has to be connected.

**Examples:** 
- **example_1:**
```yaml
-   function: read_tables
    output:
      dataframe_alias: COUNTRY
      source_id: 669e2884941eaacfdedc798a
    parameters:
      columns: []
      connection_id: 667bf6bd88a7682f2eae237d
    table_name: COUNTRY 
```

## Function: export

**Documentation:** This is function to export dataframe to a file based on given parameters

**Parameters:**
- **alias**
  - **Type:** str
  - **Description:** name of the exported file
- **type** 
  - **Type:** str
  - **Description:** type of file to be exported
- **source_id**
  - **Type:** int
  - **description:** dataframe source id to be exported
- **user_id**
  - **Type:** int
  - **description:** user id

**Examples:** 
- **example_1:**
```yaml
- function: export
  parameters:
    alias: 'df_sql_1'
    type: 'csv'
    source_id: 'cc1b87d4-5731-4eb8-a432-2e75ed7f9786'
    user_id: '670e60a261fa9d80ecb984b2'
```


## Function: export_table

**Documentation:** This is function to export dataframe to a table based on given parameters

**Parameters:**
- **connection_id**
  - **Type:**: int
  - **description:** connection id
- **table_name**
  - **Type:** str
  - **description:** The name of the table to export data
- **source_id**
  - **Type:** str
  - **description:** dataframe source id to be exported


**Examples:** 
- **example_1:**
```yaml
- function: export_table
  parameters: 
    connection_id: '67a5aacd9c2987e51bb0338f'
    table_name: 'public.poc_yy_analysis'
    source_id: '5513d613-a989-4841-9423-86ed8995249e'
```

## Function: rearrange_columns

**Documentation:** This is function to rearrange the order of columns.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The column name represents the index position of the column, where -1 denotes the last position, 0 denotes the first position (considered the relative position), and all other columns adjust accordingly.


**Examples:** 
- **example_1:**
```yaml
-   function: rearrange_columns
    output: null
    parameters:
        dataframe_alias: Enrollments
        groups:
        -   columns:
            -   name: 1
        source_id: 669f52faf0926ea7d7b3653a

```

## Function: rename_columns

**Documentation:** This is function to rename the columns.

**Parameters:**
- **old_name**
    - **Type:** str
    - **Description:** The existing column name.
- **new_name**
    - **Type:** str
    - **Description:** The new column name.

**Examples:** 
- **example_1:**
```yaml
-   function: rename_columns
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - new_name: new_age
          old_name: age
      source_id: 669f52faf0926ea7d7b3653a
```

## Function: replace_special_characters

**Documentation:** This is function to replace the special characters in the given columns.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names to replace special characters.
- **target_character**
    - **Type:** str
    - **Description:** The target character.
- **replacement_character**
    - **Type:** str
    - **Description:** The replacement character.

**Examples:** 
- **example_1:**
```yaml
-   function: replace_special_characters
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - dob
          replacement_character: '?'
          target_character: /
      source_id: 669f57a0f0926ea7d7b3653d
```

## Function: sort

**Documentation:** This is function to sort the given column.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names to perform sort.
- **ascending**
    - **Type:** bool
    - **Description:** The order of sorting.

**Examples:** 
- **example_1:**
```yaml
-   function: sort
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - ascending: true
          columns:
            - firstname
      source_id: 669f57a0f0926ea7d7b3653d
```

## Function: split

**Documentation:** This is function to split the given column based on the given delimiter.

**Parameters:**
- **column**
    - **Type:** str
    - **Description:** The column name which has to be splitted.
- **delimiter**
    - **Type:** str
    - **Description:** The delimiter based on which split has to be performed.
- **destination_columns**
    - **Type:** list
    - **Description:** The list of column names where the result has to be stored.

**Examples:** 
- **example_1:**
```yaml
-   function: split
    output: null
    parameters:
        dataframe_alias: Enrollments
        groups:
        -   column: dob
            delimiter: '/'
            destination_columns:
            - day
            - month
            - year
        source_id: 669f5881f0926ea7d7b3653e
```
## Function: sql

**Documentation:** This is function to perform sql operation.

**Parameters:**
- **query**
    - **Type:** str
    - **Description:** The query to execute.


**Examples:** 
- **example_1:**
```yaml
-   function: sql
    output:
      dataframe_alias: sql_tKTEthhx
      source_id: 669f4bb0f0926ea7d7b36534
    parameters:
      dataframe_alias: Enrollments
      groups:
        - query: SELECT corr(public_id, age) FROM df
      source_id: 669f484ef0926ea7d7b36533
```

## Function: trim

**Documentation:** This is function to trim the values in the given column.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The column names which has to be trimmed.
- **number_of_characters**
    - **Type:** int
    - **Description:** The number of characters to be trimmed.
- **location**
    - **Type:** str
    - **Description:** The location right or left where trim has to be done.

**Examples:** 
- **example_1:**
```yaml
-   function: trim
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
              - firstname
          location: left
          number_of_characters: 1
      source_id: 669f5881f0926ea7d7b3653e
```
## Function: typecast

**Documentation:** This is function to change the datatype of the column.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The column name to perform cast.
- **new_type**
    - **Type:** list
    - **Description:** The new data type to which the column has to be casted.
- **old_type**
    - **Type:** list
    - **Description:** The existing column type used for date transformations. Stores the original type if specified, otherwise null.


**Examples:** 
- **example_1:**
```yaml
-   function: typecast
    output: null
    parameters:
      dataframe_alias: enrollments
      groups:
        - columns:
            - dob
          new_type: date
          old_type: null
      source_id: 669f4e7e941eaacfdedc79f0
```

## Function: union

**Documentation:** This is function to union the files.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The columns on which union has to be performed(optional).
- **source_id**
    - **Type:** list
    - **Description:** The list of source_id's of files to perform union.
- **file_names**
    - **Type:** str
    - **Description:** The list of filenames to perform union.

**Examples:** 
- **example_1:**
```yaml
-   function: union
    output:
      dataframe_alias: union_XpD0YkNC
      source_id: 669f47e5941eaacfdedc79e6
    parameters:
      dataframe_aliases:
        - union_1
        - union_2
      file_names:
        - union_1
        - union_2
      groups:
        - columns: null
      source_id:
        - 669f47d3941eaacfdedc79e4
        - 669f47d7941eaacfdedc79e5
```

## Function: upper_case

**Documentation:** This is function to apply upper case on the given column.

**Parameters:**
- **columns**
    - **Type:** list
    - **Description:** The list of column names to perform upper case.


**Examples:** 
- **example_1:**
```yaml
-   function: upper_case
    output: null
    parameters:
      dataframe_alias: Enrollments
      groups:
        - columns:
            - firstname
      source_id: 669f52faf0926ea7d7b3653a
```

## Function: when_otherwise

**Documentation:** This is function to perform when otherwise operation.

**Parameters:**
- **query**
    - **Type:** str
    - **Description:** The query to perform when otherwise.
- **destination_column**
    - **Type:** list
    - **Description:** The destination_column name.


**Examples:** 
- **example_1:**
```yaml
-   function: when_otherwise
    output: null
    parameters:
      dataframe_alias: data1
      groups:
        - destination_column:
            - new_column_1
          query: 
            SELECT *, CASE WHEN age < 18 THEN 'minor' ELSE 'adult' END AS new_column_1
            FROM df;
      source_id: 669e3404fd5c32fb759d2b2c
```
