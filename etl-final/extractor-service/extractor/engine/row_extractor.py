class RowExtractor:
    
    def extract_rows(self, connection, tables: list):
        cursor = connection.cursor()

        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            for row in rows:
                yield table, row
