def flatten_row(row: dict):
    """
    Ensures ClickHouse receives clean flattened object.
    """
    return {k: v for k, v in row.items()}
