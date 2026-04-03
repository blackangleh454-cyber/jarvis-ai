# Database Manager

**Description:** Manage PostgreSQL, MySQL, MongoDB databases - migrations, backups, queries, and schema operations.

**Commands:**
- `query <db> <sql>` - Run SQL query
- `backup <db>` - Create database backup
- `restore <db> <file>` - Restore from backup
- `list-tables <db>` - List all tables
- `describe <db> <table>` - Show table schema
- `migrate <db> <migration>` - Run migration
- `create-db <name>` - Create new database
- `drop-db <name>` - Delete database

**Supported:**
- PostgreSQL
- MySQL/MariaDB
- MongoDB
- SQLite

**Usage:**
```bash
python handler.py query mydb "SELECT * FROM users LIMIT 10"
python handler.py backup mydb
python handler.py restore mydb backup.sql
python handler.py list-tables mydb
python handler.py describe mydb users
```
