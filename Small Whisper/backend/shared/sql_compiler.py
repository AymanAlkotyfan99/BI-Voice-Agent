def compile_sql(intent: dict, type_casting: list = None) -> str:
    """
    Compile intent into SQL with optional type casting.
    
    SYSTEMIC GUARANTEES:
    - SELECT always has valid columns (no trailing commas)
    - WHERE only added if filters contain valid conditions
    - GROUP BY only added if dimensions exist
    - ORDER BY only added if valid columns exist
    - LIMIT only added if positive integer
    - Final SQL is syntactically valid
    
    Args:
        intent: Structured intent with metrics, dimensions, filters, etc.
        type_casting: Optional list of type casting requirements from validation
    
    Returns:
        Valid SQL query string
        
    Raises:
        ValueError: If intent is invalid or SQL cannot be generated
    """
    # Validate required fields
    table = intent.get("table")
    if not table or not isinstance(table, str) or not table.strip():
        raise ValueError("Intent must contain a valid table name")
    
    metrics = intent.get("metrics", [])
    if not metrics or not isinstance(metrics, list) or len(metrics) == 0:
        raise ValueError("Intent must contain at least one metric")
    
    dimensions = intent.get("dimensions", []) or []
    filters = intent.get("filters", []) or []
    order_by = intent.get("order_by", []) or []
    limit = intent.get("limit")

    # Build type casting map
    cast_map = {}
    if type_casting:
        for tc in type_casting:
            col = tc.get("column")
            cast_func = tc.get("required_cast")
            if col and cast_func:
                cast_map[col] = cast_func

    select_parts = []
    group_by_parts = []

    # ---------------- Dimensions ----------------
    # Only add non-empty, valid dimension names
    for dim in dimensions:
        if dim and isinstance(dim, str) and dim.strip():
            dim_clean = dim.strip()
            select_parts.append(dim_clean)
            group_by_parts.append(dim_clean)

    # ---------------- Metrics ----------------
    metric_alias_map = {}
    for m in metrics:
        if not isinstance(m, dict):
            continue
            
        col = m.get("column")
        agg = m.get("aggregation")
        
        # Validate metric has required fields
        if not col or not agg:
            continue
        
        # Validate aggregation is valid
        if agg.upper() not in ["SUM", "AVG", "MIN", "MAX", "COUNT"]:
            continue
        
        alias = m.get("alias")
        if not alias or not isinstance(alias, str) or not alias.strip():
            alias = f"{agg.lower()}_{col}"
        
        metric_alias_map[col] = alias
        
        # Handle COUNT(*) specially
        if col == "*":
            select_parts.append(f"{agg.upper()}(*) AS {alias}")
        else:
            # Apply type casting if needed
            col_expr = col
            if col in cast_map:
                cast_func = cast_map[col]
                col_expr = f"{cast_func}({col})"
                print(f"🔧 Type casting applied: {col} → {col_expr}")
            
            select_parts.append(f"{agg.upper()}({col_expr}) AS {alias}")

    # Validate SELECT has at least one column
    if not select_parts:
        raise ValueError("SQL generation failed: No valid SELECT columns generated")

    # Build base SQL
    sql = f"SELECT {', '.join(select_parts)} FROM {table}"

    # ---------------- Filters ----------------
    # Only add WHERE if we have valid filter conditions
    where_clauses = []
    for f in filters:
        if not isinstance(f, dict):
            continue
        
        col = f.get("column")
        op = f.get("operator")
        val = f.get("value")
        
        # Validate filter has all required fields
        if not col or not isinstance(col, str) or not col.strip():
            continue
        if not op or not isinstance(op, str) or not op.strip():
            continue
        if val is None:
            continue
        
        # Format value based on type
        if isinstance(val, str):
            # Escape single quotes in string values
            val_escaped = val.replace("'", "''")
            val_formatted = f"'{val_escaped}'"
        elif isinstance(val, (int, float)):
            val_formatted = str(val)
        else:
            # Skip invalid value types
            continue
        
        where_clauses.append(f"{col.strip()} {op.strip().upper()} {val_formatted}")
    
    # Only add WHERE clause if we have valid conditions
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    # ---------------- Group By ----------------
    # Only add GROUP BY if we have valid dimensions
    # 🔴 CRITICAL: Never emit empty GROUP BY clause
    if group_by_parts:
        # Validate all group_by_parts are non-empty strings
        valid_group_by = [g for g in group_by_parts if g and isinstance(g, str) and g.strip()]
        if valid_group_by:
            # Double-check: ensure no empty strings slipped through
            final_group_by = [g.strip() for g in valid_group_by if g.strip()]
            if final_group_by:
                sql += " GROUP BY " + ", ".join(final_group_by)
            # If all dimensions were filtered out, DO NOT add GROUP BY
            # This prevents "GROUP BY " with nothing after it

    # ---------------- Order By ----------------
    # Only add ORDER BY if we have valid order clauses
    order_clauses = []
    for o in order_by:
        if not isinstance(o, dict):
            continue
        
        col = o.get("column")
        if not col or not isinstance(col, str) or not col.strip():
            continue
        
        # Use alias if ordering by metric, otherwise use column name
        col = metric_alias_map.get(col, col.strip())
        direction = o.get("direction", "ASC")
        
        # Validate direction
        if direction.upper() not in ["ASC", "DESC"]:
            direction = "ASC"
        
        order_clauses.append(f"{col} {direction.upper()}")
    
    # Only add ORDER BY if we have valid clauses
    if order_clauses:
        sql += " ORDER BY " + ", ".join(order_clauses)

    # ---------------- Limit ----------------
    # Only add LIMIT if it's a positive integer
    if isinstance(limit, int) and limit > 0:
        sql += f" LIMIT {limit}"

    # Final SQL validation
    final_sql = sql + ";"
    _validate_sql_structure(final_sql)
    
    return final_sql


def _validate_sql_structure(sql: str) -> None:
    """
    Validate SQL structure to ensure no empty clauses or syntax errors.
    
    Raises:
        ValueError: If SQL structure is invalid
    """
    sql_upper = sql.upper().strip()
    
    # Check for empty SELECT
    if "SELECT" in sql_upper:
        # Find SELECT ... FROM pattern
        select_from_match = sql_upper.split("FROM")
        if len(select_from_match) < 2:
            raise ValueError("SQL structure invalid: Missing FROM clause")
        
        select_part = select_from_match[0].replace("SELECT", "").strip()
        if not select_part or select_part == ",":
            raise ValueError("SQL structure invalid: Empty SELECT clause")
    
    # Check for empty WHERE
    if "WHERE" in sql_upper:
        where_index = sql_upper.find("WHERE")
        after_where = sql_upper[where_index + 5:].strip()
        # Check if WHERE is followed by GROUP BY, ORDER BY, LIMIT, or semicolon without content
        if after_where.startswith(("GROUP BY", "ORDER BY", "LIMIT", ";")):
            raise ValueError("SQL structure invalid: Empty WHERE clause")
    
    # Check for empty GROUP BY
    if "GROUP BY" in sql_upper:
        group_by_index = sql_upper.find("GROUP BY")
        after_group_by = sql_upper[group_by_index + 8:].strip()
        # Check if GROUP BY is immediately followed by another clause (empty)
        if after_group_by.startswith(("ORDER BY", "LIMIT", ";")):
            raise ValueError("SQL structure invalid: Empty GROUP BY clause")
        # Check if GROUP BY has only commas or whitespace
        if not after_group_by or after_group_by.startswith(",") or after_group_by.replace(",", "").replace(" ", "").strip() == "":
            raise ValueError("SQL structure invalid: GROUP BY clause contains no valid columns")
        # Check if GROUP BY ends with comma (trailing comma)
        if after_group_by.rstrip().endswith(","):
            raise ValueError("SQL structure invalid: GROUP BY clause has trailing comma")
    
    # Check for empty ORDER BY
    if "ORDER BY" in sql_upper:
        order_by_index = sql_upper.find("ORDER BY")
        after_order_by = sql_upper[order_by_index + 8:].strip()
        if after_order_by.startswith(("LIMIT", ";")):
            raise ValueError("SQL structure invalid: Empty ORDER BY clause")
    
    # Check for trailing commas in SELECT
    if ",," in sql or ", ," in sql:
        raise ValueError("SQL structure invalid: Trailing or double commas detected")
    
    # Check for balanced parentheses
    if sql.count("(") != sql.count(")"):
        raise ValueError("SQL structure invalid: Unbalanced parentheses")