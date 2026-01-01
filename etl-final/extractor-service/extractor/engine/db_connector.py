import pymysql
import psycopg2


class DBConnector:

    def connect_mysql(self, cfg):
        return pymysql.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=int(cfg["port"]),
            cursorclass=pymysql.cursors.DictCursor
        )

    def connect_postgres(self, cfg):
        return psycopg2.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            dbname=cfg["database"],
            port=int(cfg["port"])
        )

    def connect(self, cfg):
        db_type = cfg["db_type"]
        if db_type == "mysql":
            return self.connect_mysql(cfg)
        elif db_type == "postgres":
            return self.connect_postgres(cfg)
        else:
            raise Exception("Unsupported database type")
