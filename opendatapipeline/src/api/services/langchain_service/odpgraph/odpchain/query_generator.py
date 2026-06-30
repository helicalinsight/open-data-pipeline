from ......models.connector import MongoConnector
from ......models.mongo.mongo_factory import MongoFactory
from ......logger.logger import logger, Logger
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
mongo_connector = MongoConnector()
mongo_client=mongo_connector.client

class QueryGenerator:
    """This class provides methods to generate SQL queries and manage MongoDB data related to schema metadata.

    The class connects to MongoDB to retrieve metadata and cache information, and uses this information
    to generate SQL `CREATE TABLE` statements. It also includes methods to map data types from metadata
    to SQLite data types and to generate expected output for SQL queries based on the provided metadata.

    :param session: Optional session parameter used for MongoDB connections, defaults to None
    :type session: object, optional
    """
    def __init__(self,session=None):
        """Constructor method

        Initializes the `QueryGenerator` with a MongoDB connection and creates instances
        of `MongoFactory` for accessing 'chats' and 'cache' collections.

        :param session: Optional session parameter used for MongoDB connections, defaults to None
        :type session: object, optional
        """
        self.session=session
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.mongo_chats = MongoFactory(self.mongo_client, "chats", session=self.session)
        
        self.cache: CacheBase = get_cache(session=self.session)

    @staticmethod
    def map_datatype(datatype):
        """
        Maps data types present in metadata to SQLite data types

        :param datatype: Datatype from the metadata
        :return: SQLite datatype
        """
        if datatype.startswith('int'):
            return 'INTEGER'
        elif datatype == 'object' or datatype.startswith('str'):
            return 'VARCHAR'
        elif datatype.startswith('float'):
            return 'FLOAT'
        elif datatype == 'bool':
            return 'boolean'
        elif datatype == 'date':
            return 'DATE'
        elif datatype == 'datetime64[ns]':
            return 'DATE'
        else:
            return 'others'

    def generate_create_table_statement(self, file_name, datatypes):
        """
        Generates a SQL `CREATE TABLE` statement based on the provided file name and column data types.

        :param file_name: File name from metadata which will be used as the table name
        :type file_name: str
        :param datatypes: Dictionary of column names and their corresponding data types
        :type datatypes: dict
        :return: SQL `CREATE TABLE` query
        :rtype: str
        """
        create_table_query = f" Schema: (\n"
        for column, datatype in datatypes.items():
            datatype = self.map_datatype(datatype)
            create_table_query += f"    {column} {datatype},\n"
        create_table_query = create_table_query.rstrip(",\n") + "\n)"
        return create_table_query

    # @staticmethod
    def extract_column_datatypes_from_mongodb(self, source_id, chat_id):
        """
        Extracts file name and dictionary of column names and data types from the cache collection in MongoDB
        based on the provided source ID.

        :param source_id: Cache ID in MongoDB
        :type source_id: str
        :return: File name and dictionary of columns and their data types
        :rtype: tuple of (str, dict) or (None, None)
        """
        _, chat = self.mongo_chats.get_by_id(chat_id)
        cache = self.cache.get_item(source_id, chat.get("user_id"), chat_id)
        if cache:
            file_name = cache["file_name"]
            datatypes = cache["metadata"]["column_information"]["datatypes"]
            return file_name, datatypes
        else:
            return None, None # pragma: no cover



    def generate_expected_output(self, questions_text, chat_id):
        """
        Generates the expected output for a query based on the provided questions text and chat ID.

        Retrieves the source ID from the chat document, extracts column data types from the MongoDB cache,
        and generates a SQL `CREATE TABLE` statement. The expected output is formatted to include the SQL
        `CREATE TABLE` statement and the provided query.

        :param questions_text: Questions string to be used in the query
        :type questions_text: str
        :param chat_id: Chat ID used to retrieve metadata from MongoDB
        :type chat_id: str
        :return: Expected output formatted with the SQL statement and query
        :rtype: str
        """
        succ,chat_doc=self.mongo_chats.get_by_id(chat_id)
        cwf=chat_doc.get("cwf",None)
        source_id=cwf.get("source_id", None)
        file_name, datatypes = self.extract_column_datatypes_from_mongodb(source_id, chat_id)
        logger.info(f"Filename and datatypes: {file_name}, {datatypes}")
        if file_name and datatypes:
            create_table_statement = self.generate_create_table_statement(file_name, datatypes)
            # expected_output = f"""{create_table_statement} \n -- Generate only the SQL part for my query based on the above table. \n\n --  My query is: {questions_text} \n\n"""
            # return expected_output

            logger.info(f"Create table Statmenent: {create_table_statement}")
        
            expected_output = f"The name of the table is 'df' and consider this schema: {create_table_statement}" + """
            
            Generate only the sql statement for my table strictly in duckdb dialect.
            Here is some documentation  from duckdb for few functions use this documentaion to create sql queries if you are using any of the function from this.
            Documentation: 
current_date
Description	Current date (at start of current transaction).
Example	current_date
Result	2022-10-08
date_add(date, interval)
Description	Add the interval to the date.
Example	date_add(DATE '1992-09-15', INTERVAL 2 MONTH)
Result	1992-11-15
date_diff(part, startdate, enddate)
Description	The number of partition boundaries between the dates.
Example	date_diff('month', DATE '1992-09-15', DATE '1992-11-14')
Result	2
date_part(part, date)
Description	Get the subfield (equivalent to extract).
Example	date_part('year', DATE '1992-09-20')
Result	1992
date_sub(part, startdate, enddate)
Description	The number of complete partitions between the dates.
Example	date_sub('month', DATE '1992-09-15', DATE '1992-11-14')
Result	1
date_trunc(part, date)
Description	Truncate to specified precision.
Example	date_trunc('month', DATE '1992-03-07')
Result	1992-03-01
datediff(part, startdate, enddate)
Description	Alias of date_diff. The number of partition boundaries between the dates.
Example	datediff('month', DATE '1992-09-15', DATE '1992-11-14')
Result	2
datepart(part, date)
Description	Alias of date_part. Get the subfield (equivalent to extract).
Example	datepart('year', DATE '1992-09-20')
Result	1992
datesub(part, startdate, enddate)
Description	Alias of date_sub. The number of complete partitions between the dates.
Example	datesub('month', DATE '1992-09-15', DATE '1992-11-14')
Result	1
datetrunc(part, date)
Description	Alias of date_trunc. Truncate to specified precision.
Example	datetrunc('month', DATE '1992-03-07')
Result	1992-03-01
dayname(date)
Description	The (English) name of the weekday.
Example	dayname(DATE '1992-09-20')
Result	Sunday
extract(part from date)
Description	Get subfield from a date.
Example	extract('year' FROM DATE '1992-09-20')
Result	1992
greatest(date, date)
Description	The later of two dates.
Example	greatest(DATE '1992-09-20', DATE '1992-03-07')
Result	1992-09-20
isfinite(date)
Description	Returns true if the date is finite, false otherwise.
Example	isfinite(DATE '1992-03-07')
Result	true
isinf(date)
Description	Returns true if the date is infinite, false otherwise.
Example	isinf(DATE '-infinity')
Result	true
last_day(date)
Description	The last day of the corresponding month in the date.
Example	last_day(DATE '1992-09-20')
Result	1992-09-30
least(date, date)
Description	The earlier of two dates.
Example	least(DATE '1992-09-20', DATE '1992-03-07')
Result	1992-03-07
make_date(bigint, bigint, bigint)
Description	The date for the given parts.
Example	make_date(1992, 9, 20)
Result	1992-09-20
monthname(date)
Description	The (English) name of the month.
Example	monthname(DATE '1992-09-20')
Result	September
strftime(date, format)
Description	Converts a date to a string according to the format string.
Example	strftime(date '1992-01-01', '%a, %-d %B %Y')
Result	Wed, 1 January 1992
time_bucket(bucket_width, date[, offset])
Description	Truncate date by the specified interval bucket_width. Buckets are offset by offset interval.
Example	time_bucket(INTERVAL '2 months', DATE '1992-04-20', INTERVAL '1 month')
Result	1992-04-01
time_bucket(bucket_width, date[, origin])
Description	Truncate date by the specified interval bucket_width. Buckets are aligned relative to origin date. origin defaults to 2000-01-03 for buckets that don’t include a month or year interval, and to 2000-01-01 for month and year buckets.
Example	time_bucket(INTERVAL '2 weeks', DATE '1992-04-20', DATE '1992-04-01')
Result	1992-04-15
today()
Description	Current date (start of current transaction).
Example	today()
Result	2022-10-08


Description  GROUPING SETS, ROLLUP and CUBE can be used in the GROUP BY clause to perform a grouping over multiple dimensions within the same query. Note that this syntax is not compatible with GROUP BY ALL.
CUBE and ROLLUP are syntactic sugar to easily produce commonly used grouping sets.
The ROLLUP clause will produce all “sub-groups” of a grouping set, e.g., ROLLUP (country, city, zip) produces the grouping sets (country, city, zip), (country, city), (country), (). This can be useful for producing different levels of detail of a group by clause. This produces n+1 grouping sets where n is the amount of terms in the ROLLUP clause.
CUBE produces grouping sets for all combinations of the inputs, e.g., CUBE (country, city, zip) will produce (country, city, zip), (country, city), (country, zip), (city, zip), (country), (city), (zip), (). This produces 2^n grouping set

Examples Compute the average income along the provided four different dimensions:
        ```SELECT city, street_name, avg(income)
FROM addresses
GROUP BY GROUPING SETS ((city, street_name), (city), (street_name), ()); ```

Example2 Compute the average income along the same dimensions:
    ```SELECT city, street_name, avg(income)
FROM addresses
GROUP BY CUBE (city, street_name);```

Example3 Compute the average income along the dimensions (city, street_name), (city) and ():
```SELECT city, street_name, avg(income)
FROM addresses
GROUP BY ROLLUP (city, street_name); ```
            
The name of my table is df and refer the schema """ + create_table_statement + """. Strictly Generate Only SELECT queries. The generated query should be always wrapped inside sql``` {sql query}``` . my query:"""+ f"{questions_text}" 
            
            return expected_output
        else:
            return None # pragma: no cover

