import clickhouse_connect
import os
import re


def sanitize_sql_for_http(sql: str) -> str:
    """
    Sanitize SQL for ClickHouse HTTP execution.
    
    Removes incompatible syntax:
    - FORMAT Native (not supported via HTTP)
    - Semicolons (causes multi-statement errors)
    - Extra whitespace
    
    Args:
        sql: Raw SQL string
    
    Returns:
        Clean SQL safe for HTTP execution
    """
    if not sql:
        return ""
    
    # Remove FORMAT Native (case-insensitive)
    clean_sql = re.sub(r'\s+FORMAT\s+Native\s*', ' ', sql, flags=re.IGNORECASE)
    
    # Remove all semicolons
    clean_sql = clean_sql.replace(';', '')
    
    # Remove extra whitespace and trim
    clean_sql = ' '.join(clean_sql.split())
    clean_sql = clean_sql.strip()
    
    return clean_sql


def get_query_clickhouse_client():
    """Get ClickHouse client for query execution using HTTP protocol."""
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_HTTP_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_QUERY_USER", os.getenv("CLICKHOUSE_USER", "etl_user")),
        password=os.getenv("CLICKHOUSE_QUERY_PASSWORD", os.getenv("CLICKHOUSE_PASSWORD", "etl_pass123")),
        database=os.getenv("CLICKHOUSE_DATABASE", "etl")
    )

def get_schema() -> dict:
    client = get_query_clickhouse_client()
    
    # Query to fetch schema
    schema_query = """
        SELECT database, table, name, type
        FROM system.columns
        WHERE database = 'etl'
        ORDER BY database, table;
    """
    
    # Sanitize before execution
    clean_query = sanitize_sql_for_http(schema_query)
    result = client.query(clean_query)
    rows = result.result_rows

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
