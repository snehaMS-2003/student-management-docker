import os
import time
import mysql.connector
from mysql.connector import Error

def get_db_config():
    """Retrieve database connection settings from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'student_db'),
        'user': os.getenv('DB_USER', 'student_user'),
        'password': os.getenv('DB_PASSWORD', 'student_password'),
    }

def get_connection(retries=10, retry_interval=2):
    """Establish and return a MySQL connection with retry mechanism."""
    config = get_db_config()

    for attempt in range(1, retries + 1):
        try:
            conn = mysql.connector.connect(
                connection_timeout=3,
                **config
            )
            if conn.is_connected():
                return conn
        except Error as e:
            if attempt == retries:
                raise Exception(f"Failed to connect to MySQL after {retries} attempts: {e}")
            time.sleep(retry_interval)
    return None

def init_db():
    """Ensure table and initial data exist upon application startup."""
    config = get_db_config()
    db_name = config.get('database')

    # Quick single attempt check during init to avoid blocking app startup
    try:
        conn = get_connection(retries=1, retry_interval=1)
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
        cursor.execute(f"USE `{db_name}`;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) NOT NULL UNIQUE,
                phone VARCHAR(20) NOT NULL,
                department VARCHAR(80) NOT NULL,
                gender ENUM('Male', 'Female', 'Other') NOT NULL,
                date_of_birth DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization deferred (will connect on requests): {e}")

