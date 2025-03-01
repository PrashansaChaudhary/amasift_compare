"""
Database utility functions.
"""
import mysql.connector
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Database connection configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'amasift_compare')
}

def get_db_connection():
    """
    Establish a connection to the MySQL database.
    
    Returns:
        connection: MySQL database connection object or None if connection fails
    """
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to MySQL: {err}")
        return None

def execute_query(query, params=None, fetch=True, many=False):
    """
    Execute a database query with error handling.
    
    Args:
        query (str): SQL query to execute
        params (tuple or list): Parameters for the query
        fetch (bool): Whether to fetch results (True) or just execute (False)
        many (bool): Whether to execute many statements (True) or a single one (False)
    
    Returns:
        list or None: Query results if fetch=True, None otherwise
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=True)
        
        if many:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return None
            
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()