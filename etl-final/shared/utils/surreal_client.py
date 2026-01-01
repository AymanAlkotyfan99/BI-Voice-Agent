import os
import json
import requests

class SurrealClient:

    def __init__(self):
        self.url = os.getenv("SURREAL_URL", "http://surrealdb:8000/sql")
        self.user = os.getenv("SURREAL_USER", "root")
        self.password = os.getenv("SURREAL_PASS", "root")
        self.ns = os.getenv("SURREAL_NS", "bi_etl")
        self.db = os.getenv("SURREAL_DB", "etl_logs")

    def query(self, sql: str):
        # Prepend USE statements to set namespace and database context
        full_sql = f"USE NS {self.ns}; USE DB {self.db}; {sql}"
        
        try:
            response = requests.post(
                self.url,
                auth=(self.user, self.password),
                headers={"Content-Type": "text/plain", "Accept": "application/json"},
                data=full_sql,
                timeout=10
            )
            return response.json()
        except Exception as e:
            print("[SurrealDB ERROR]", e)
            return None

    def insert(self, table: str, record: dict):
        sql = f"CREATE {table} CONTENT {json.dumps(record)};"
        return self.query(sql)
