import pymysql
import pandas as pd

# MySQL Database Configuration
DB_USER = "atanalytics"  # Replace with your MySQL username
DB_PASSWORD = "gcp1!2@3#"  # Replace with your MySQL password
DB_NAME = "task"
DB_HOST = "127.0.0.1"  # Localhost when using Cloud SQL Proxy

# Establish MySQL connection
connection = pymysql.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_NAME
)

try:
    # Query to select all data from the table
    query = "SELECT * FROM task"

    # Read the data into a pandas DataFrame
    df = pd.read_sql(query, connection)

    # Write the DataFrame to a CSV file
    df.to_csv("task_data.csv", index=False)
    print("Data successfully exported to task_data.csv")

except Exception as e:
    print(f"Error: {e}")

finally:
    if connection:
        connection.close()
