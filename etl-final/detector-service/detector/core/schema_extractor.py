import pymysql
import psycopg2


class SchemaExtractor:

    def extract_mysql(self, cfg):
        connection = pymysql.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=int(cfg["port"])
        )

        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        schema = {}

        for (table,) in tables:
            cursor.execute(f"DESCRIBE {table}")
            fields = cursor.fetchall()
            schema[table] = [f[0] for f in fields]

        return schema

    def extract_postgres(self, cfg):
        connection = psycopg2.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            dbname=cfg["database"],
            port=int(cfg["port"])
        )

        cursor = connection.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)

        tables = cursor.fetchall()
        schema = {}

        for (table,) in tables:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='{table}';
            """)
            fields = cursor.fetchall()
            schema[table] = [f[0] for f in fields]

        return schema
