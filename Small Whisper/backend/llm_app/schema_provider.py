from clickhouse_driver import Client

client = Client(
    host="localhost",
    port=9000,
    user="etl_user",
    password="etl_pass123",
)

def get_schema() -> dict:
    rows = client.execute("""
        SELECT database, table, name, type
        FROM system.columns
        WHERE database = 'etl'
        ORDER BY database, table;
    """)

    schema = {}

    for db, table, column, col_type in rows:
        full_table = f"{db}.{table}"
        schema.setdefault(full_table, []).append({
            "name": column,
            "type": col_type
        })

    print("\n--- CLICKHOUSE SCHEMA WITH TYPES LOADED ---")
    for table, columns in schema.items():
        print(f"\n{table}")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")

    return schema



def is_question_matching_schema(question: str, schema: dict) -> bool:
    question = question.lower()
    tokens = set()

    for table, columns in schema.items():
        tokens.add(table.split(".")[-1].lower())

        for col in columns:
            col_name = col["name"].lower()
            tokens.add(col_name)
            tokens.add(col_name.replace("_", " "))

    return any(token in question for token in tokens)
