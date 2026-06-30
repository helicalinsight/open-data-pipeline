import pandas as pd
import os


def setup_feather():
    data1 = {
        'id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'age': [25, 30, 35, 40],
        'join_date': [pd.to_datetime('2022-01-01'), pd.to_datetime('2022-02-15'), pd.to_datetime('2022-03-20'), pd.to_datetime('2022-04-10')]
    }

    # Sample data for DataFrame 2
    data2 = {
        'id': [3, 4, 5, 6],
        'name': ['Charlie', 'David', 'Eve', 'Frank'],
        'age': [35, 40, 45, 50],
        'join_date': [pd.to_datetime('2022-03-20'), pd.to_datetime('2022-04-10'), pd.to_datetime('2022-05-05'), pd.to_datetime('2022-06-20')]
    }
    data3 = {
        'bool_column': ["true", "false", "1", "False"],
        'int_column': [12, 34, 45, 56]
    }

    # Create DataFrame 1
    df1 = pd.DataFrame(data1)

    # Create DataFrame 2
    df2 = pd.DataFrame(data2)
    df3 = pd.DataFrame(data3)

    absolute_path = os.path.abspath(os.path.join(__file__, "../.."))
    feather_file_path = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", ".cache",
                                    "65cb43f2007a5f38718b9d6f",
                                    "be687a30-1329-4639-a606-16f083afa6e6.feather")
    feather_file_path_2 = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", ".cache",
                                 "65cb43f2007a5f38718b9d6f",
                                 "be687a30-1329-4639-a606-16f083afa6e5.feather")
    feather_file_path_3 = os.path.join(absolute_path, "hadoop_local", "65365001d9654d9ec1172f87", ".cache",
                                 "65cb43f2007a5f38718b9d6f",
                                 "be687a30-1329-4639-a606-16f083afa6e0.feather")
    df1.to_feather(feather_file_path)
    df2.to_feather(feather_file_path_2)
    df3.to_feather(feather_file_path_3)

def setup_files():
    data1 = {
        'id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'age': [25, 30, 35, 40],
        'join_date': [pd.to_datetime('2022-01-01'), pd.to_datetime('2022-02-15'), pd.to_datetime('2022-03-20'),
                      pd.to_datetime('2022-04-10')]
    }

    # Sample data for DataFrame 2
    data2 = {
        'id': [3, 4, 5, 6],
        'name': ['Charlie', 'David', 'Eve', 'Frank'],
        'age': [35, 40, 45, 50],
        'join_date': [pd.to_datetime('2022-03-20'), pd.to_datetime('2022-04-10'), pd.to_datetime('2022-05-05'),
                      pd.to_datetime('2022-06-20')]
    }

    # Sample data for DataFrame 3
    data3 = {
        'id': [1, 2, 5, 6],
        'name': ['Smith', 'Tom', 'Pam', 'Edward'],
        'age': [25, 27, 35, 40],
        'join_date': [pd.to_datetime('2022-05-20'), pd.to_datetime('2022-08-10'), pd.to_datetime('2022-09-05'),
                      pd.to_datetime('2022-07-20')]
    }

    data4 = {
        'public_id': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112],
        'firstname': ['manish', 'harish', 'karan', 'vicky', 'utkarsh', 'nitin', 'nikhilesh', 'aman', 'ganesh',
                      'sibtain', 'pooja', 'mahendran'],
        'lastname': ['kumar', 'raj', 'raj', 'soni', 'soni', 'sahu', 'kumar', 'gupta', 'danuri', 'jammu', 'singh',
                     'pandey'],
        'age': [16, 19, 18, 16, 19, 24, 25, 12, 42, 50, 12, 28],
        'dob': ['2000/12/22', '1998/12/22', '2001/12/21', '2000/10/22', '2000/10/12', '1997/12/22', '1996/12/22',
                '1995/12/22', '1994/12/22', '2000/10/22', '2000/10/12', '1997/12/22'],
        'zipcode': [462023, 377041, 377031, 234237, 235730, 377031, 128014, 377041, 257960, 377011, 377041, 377031],
        'address': ['4 th street mexico', '1234 west main street', '23 east main street', '4 th street mexico',
                    '1234 west main street', '23 east main street', '4 th street mexico', '1234 west main street',
                    '23 east main street', '4 th street mexico', '1234 west main street', '23 east main street']
    }

    data5 = {
        'name': ["Science", "Science", "English", "English"],
        'marks': [95, 72, 80, 67]
    }

    # Create DataFrame 1
    df1 = pd.DataFrame(data1)

    # Create DataFrame 2
    df2 = pd.DataFrame(data2)

    # Create DataFrame 3
    df3 = pd.DataFrame(data3)

    # Create DataFrame 3
    df4 = pd.DataFrame(data4)

    # Create an empty DataFrame
    empty_df = pd.DataFrame()

    df5 = pd.DataFrame(data5)

    absolute_path = os.path.abspath(os.path.join(__file__, "../.."))
    csv_file_path = os.path.join(absolute_path, "test_files", "data1.csv")
    csv_file_path_2 = os.path.join(absolute_path, "test_files", "data2.csv")
    csv_file_path_3 = os.path.join(absolute_path, "test_files", "data3.csv")
    csv_file_path_4 = os.path.join(absolute_path, "test_files", "dept.csv")
    empty_path = os.path.join(absolute_path, "test_files", "empty_file.csv")
    file1 = os.path.join(absolute_path, "test_files", "file1.csv")
    file2 = os.path.join(absolute_path, "test_files", "file2.csv")
    file3 = os.path.join(absolute_path, "test_files", "file3.csv")
    file4 = os.path.join(absolute_path, "test_files", "file4.csv")

    paths = [csv_file_path, csv_file_path_2, csv_file_path_3,
             csv_file_path_4,
             empty_path, file1, file2, file3, file4]
    for path in paths:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

    df1.to_csv(csv_file_path, index=False)
    df2.to_csv(csv_file_path_2, index=False)
    df3.to_csv(csv_file_path_3, index=False)
    df4.to_csv(csv_file_path_4, index=False)
    empty_df.to_csv(empty_path, index=False)
    df1.to_csv(file1, index=False)
    df2.to_csv(file2, index=False)
    df3.to_csv(file3, index=False)
    df5.to_csv(file4, index=False)

    """
    cannot write xls file:
    FutureWarning: As the xlwt package is no longer maintained, the xlwt engine will be removed in a future
   version of pandas. This is the only engine in pandas that supports writing in the xls format. Install openpyxl and write to an xlsx file instead. You can
   set the option io.excel.xls.writer to 'xlwt' to silence this warning. While this option is deprecated and will also raise a warning, it can be globally s
   et and the warning suppressed.

    """



