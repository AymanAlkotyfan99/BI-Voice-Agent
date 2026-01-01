class LogSerializer:
    
    @staticmethod
    def serialize(records):
        try:
            # SurrealDB returns nested list
            return records[0]["result"]
        except:
            return []
