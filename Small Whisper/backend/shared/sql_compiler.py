def _is_string_type(col_type: str) -> bool:
    """Check if ClickHouse column type is a string type."""
    if not col_type:
        return False
    col_type_lower = col_type.lower()
    return "string" in col_type_lower or "char" in col_type_lower


def _normalize_invalid_casts(sql: str) -> str:
    """
    Global fix: Replace invalid ClickHouse functions with valid ones.
    toFloat64OrNullOrNull / toInt64OrNullOrNull do NOT exist in ClickHouse;
    only toFloat64OrNull / toInt64OrNull are valid.
    Apply to ALL generated SQL so double casting never reaches the engine.
    """
    if not sql:
        return sql
    sql = sql.replace("toFloat64OrNullOrNull(", "toFloat64OrNull(")
    sql = sql.replace("toInt64OrNullOrNull(", "toInt64OrNull(")
    return sql


def _agg_to_agg_if(agg: str) -> str:
    """Map aggregation to ClickHouse *If form: AVG→avgIf, SUM→sumIf, etc."""
    m = {"AVG": "avgIf", "SUM": "sumIf", "MIN": "minIf", "MAX": "maxIf"}
    return m.get(agg.upper(), agg.lower() + "If")


def _normalize_cast_func_name(cast_func: str) -> str:
    """Ensure cast function is valid ClickHouse (no double OrNull)."""
    if not cast_func:
        return cast_func
    return cast_func.replace("toFloat64OrNullOrNull", "toFloat64OrNull").replace("toInt64OrNullOrNull", "toInt64OrNull")


def _get_column_type(col_name: str, table: str, schema: dict) -> str:
    """
    Get column type from schema.
    
    Args:
        col_name: Column name
        table: Table name  
        schema: Schema dict with structure {table: [{name, type}, ...]}
    
    Returns:
        Column type string or empty string if not found
    """
    if not schema or table not in schema:
        return ""
    
    columns = schema.get(table, [])
    for col in columns:
        if col.get("name") == col_name:
            return col.get("type", "")
    return ""


def _build_safe_metric_filter(col: str, schema_type: str, has_explicit_cast: bool) -> str:
    """
    🔒 NaN-SAFE: Build WHERE clause filter for STRING columns with numeric aggregations.
    
    Returns WHERE clause condition or empty string if not needed.
    
    Pattern 1 (Row filtering - preferred):
    WHERE toFloat64OrNull(column) IS NOT NULL
    """
    # Only add filter for STRING columns that need safe casting
    if _is_string_type(schema_type) or has_explicit_cast:
        return f"toFloat64OrNull({col}) IS NOT NULL"
    return ""


def compile_sql(intent: dict, type_casting: list = None, schema: dict = None) -> str:
    """
    Compile intent into SQL with optional type casting.
    
    🔒 NaN-SAFE SYSTEMIC GUARANTEES (global contract for ALL queries):
    - STRING columns: safe cast exactly ONCE via toFloat64OrNull (never toFloat64OrNullOrNull)
    - Numeric aggregations: avgIf/sumIf/minIf/maxIf with condition (expr IS NOT NULL)
    - NaN guard: if(isNaN(aggIf(...)), 0, aggIf(...)) so result is never NaN
    - Zero groups removed: outer SELECT ... FROM (inner) WHERE metric_alias != 0
    - Invalid casts normalized: toFloat64OrNullOrNull → toFloat64OrNull in final SQL
    - SELECT/WHERE/GROUP BY/ORDER BY/LIMIT validated; no empty clauses.
    
    Args:
        intent: Structured intent with metrics, dimensions, filters, etc.
        type_casting: Optional list of type casting requirements from validation
        schema: Optional schema dict for automatic STRING column detection
    
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
    safe_metric_filters = []  # 🔒 NaN-SAFE: Collect WHERE conditions for STRING columns
    numeric_agg_aliases = []  # Aliases for metrics that get final WHERE ... != 0

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
            # 🔒 NaN-SAFE: Determine if column needs safe casting (exactly ONCE)
            col_expr = col
            needs_safe_cast = False
            has_explicit_cast = col in cast_map

            # Check if column is STRING type from schema (automatic detection)
            if schema:
                col_type = _get_column_type(col, table, schema)
                if _is_string_type(col_type) and agg.upper() in ["SUM", "AVG", "MIN", "MAX"]:
                    needs_safe_cast = True
                    print(f"🔧 Auto-detected STRING column: {col} ({col_type})")

            # Apply explicit type casting if provided — NEVER double-apply OrNull
            if has_explicit_cast:
                cast_func = _normalize_cast_func_name(cast_map[col])
                # If already safe (contains OrNull), use as-is to avoid toFloat64OrNullOrNull
                if "OrNull" in cast_func:
                    safe_cast_func = cast_func
                else:
                    safe_cast_func = cast_func.replace("toFloat64", "toFloat64OrNull").replace("toInt64", "toInt64OrNull")
                col_expr = f"{safe_cast_func}({col})"
                needs_safe_cast = True
                print(f"🔧 Type casting applied (NaN-safe): {col} → {col_expr}")
            elif needs_safe_cast:
                # 🔒 Apply safe casting exactly ONCE
                col_expr = f"toFloat64OrNull({col})"
                print(f"🔧 Auto-casting STRING column (NaN-safe): {col} → {col_expr}")

            # 🔒 WHERE filter for STRING columns (toFloat64OrNull(col) IS NOT NULL)
            if needs_safe_cast and agg.upper() in ["SUM", "AVG", "MIN", "MAX"]:
                filter_condition = f"toFloat64OrNull({col}) IS NOT NULL"
                if filter_condition not in safe_metric_filters:
                    safe_metric_filters.append(filter_condition)
                    print(f"🔒 Adding NULL filter: {filter_condition}")

            agg_upper = agg.upper()
            if agg_upper in ["AVG", "SUM", "MIN", "MAX"]:
                # Canonical pattern: *If + isNaN guard; zero groups removed in outer WHERE
                agg_if = _agg_to_agg_if(agg_upper)
                inner_agg = f"{agg_if}({col_expr}, {col_expr} IS NOT NULL)"
                metric_expr = f"if(isNaN({inner_agg}), 0, {inner_agg}) AS {alias}"
                select_parts.append(metric_expr)
                numeric_agg_aliases.append(alias)
            else:
                # COUNT: no NaN/zero filtering
                select_parts.append(f"{agg_upper}({col_expr}) AS {alias}")

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
    
    # 🔒 NaN-SAFE: Add safe metric filters for STRING columns (Pattern 1)
    # These filters exclude rows where STRING→Float conversion fails
    where_clauses.extend(safe_metric_filters)
    
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

    # ---------------- Order By (clauses only; appended below) ----------------
    order_clauses = []
    for o in order_by:
        if not isinstance(o, dict):
            continue
        col = o.get("column")
        if not col or not isinstance(col, str) or not col.strip():
            continue
        col = metric_alias_map.get(col, col.strip())
        direction = o.get("direction", "ASC")
        if direction.upper() not in ["ASC", "DESC"]:
            direction = "ASC"
        order_clauses.append(f"{col} {direction.upper()}")

    # ---------------- Wrap with outer WHERE != 0 when we have numeric aggregations ----------------
    # Contract: frontend must never receive NaN, NULL, or zero-only groups.
    if numeric_agg_aliases:
        inner_sql = sql  # SELECT ... FROM ... WHERE ... GROUP BY ...
        zero_filter = " AND ".join(f"{a} != 0" for a in numeric_agg_aliases)
        sql = f"SELECT * FROM ({inner_sql}) WHERE {zero_filter}"

    # Only add ORDER BY if we have valid clauses
    if order_clauses:
        sql += " ORDER BY " + ", ".join(order_clauses)

    # ---------------- Limit ----------------
    if isinstance(limit, int) and limit > 0:
        sql += f" LIMIT {limit}"

    # Global fix: normalize invalid ClickHouse functions (e.g. toFloat64OrNullOrNull → toFloat64OrNull)
    final_sql = _normalize_invalid_casts(sql + ";")
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