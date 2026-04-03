#!/usr/bin/env python3
import sys
import os
import subprocess
import datetime

BACKUP_DIR = os.path.expanduser("~/Backups")

def check_tool(tool):
    try:
        subprocess.run([tool, "--version"], capture_output=True, check=True)
        return True
    except:
        return False

def run_psql(query, db=None):
    cmd = ["psql"]
    if db:
        cmd.extend(["-d", db])
    cmd.extend(["-c", query])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "PostgreSQL client not found. Install: sudo apt install postgresql-client"

def run_mysql(query, db=None):
    cmd = ["mysql"]
    if db:
        cmd.extend(["-e", f"use {db}; {query}"])
    else:
        cmd.extend(["-e", query])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "MySQL client not found. Install: sudo apt install mysql-client"

def run_mongo(query, db=None):
    cmd = ["mongosh", "--eval", query]
    if db:
        cmd.insert(1, db)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "MongoDB client not found. Install: sudo apt install mongodb-org"

def query_postgres(db, sql):
    return run_psql(sql, db)

def query_mysql(db, sql):
    return run_mysql(sql, db)

def list_tables_postgres(db):
    return run_psql("\\dt", db)

def list_tables_mysql(db):
    return run_mysql("SHOW TABLES;", db)

def describe_table_postgres(db, table):
    return run_psql(f"\\d {table}", db)

def describe_table_mysql(db, table):
    return run_mysql(f"DESCRIBE {table};", db)

def backup_postgres(db, output_path=None):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not output_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(BACKUP_DIR, f"{db}_{timestamp}.sql")
    
    try:
        result = subprocess.run(
            ["pg_dump", "-Fc", db, "-f", output_path],
            capture_output=True, text=True, check=True
        )
        return f"Backup created: {output_path}"
    except FileNotFoundError:
        return "pg_dump not found. Install: sudo apt install postgresql-client"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def backup_mysql(db, output_path=None):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not output_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(BACKUP_DIR, f"{db}_{timestamp}.sql")
    
    try:
        result = subprocess.run(
            ["mysqldump", db, "-r", output_path],
            capture_output=True, text=True, check=True
        )
        return f"Backup created: {output_path}"
    except FileNotFoundError:
        return "mysqldump not found. Install: sudo apt install mysql-client"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def restore_postgres(db, backup_file):
    if not os.path.exists(backup_file):
        return f"Backup file not found: {backup_file}"
    
    try:
        result = subprocess.run(
            ["pg_restore", "-d", db, backup_file],
            capture_output=True, text=True, check=True
        )
        return f"Restored: {db}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "pg_restore not found"

def restore_mysql(db, backup_file):
    if not os.path.exists(backup_file):
        return f"Backup file not found: {backup_file}"
    
    try:
        result = subprocess.run(
            ["mysql", db],
            stdin=open(backup_file),
            capture_output=True, text=True, check=True
        )
        return f"Restored: {db}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "mysql not found"

def create_database_postgres(name):
    return run_psql(f"CREATE DATABASE {name};")

def create_database_mysql(name):
    return run_mysql(f"CREATE DATABASE {name};")

def drop_database_postgres(name):
    return run_psql(f"DROP DATABASE IF EXISTS {name};")

def drop_database_mysql(name):
    return run_mysql(f"DROP DATABASE IF EXISTS {name};")

def sqlite_query(db_path, sql):
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if sql.strip().lower().startswith("select"):
            cursor.execute(sql)
            results = cursor.fetchall()
            if results:
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                output = " | ".join(columns) + "\n" + "-"*50 + "\n"
                output += "\n".join([" | ".join(map(str, row)) for row in results])
                return output
            return "No results"
        else:
            cursor.execute(sql)
            conn.commit()
            return "Query executed successfully"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        return """Usage: database-manager <command> [args]

Commands:
  query <db> <sql>              - Run SQL query
  query-sqlite <file> <sql>    - Query SQLite database
  backup <db> [file]           - Create database backup
  restore <db> <file>          - Restore from backup
  list-tables <db>             - List all tables
  describe <db> <table>        - Show table schema
  create-db <name>             - Create new database
  drop-db <name>               - Delete database

Examples:
  python handler.py query mydb "SELECT * FROM users LIMIT 10"
  python handler.py query-sqlite /path/to/db.sqlite "SELECT * FROM users"
  python handler.py backup mydb
  python handler.py list-tables mydb"""
    
    command = sys.argv[1]
    
    if command == "query":
        if len(sys.argv) < 4:
            return "Usage: query <db> <sql>"
        return query_postgres(sys.argv[2], sys.argv[3])
    
    elif command == "query-sqlite":
        if len(sys.argv) < 4:
            return "Usage: query-sqlite <file> <sql>"
        return sqlite_query(sys.argv[2], sys.argv[3])
    
    elif command == "backup":
        if len(sys.argv) < 3:
            return "Usage: backup <db> [output-file]"
        output = sys.argv[3] if len(sys.argv) > 3 else None
        return backup_postgres(sys.argv[2], output)
    
    elif command == "restore":
        if len(sys.argv) < 4:
            return "Usage: restore <db> <backup-file>"
        return restore_postgres(sys.argv[2], sys.argv[3])
    
    elif command == "list-tables":
        if len(sys.argv) < 3:
            return "Usage: list-tables <db>"
        return list_tables_postgres(sys.argv[2])
    
    elif command == "describe":
        if len(sys.argv) < 4:
            return "Usage: describe <db> <table>"
        return describe_table_postgres(sys.argv[2], sys.argv[3])
    
    elif command == "create-db":
        if len(sys.argv) < 3:
            return "Usage: create-db <name>"
        return create_database_postgres(sys.argv[2])
    
    elif command == "drop-db":
        if len(sys.argv) < 3:
            return "Usage: drop-db <name>"
        return drop_database_postgres(sys.argv[2])
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
