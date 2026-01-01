def build_prompt(question: str, schema: dict) -> str:
    schema_lines = []

    for table, columns in schema.items():
        schema_lines.append(f"Table: {table}")
        for col in columns:
            schema_lines.append(f"  - {col['name']} ({col['type']})")

    schema_text = "\n".join(schema_lines)

    return f"""
You are a BI intent extraction engine.

Your task is to convert a natural language analytical question
into a structured, machine-readable analytical intent.

The intent must be suitable for automatic SQL generation
against a ClickHouse database.

====================
GENERAL RULES
====================
- Use ONLY tables and columns from the provided database schema
- DO NOT invent tables or columns
- DO NOT generate SQL
- DO NOT explain the result
- Output ONLY valid JSON that strictly follows the output format

====================
SEMANTIC CONSTRAINTS
====================
- Metrics MUST use numeric columns only (Int, Float, Decimal)
- Dimensions MUST use categorical columns only (String, Enum)
- Date or time filters MUST use Date / DateTime columns
- Aggregations SUM, AVG, MIN, MAX MUST NOT be applied to non-numeric columns
- COUNT may be applied to any column
- If the question implies grouping (e.g. breakdown, grouping, comparison, per, by),
  the grouping MUST be done using the most appropriate categorical identifier
- If no grouping is implied, the dimensions list MUST be empty
- Filters represent WHERE conditions derived from the question
- order_by and limit are OPTIONAL and must be included only if implied

====================
DATABASE SCHEMA
====================
{schema_text}

====================
OUTPUT FORMAT
====================
{{
  "table": string,
  "metrics": [
    {{
      "column": string,
      "aggregation": "SUM|COUNT|AVG|MIN|MAX",
      "alias": string
    }}
  ],
  "dimensions": [string],
  "filters": [
    {{
      "column": string,
      "operator": string,
      "value": string|number
    }}
  ],
  "order_by": [
    {{
      "column": string,
      "direction": "ASC|DESC"
    }}
  ],
  "limit": number|null
}}

====================
USER QUESTION
====================
{question}
""".strip()