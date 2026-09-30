import os

import pyodbc
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """
    Creates and returns a connection to the AZURE SQL Managed Instance
    """
    try:
        # Connection string
        conn_str = (
            f"DRIVER={os.getenv('DB_DRIVER', '{ODBC Driver 18 for SQL Server}')};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Error Connecting to Database: {e} ")
        return None


def execute_sql_file(connection, file_path):
    """
    Reads a .sql file and executes the contents block by block.
    """
    print(f"Executing {file_path}...")

    try:
        with open(file_path, "r") as file:
            sql_script = file.read()

        cursor = connection.cursor()

        # MSSQL scripts can contain 'GO' commands.
        # We split by 'GO' to execute each logical block separately.
        for statement in sql_script.split("GO"):
            clean_statment = statement.strip()
            if clean_statment:
                cursor.execute(clean_statment)

        connection.commit()
        print(f"Successfully executed {file_path}")

    except Exception as e:
        print(f"Errir executing {file_path}: {e}")
        connection.rollback()


def main():
    # Establish Connection
    conn = get_db_connection()
    if not conn:
        print("Could not Establish DB Connection, Please check the DB configuration")
        return

    try:
        # 2 Path to SQL files - Schema must be created before Indexes
        scripts = ["database/schema.sql", "database/index.sql"]

        for script in scripts:
            execute_sql_file(conn, script)

        print("\n Database setup Completed Successfully! Your Environment is ready")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
