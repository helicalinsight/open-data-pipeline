

# planner=""""Your task is to break down the given queries into separate steps. Each query is a description of operations to perform on a dataset.Your task involves data engineering operations, where you'll receive queries describing tasks to be performed on a dataset. To break down these tasks accurately, analyze each task carefully. Your output should be a list containing these steps. Here are some examples for reference:

#                     1. Task: 'Rename the salary column to monthly_salary, drop all columns except monthly_salary, employee_id, and department, and trim the department by 2 characters from the right.'
#                     Expected Output: ```['Rename the salary column to monthly_salary', 'Drop all columns except monthly_salary, employee_id, and department', 'Trim the department by 2 characters from right']```

#                     2. Task: 'add column employee_id and give sum on employee_payment column and finally abort operation.'
#                     Expected Output: ```['add column employee_id', 'give sum on employee_payment column', 'abort operation']```

#                     3. Task: 'calculate mean of client_salary and concate columns client_id and phone_number, and convert date format of column purchase_date to MM/DD/YYYY.'
#                     Expected Output: ```['calculate mean of client_salary', 'concate columns client_id and phone_number', 'onvert date format of column purchase_date to MM/DD/YYYY']```

#                     4. Task: 'Remove duplicates entries from product_name column and drop all columns except product_name and category, and export data to abc.csv file.'
#                     Expected Output: ```['Remove duplicates entries from product_name column', 'Drop all columns except product_name and category', 'export data to abc.csv file']```

#                     5. Task: 'Filter the records where price > 100 and join students and enrollments using id and stud_id by left join and finally rename column price to total_price.'
#                     Expected Output: ```['Filter the records where price > 100', 'join students and enrollments using id and stud_id by left join', 'rename column price to total_price']```

#                     6. Task: 'Join the orders with the customers by matching customer_ID using an inner join and replace * in column price by - and select file data.csv.'
#                     Expected Output: ```['Join the orders with the customers by matching customer_ID using an inner join', 'replace * in column price by -', 'select file data.csv']```

#                     7. Task: 'Sort first_name column records in ascending order and split full_name column into first_name and last_name using _ and typecast salary column from decimal to int'
#                     Expected Output: ```['Sort first_name column records in ascending order', 'split full_name column into first_name and last_name using _', 'typecast salary column from decimal to int datatype']```

#                     8. Task: 'Union syllabus.csv with tutorial.csv and modify the address column data to uppercase letter and if student score greater than 60 then firstclass otherwise second class.'
#                     Expected Output: ```['Union syllabus.csv with tutorial.csv', 'modify the address column data to uppercase letter', 'if student score greater than 60 then firstclass otherwise second class']```


#                     9. Task: 'Concatenate employee_first_name and employee_last_name columns into full_name, then calculate the average from salary column, and finally, filter out records where the average salary is below $5000.'
#                     Expected Output: ```['Concatenate employee_first_name and employee_last_name columns into full_name', 'calculate the average from salary column', 'filter out records where the average salary is below $5000']```

#                     Task: 'If salary is less than 10000 then low_salary otherwise high_salary and add columns fees and total_fees and finally stop operation.'
#                     Expected Output: ```['If salary is less than 10000 then low_salary otherwise high_salary', 'add columns fees and total_fees', 'finally stop operation']```


#                     10. Task: 'Add a new column named hire_date with the default value '2022-01-01' then change the format of the date_of_birth column to YYYY-MM-DD, and remove the age column.'
#                     Expected Output: ```['Add a new column named hire_date with the default value '2022-01-01'', 'Change the format of the date_of_birth column to YYYY-MM-DD', 'Remove the age column']```


#                     11. Task: 'Give max from student_fees column then add student_address and student_phone columns and finally calculate min from student_payment column.'
#                     Expected Output: ```['Give max from student_fees column', 'add student_address and student_phone columns', 'alculate min from student_payment column']```

#                     12. Task: 'find the sum of staff_salary then calculate count of student_id and in the end terminate operation.'
#                     Expected Output: ```['find the sum of staff_salary', 'calculate count of student_id', 'terminate operation']```

#                     13. Task: 'Give distinct value from student_status column then also find distinct count from payment column and at last calculate variance of column total_salary.'
#                     Expected Output: ```['Give distinct value from student_status column', 'find distinct count from payment column', 'calculate variance of column total_salary']```

#                     14. Task: 'calculate standard deviation of column percentage then concate classYear and award_topics columns and then eventually merge first_name and last_name columns by placing _ between them.'
#                     Expected Output: ```['calculate standard deviation of column percentage', 'concate classYear and award_topics columns', 'merge first_name and last_name columns by placing _ between them']```

#                     15. Task: 'Change date format of start_year and end_year columns to MMDDYYYY and then apply DD/MM/YYYY date format to award_date and at last stop current job execution.'
#                     Expected Output: ```['Change date format of start_year and end_year columns to MMDDYYYY', 'apply DD/MM/YYYY date format to award_date', 'stop current job execution']```

#                     16. Task: 'Remove duplicate values from PhoneNumber and topic_id columns and drop all columns and in the end remove all columns except staff_id.'
#                     Expected Output: ```['Remove duplicate values from PhoneNumber and topic_id columns', 'drop all columns', 'remove all columns except staff_id']```


#                     17. Task: 'export all data into student file then Apply a filter on the age column to display only the rows where the age is greater than 30 and finally Merge schools to students using id and stud_id with an full join.'
#                     Expected Output: ```['export all data into student file', 'Apply a filter on the age column to display only the rows where the age is greater than 30', 'Merge schools to students using id and stud_id with an full join']```


#                     18. Task: 'Merge staff to students using id and stud_id with an inner join and Filter price column to show data where price is less than 5000 then Combine schools with an left join to students using id and stud_id.'
#                     Expected Output: ```['Merge staff to students using id and stud_id with an inner join', 'Filter price column to show data where price is less than 5000', 'Combine schools with an left join to students using id and stud_id']```


#                     19. Task: 'Through an right join, concate teachers to class by columns teacher_id and class_id and Select data where status is equals to active then replace * by ^ in the column price.'
#                     Expected Output: ```['Through an right join, concate teachers to class by columns teacher_id and class_id', 'Select data where status is equals to active', 'replace * by ^ in the price column']```



#                     20. Task: 'Replace _ in the school_info column by - and Extract records where the email ends with '@gmail.com' and at the end choose college.csv file.'
#                     Expected Output: ```['Replace _ in the school_info column by -', 'Extract records where the email ends with '@gmail.com' ', 'choose college.csv file']```


#                     21. Task: 'join library and students using stud_id then Display the rows where the first_name starts with 'John' and at the end select teachers.xlsx file.'
#                     Expected Output: ```['join library and students using stud_id', 'Display the rows where the first_name starts with 'John'', 'select teachers.xlsx file']```


#                     22. Task: 'Sort percentage column records in descending order and then Show the rows where the description contains the word 'urgent' and finally Arrange data of temperature column into low to high'.'
#                     Expected Output: ```['Sort percentage column records in descending order', 'Show the rows where the description contains the word 'urgent'', 'Arrange data of temperature column into low to high']```


#                     23. Task: 'Split firstname_lastname column using _ into firstname and lastname and Display records where the address is like '123 Main then eventually change data type of roll_no column into integer.'
#                     Expected Output: ```['Split firstname_lastname column using _ into firstname and lastname', 'Display records where the address is like '123 Main', 'change data type of roll_no column into integer']```

#                     24. Task: 'Alter the data type of address column into string and filter the records where the admission_date is between '2023-01-01' and '2023-12-31' then at the last combine students.csv and schools.csv using stud_id.'
#                     Expected Output: ```['Alter the data type of address column into string', 'filter the records where the admission_date is between '2023-01-01' and '2023-12-31', 'combine students.csv and schools.csv using stud_id']```


#                     25. Task: 'Union college.csv and teacher files using teacher_id and college_id and Select values where the temperature is less than or equal to 25 degrees Celsius then change bank_name column data into lower case letter.'
#                     Expected Output: ```['Union college.csv and teacher files using teacher_id and college_id', 'Select values where the temperature is less than or equal to 25 degrees Celsius', 'change bank_name column data into lower case letter']```


#                     26. Task: 'If age is less than 18 then minor otherwise adult and Extract data where the score is greater than or equal to 85 then finally add students and teachers files using teacher_id and student_id columns.'
#                     Expected Output: ```['If age is less than 18 then minor otherwise adult', 'Extract data where the score is greater than or equal to 85', 'add students and teachers files using teacher_id and student_id columns']```


#     Please proceed to break down the given query into these distinct steps. 
#     Your output should only include the resultant task lists inside ``` ````.
#     Following is the Task: """


planner="""You know about sql, excel and data engineering. Given a paragraph describing a data engineering task, your goal is to divide the task into smaller, manageable subtasks based on the context of the operations involved. Ensure that each subtask has a clear and distinct objective that contributes to the overall task. If the paragraph contains multiple distinct contexts, separate them into different tasks.


Here are Few Examples for you to understand how the things should work. These are just examples do not use them as tasks:



1. Input:
"Merge customer.csv and transactions.csv based on customer_id, then filter records where the transaction_amount is greater than 1000, and finally, calculate the total revenue for each customer."

Expected Output:
['Merge customer.csv and transactions.csv based on customer_id', 'Filter records where the transaction_amount is greater than 1000', 'Calculate the total revenue for each customer']

2. Input:
'Remove duplicate values from PhoneNumber and topic_id columns and drop all columns and in the end remove all columns except staff_id.'
Expected Output:
['Remove duplicate values from PhoneNumber and topic_id columns', 'drop all columns', 'remove all columns except staff_id']


3. Input: 
'export all data into student file then Apply a filter on the age column to display only the rows where the age is greater than 30 and finally Merge schools to students using id and stud_id with an full join.'
Expected Output: 
['export all data into student file', 'Apply a filter on the age column to display only the rows where the age is greater than 30', 'Merge schools to students using id and stud_id with an full join']


4. Input: 
'Merge staff to students using id and stud_id with an inner join and Filter price column to show data where price is less than 5000 then Combine schools with an left join to students using id and stud_id.'
Expected Output: 
['Merge staff to students using id and stud_id with an inner join', 'Filter price column to show data where price is less than 5000', 'Combine schools with an left join to students using id and stud_id']


5. Input: 
'Through an right join, concate teachers to class by columns teacher_id and class_id and Select data where status is equals to active then replace * by ^ in the column price.'
Expected Output: 
['Through an right join, concate teachers to class by columns teacher_id and class_id', 'Select data where status is equals to active', 'replace * by ^ in the price column']



6. Input: 
'Replace _ in the school_info column by - and Extract records where the email ends with '@gmail.com' and at the end choose college.csv file.'
Expected Output: 
['Replace _ in the school_info column by -', 'Extract records where the email ends with '@gmail.com' ', 'choose college.csv file']


7. Input: 
'join library and students using stud_id then Display the rows where the first_name starts with 'John' and at the end select teachers.xlsx file.'
Expected Output: 
['join library and students using stud_id', 'Display the rows where the first_name starts with 'John'', 'select teachers.xlsx file']


8. Input: 
'Sort percentage column records in descending order and then Show the rows where the description contains the word 'urgent' and finally Arrange data of temperature column into low to high'.'
Expected Output: 
['Sort percentage column records in descending order', 'Show the rows where the description contains the word 'urgent'', 'Arrange data of temperature column into low to high']


9. Input: 
'Split firstname_lastname column using _ into firstname and lastname and Display records where the address is like '123 Main then eventually change data type of roll_no column into integer.'
Expected Output: 
['Split firstname_lastname column using _ into firstname and lastname', 'Display records where the address is like '123 Main', 'change data type of roll_no column into integer']

10. Input: 
'Alter the data type of address column into string and filter the records where the admission_date is between '2023-01-01' and '2023-12-31' then at the last combine students.csv and schools.csv using stud_id.'
Expected Output: 
['Alter the data type of address column into string', 'filter the records where the admission_date is between '2023-01-01' and '2023-12-31', 'combine students.csv and schools.csv using stud_id']


11. Input: 
'Union college.csv and teacher files using teacher_id and college_id and Select values where the temperature is less than or equal to 25 degrees Celsius then change bank_name column data into lower case letter.'
Expected Output: 
['Union college.csv and teacher files using teacher_id and college_id', 'Select values where the temperature is less than or equal to 25 degrees Celsius', 'change bank_name column data into lower case letter']


12. Input: 
'If age is less than 18 then minor otherwise adult and Extract data where the score is greater than or equal to 85 then finally add students and teachers files using teacher_id and student_id columns.'
Expected Output: 
['If age is less than 18 then minor otherwise adult', 'Extract data where the score is greater than or equal to 85', 'add students and teachers files using teacher_id and student_id columns']


13. Input:
"Merge customer and transactions"

Expected Output:
['Merge customer and transactions']


Examples End. Note: Above examples should not be used to modify the given task. You should strictly follow the rule and do not modify any given task.

Note: When dividing tasks, maintain continuity and coherence within each subtask. If the context remains consistent throughout the paragraph, avoid introducing new subtasks unnecessarily.
    The output should always be in the form of list inside [] square brackets. Your output should only include the resultant task lists inside ``` ````.
    You should strictly follow, never change or add anything in the given user task.You will just take the task and divide it into subtasks do not modify the input and do not use given examples to modify anything. Following is the Task: """