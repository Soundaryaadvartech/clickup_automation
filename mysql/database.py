import pymysql
import urllib.parse
import logging
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Define the database connection parameters
DB_CONFIG = {
    'user':urllib.parse.quote_plus(os.getenv("DB_USER")),
    'password': urllib.parse.quote_plus(os.getenv("DB_PASSWORD")),
    'host': os.getenv("DB_HOST"),  # This will be the address of the Cloud SQL Proxy
    'database': os.getenv("DB_NAME"),
    'port': int(os.getenv("DB_PORT"))
}

# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='logs/dbconnection.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s',
)

# Global counter for database connections
connection_counter = 0

def get_db_connection(retries=10, delay=5):
    global connection_counter
    for attempt in range(retries):
        try:
            connection = pymysql.connect(
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                host=DB_CONFIG['host'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port'],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            connection_counter += 1
            print(f"Connected to MySQL. Total connections made: {connection_counter}")
            return connection
        except pymysql.MySQLError as e:
            logging.error(f"Error connecting to MySQL: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise
    return None

def add_tasks_bulk(tasks):
    connection = get_db_connection()
    if connection is None:
        return
    try:
        cursor = connection.cursor()
        query = "INSERT INTO task (task_id, link_id, status, list_id, tags, task_name) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.executemany(query, tasks)
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Added {len(tasks)} tasks successfully.")
    except pymysql.MySQLError as e:
        logging.error(f"Error executing add_tasks_bulk: {e}")
        if connection:
            connection.close()
        raise

def update_tasks_bulk(tasks, columns):
    connection = get_db_connection()
    if connection is None:
        return
    try:
        cursor = connection.cursor()
        
        # Dynamically build the SET clause of the query
        set_clause = ", ".join([f"{column} = %s" for column in columns])
        query = f"UPDATE task SET {set_clause} WHERE task_id = %s"
        
        # Prepare the data for executemany
        data = []
        for task in tasks:
            task_data = [task[column] for column in columns]
            task_data.append(task['task_id'])
            data.append(tuple(task_data))
        
        cursor.executemany(query, data)
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Updated {len(tasks)} tasks successfully.")
    except pymysql.MySQLError as e:
        logging.error(f"Error executing update_tasks_bulk: {e}")
        if connection:
            connection.close()
        raise

def delete_tasks_bulk(task_ids):
    connection = get_db_connection()
    if connection is None:
        return
    try:
        cursor = connection.cursor()
        query = "DELETE FROM task WHERE task_id IN (%s)" % ','.join(['%s'] * len(task_ids))
        cursor.execute(query, tuple(task_ids))
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Deleted tasks with task_ids {task_ids} successfully.")
    except pymysql.MySQLError as e:
        logging.error(f"Error executing delete_tasks_bulk: {e}")
        if connection:
            connection.close()
        raise

def get_tasks_by_conditions(task_ids=None, list_ids=None, link_ids=None, statuses=None):
    connection = get_db_connection()
    if connection is None:
        return []
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM task WHERE 1=1"
        params = []
        
        if task_ids:
            query += " AND task_id IN (%s)" % ','.join(['%s'] * len(task_ids))
            params.extend(task_ids)
        if list_ids:
            query += " AND list_id IN (%s)" % ','.join(['%s'] * len(list_ids))
            params.extend(list_ids)
        if link_ids:
            query += " AND link_id IN (%s)" % ','.join(['%s'] * len(link_ids))
            params.extend(link_ids)
        if statuses:
            if isinstance(statuses, str):
                statuses = [statuses]
            query += " AND status IN (%s)" % ','.join(['%s'] * len(statuses))
            params.extend(statuses)
        
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        if results:
            print(f"Tasks found: {results}")
        else:
            print(f"No tasks found with the given conditions.")
        return results
    except pymysql.MySQLError as e:
        logging.error(f"Error executing get_tasks_by_conditions: {e}")
        if connection:
            connection.close()
        raise