import mysql.connector
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Database connection configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'amasift_compare')
}

def test_connection():
    """Test database connection and simple query."""
    try:
        print("Connecting to database...")
        start_time = time.time()
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        print(f"Connection established in {time.time() - start_time:.2f} seconds")
        
        print("Executing simple query...")
        query_start = time.time()
        
        cursor.execute("SELECT COUNT(*) as count FROM products")
        result = cursor.fetchone()
        
        print(f"Query executed in {time.time() - query_start:.2f} seconds")
        print(f"Total products in database: {result['count']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()