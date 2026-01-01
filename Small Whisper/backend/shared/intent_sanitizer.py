def _is_numeric_type(col_type: str) -> bool:
    """
    Check if a column type is numeric based on ClickHouse type names.
    Covers: Int*, UInt*, Float*, Decimal*, Nullable variants, etc.
    """
    if not col_type:
        return False
    
    col_type_lower = col_type.lower()
    
    # Core numeric types
    numeric_types = ("int", "float", "decimal", "double", "numeric")
    if any(nt in col_type_lower for nt in numeric_types):
        return True
    
    # Specific ClickHouse types
    clickhouse_numeric = ("uint", "bigint", "smallint", "tinyint", "money", "real")
    if any(nt in col_type_lower for nt in clickhouse_numeric):
        return True
    
    return False


def _infer_metric_from_question(question: str, numeric_columns: list, categorical_columns: list) -> dict | None:
    """
    Infer a metric from the question when sanitization removed all metrics.
    Looks for aggregation keywords and matching columns.
    """
    question_lower = question.lower()
    
    # Map common question patterns to aggregation types
    agg_patterns = [
        (["average", "avg", "mean"], "AVG"),
        (["sum", "total"], "SUM"),
        (["maximum", "max", "highest", "largest"], "MAX"),
        (["minimum", "min", "lowest", "smallest"], "MIN"),
        (["count", "number of", "how many"], "COUNT"),
    ]
    
    # Find which aggregation is implied
    detected_agg = None
    for keywords, agg_type in agg_patterns:
        if any(kw in question_lower for kw in keywords):
            detected_agg = agg_type
            break
    
    if not detected_agg:
        return None
    
    # For COUNT, we can use any column or *
    if detected_agg == "COUNT":
        if numeric_columns:
            return {
                "column": numeric_columns[0],
                "aggregation": "COUNT",
                "alias": f"count_{numeric_columns[0]}"
            }
        return {
            "column": "*",
            "aggregation": "COUNT",
            "alias": "count"
        }
    
    # For other aggregations, try to find a matching numeric column
    # Look for column names mentioned in the question
    best_match = None
    best_score = 0
    
    for col in numeric_columns:
        col_lower = col.lower()
        col_tokens = set(col_lower.replace("_", " ").split())
        question_tokens = set(question_lower.split())
        
        # Score based on token overlap
        score = len(col_tokens & question_tokens)
        
        # Boost score if column name is substring of question or vice versa
        if col_lower in question_lower or any(token in question_lower for token in col_tokens if len(token) > 3):
            score += 2
        
        # Special boost for "score" columns when question mentions "score"
        if "score" in col_lower and "score" in question_lower:
            score += 3
        
        if score > best_score:
            best_score = score
            best_match = col
    
    # If we found a good match, use it
    if best_match and best_score > 0:
        return {
            "column": best_match,
            "aggregation": detected_agg,
            "alias": f"{detected_agg.lower()}_{best_match}"
        }
    
    # If no specific column match, use the first numeric column
    if numeric_columns:
        return {
            "column": numeric_columns[0],
            "aggregation": detected_agg,
            "alias": f"{detected_agg.lower()}_{numeric_columns[0]}"
        }
    
    return None


def resolve_entity_dimension(question: str, schema: dict, table: str):
    """
    Resolve linguistic entities (e.g. customer, product, user)
    to identifier columns in a generic way.
    """
    question = question.lower()
    columns = schema[table]  # list of dicts: {"name", "type"}

    identifier_columns = [
        c["name"] for c in columns
        if c["name"].endswith("_id") or c["name"].endswith("_name")
    ]

    for col in identifier_columns:
        base = col.replace("_id", "").replace("_name", "")
        if base in question:
            return col

    return None


def sanitize_intent(intent: dict, schema: dict, question: str) -> dict:
    """
    Dataset-agnostic and question-agnostic intent sanitizer.
    Removes only technically invalid or hallucinated parts.
    """

    table = intent.get("table")
    if table not in schema:
        raise ValueError("Invalid table in intent")

    columns = schema[table]  # list of dicts
    column_names = [c["name"] for c in columns]

    numeric_like_keywords = (
        "id", "count", "num", "amount", "price", "total", "sales", "qty"
    )

    # ✅ Also check for actual numeric types from schema
    numeric_columns = [
        c["name"] for c in columns
        if any(k in c["name"].lower() for k in numeric_like_keywords)
        or _is_numeric_type(c.get("type", ""))
    ]

    categorical_columns = [
        c for c in column_names if c not in numeric_columns
    ]

    # ---------------- Metrics ----------------
    sanitized_metrics = []
    for m in intent.get("metrics", []):
        col = m.get("column")
        agg = m.get("aggregation")
        alias = m.get("alias")

        if not col or not agg:
            continue
        if col not in column_names:
            continue
        if agg in {"SUM", "AVG", "MIN", "MAX"} and col not in numeric_columns:
            continue

        sanitized_metrics.append({
            "column": col,
            "aggregation": agg,
            "alias": alias or f"{agg.lower()}_{col}"
        })

    # ✅ If no valid metrics after sanitization, try to infer from question
    if not sanitized_metrics:
        print("⚠️ No valid metrics after sanitization. Attempting to infer from question...")
        inferred_metric = _infer_metric_from_question(question, numeric_columns, categorical_columns)
        if inferred_metric:
            sanitized_metrics.append(inferred_metric)
            print(f"✅ Inferred metric: {inferred_metric}")
        else:
            # ✅ Last resort: use COUNT(*) if no metrics can be inferred
            print("⚠️ Could not infer specific metric. Using COUNT(*) as fallback.")
            sanitized_metrics.append({
                "column": "*",
                "aggregation": "COUNT",
                "alias": "count"
            })

    intent["metrics"] = sanitized_metrics

    # ---------------- Dimensions ----------------
    sanitized_dimensions = [
        d for d in intent.get("dimensions", []) if d in categorical_columns
    ]

    if not sanitized_dimensions:
        resolved = resolve_entity_dimension(question, schema, table)
        if resolved:
            sanitized_dimensions = [resolved]

    intent["dimensions"] = sanitized_dimensions

    # ---------------- Filters ----------------
    question_lc = question.lower()
    sanitized_filters = []

    for f in intent.get("filters", []):
        col = f.get("column")
        op = f.get("operator")
        val = f.get("value")

        # Guard: لا نسمح بفلترة لم تُذكر قيمتها في السؤال
        if (
            col in column_names
            and op
            and val is not None
            and str(val).lower() in question_lc
        ):
            sanitized_filters.append({
                "column": col,
                "operator": op,
                "value": val
            })

    intent["filters"] = sanitized_filters

    # ---------------- Order By ----------------
    intent["order_by"] = [
        o for o in intent.get("order_by", [])
        if o.get("column") in column_names
        and o.get("direction", "ASC") in {"ASC", "DESC"}
    ]

    # ---------------- Limit ----------------
    limit = intent.get("limit")
    intent["limit"] = limit if isinstance(limit, int) and limit > 0 else None

    return intent
