def compile_sql(intent: dict) -> str:
    table = intent["table"]
    metrics = intent.get("metrics", [])
    dimensions = intent.get("dimensions", [])
    filters = intent.get("filters", [])
    order_by = intent.get("order_by", [])
    limit = intent.get("limit")

    if not metrics:
        raise ValueError("Intent must contain at least one metric")

    select_parts = []
    group_by_parts = []

    # ---------------- Dimensions ----------------
    for dim in dimensions:
        select_parts.append(dim)
        group_by_parts.append(dim)

    # ---------------- Metrics ----------------
    metric_alias_map = {}
    for m in metrics:
        col = m["column"]
        agg = m["aggregation"]
        alias = m.get("alias") or f"{agg.lower()}_{col}"
        metric_alias_map[col] = alias
        
        # ✅ Handle COUNT(*) specially
        if col == "*":
            select_parts.append(f"{agg}(*) AS {alias}")
        else:
            select_parts.append(f"{agg}({col}) AS {alias}")

    sql = f"SELECT {', '.join(select_parts)} FROM {table}"

    # ---------------- Filters ----------------
    if filters:
        where_clauses = []
        for f in filters:
            val = f["value"]
            if isinstance(val, str):
                val = f"'{val}'"
            where_clauses.append(f"{f['column']} {f['operator']} {val}")
        sql += " WHERE " + " AND ".join(where_clauses)

    # ---------------- Group By ----------------
    if group_by_parts:
        sql += " GROUP BY " + ", ".join(group_by_parts)

    # ---------------- Order By ----------------
    if order_by:
        clauses = []
        for o in order_by:
            col = o.get("column")
            # إذا كان الترتيب على metric، استخدم alias
            col = metric_alias_map.get(col, col)
            direction = o.get("direction", "ASC")
            clauses.append(f"{col} {direction}")
        sql += " ORDER BY " + ", ".join(clauses)

    # ---------------- Limit ----------------
    if isinstance(limit, int) and limit > 0:
        sql += f" LIMIT {limit}"

    return sql + ";"