def schema_record(schema: dict):
    return {
        "tables": list(schema.keys()),
        "fields": schema
    }
