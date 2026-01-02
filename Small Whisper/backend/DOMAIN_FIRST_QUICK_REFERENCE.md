# DOMAIN-FIRST QUICK REFERENCE GUIDE

## 🎯 For AI/LLM Intent Extraction

When generating intents for analytical questions, follow this mental model:

### Step 1: Identify the Question Domain

Ask yourself: **What domain does this question belong to?**

- **Academic**: "average score", "student grades", "test results"
- **Financial**: "total revenue", "profit margin", "costs"
- **Sales**: "products sold", "order quantity", "customer purchases"
- **Demographic**: "enrollment count", "population", "headcount"

### Step 2: Lock to That Domain

Once you identify the domain, **stay within it**. Do NOT:
- Use financial columns for academic questions
- Use academic columns for financial questions
- Fall back to generic metrics like `COUNT(*)`

### Step 3: Select Domain-Aligned Columns FIRST

Find columns that semantically match the question domain:

```python
# ✅ CORRECT
Question: "What is the average student score?"
Column: "math_score" (academic domain)
Type: String
Action: Preserve column, flag for type casting

# ❌ INCORRECT
Question: "What is the average student score?"
Column: "student_id" (numeric but semantically wrong)
Type: Int64
Action: REFUSE - semantically incorrect even if type-compatible
```

### Step 4: Don't Worry About Type Issues

If the domain-aligned column is String-typed:
- **Don't discard it**
- **Don't switch columns**
- The system will automatically apply type casting (e.g., `toFloat64()`)

---

## 🔧 For Developers

### Adding New Domains

1. Update domain keywords in `intent_validator.py`:

```python
domains = {
    "your_domain": ["keyword1", "keyword2", "keyword3"],
}
```

2. Update the same in `intent_sanitizer.py`

### Type Casting Support

The system supports ClickHouse casting functions:
- `toFloat64()` - For decimal numbers
- `toInt64()` - For integers
- Automatically inferred based on column name and context

### Validation Flow

```
User Question
    ↓
LLM Intent Extraction
    ↓
Sanitizer (Auto-Repair)
    ↓
Pass 1: Domain & Intent Validation ← Locks domain, checks alignment
    ↓
Pass 2: Type Repair ← Identifies type casting needs
    ↓
SQL Compilation (with type casting)
    ↓
Pass 3: SQL Validation ← Checks syntax & executability
    ↓
Return SQL or Refuse
```

---

## 📋 Common Scenarios

### Scenario 1: String-Typed Numeric Column

**Question:** "What is the average math score?"

**Schema:**
```python
{"name": "math_score", "type": "String"}
```

**System Behavior:**
1. Domain identified: **Academic**
2. Column `math_score` matches domain ✅
3. Type issue detected: String for AVG
4. Type casting applied: `toFloat64(math_score)`
5. SQL generated: `SELECT AVG(toFloat64(math_score)) AS avg_math_score FROM students;`

**Result:** ✅ Success with type casting

---

### Scenario 2: Domain Mismatch

**Question:** "What is the total revenue?"

**Intent (incorrectly extracted):**
```python
{
    "metrics": [
        {"column": "test_score", "aggregation": "SUM"}  # ❌ Wrong domain
    ]
}
```

**System Behavior:**
1. Domain identified: **Financial**
2. Column domain: **Academic**
3. Domain violation detected ❌
4. **Refuse to generate SQL**

**Result:** ❌ Refused with domain violation error

---

### Scenario 3: Generic Fallback Attempt

**Question:** "What is the average score?"

**Intent (incorrectly extracted):**
```python
{
    "metrics": [
        {"column": "*", "aggregation": "COUNT"}  # ❌ Generic fallback
    ]
}
```

**System Behavior:**
1. Domain identified: **Academic**
2. Domain-specific columns exist: `math_score`, `reading_score`
3. Generic `COUNT(*)` detected ❌
4. **Refuse to generate SQL**

**Result:** ❌ Refused with generic fallback error

---

### Scenario 4: Auto-Repair Success

**Question:** "What is the average GPA?"

**Intent (empty metrics):**
```python
{
    "metrics": []  # LLM failed to extract
}
```

**Schema:**
```python
[
    {"name": "gpa", "type": "String"},
    {"name": "tuition_fee", "type": "Float64"}
]
```

**System Behavior:**
1. Metrics empty → Trigger auto-repair
2. Domain identified: **Academic**
3. Find domain-aligned columns:
   - `gpa` → Academic ✅
   - `tuition_fee` → Financial ❌
4. Select `gpa` (domain match)
5. Apply type casting: `toFloat64(gpa)`
6. Generate: `SELECT AVG(toFloat64(gpa)) AS avg_gpa FROM students;`

**Result:** ✅ Auto-repair successful with domain preservation

---

## 🚫 What NOT To Do

### ❌ DON'T: Discard columns due to type issues
```python
# BAD
if col_type == "String" and aggregation == "AVG":
    continue  # ❌ Violates domain-first principle
```

### ❌ DON'T: Use type-compatible but semantically wrong columns
```python
# BAD
# Question: "What is the average score?"
# Using: student_id (numeric but semantically wrong)
```

### ❌ DON'T: Fall back to COUNT(*) for specific metrics
```python
# BAD
# Question: "What is the average revenue?"
# Using: COUNT(*) because revenue is String-typed
```

### ❌ DON'T: Switch domains silently
```python
# BAD
# Question: "What is the average score?" (Academic)
# Using: revenue column because it's numeric (Financial)
```

---

## ✅ What TO Do

### ✅ DO: Preserve domain-aligned columns
```python
# GOOD
if col_domain == question_domain:
    if _is_string_type(col_type):
        type_casting_needed.append({"column": col, "cast": "toFloat64"})
    preserve_as_candidate(col)
```

### ✅ DO: Apply type casting for String columns
```python
# GOOD
SELECT AVG(toFloat64(math_score)) AS avg_math_score FROM students;
```

### ✅ DO: Refuse cross-domain substitutions
```python
# GOOD
if question_domain != column_domain:
    raise ValueError("Domain violation: Cannot use financial metric for academic question")
```

### ✅ DO: Request clarification when no domain match exists
```python
# GOOD
if not domain_aligned_columns:
    raise ValueError(
        f"No {question_domain} metrics found. "
        f"Please clarify which metric to analyze."
    )
```

---

## 🔍 Debugging Tips

### Check Domain Identification
```python
from shared.intent_sanitizer import _identify_question_domain, _identify_column_domain

question_domain = _identify_question_domain("What is the average score?")
print(f"Question domain: {question_domain}")  # Should be "academic"

col_domain = _identify_column_domain("math_score")
print(f"Column domain: {col_domain}")  # Should be "academic"
```

### Run Validation Manually
```python
from shared.intent_validator import perform_multi_pass_validation

validation = perform_multi_pass_validation(intent, sql, question, schema)

if not validation["valid"]:
    print("Issues:", validation["overall_issues"])
    print("Type casting needed:", validation["type_casting_needed"])
```

### Test Auto-Repair
```python
from shared.intent_sanitizer import sanitize_intent

intent = {"table": "students", "metrics": []}
repaired_intent = sanitize_intent(intent, schema, question)
print("Auto-repaired metrics:", repaired_intent["metrics"])
```

---

## 📊 Testing

Run the test suite to verify domain-first principles:

```bash
cd backend
python test_domain_first_principles.py
```

Expected output:
```
TEST RESULTS: 7 passed, 0 failed
✅ ALL TESTS PASSED - Domain-First Principles Verified
```

---

## 🎓 Key Principles (Remember Always)

1. **Domain FIRST, Type SECOND**
2. **Semantic Correctness > Executability**
3. **Type issues are REPAIRABLE**
4. **Cross-domain substitutions are FORBIDDEN**
5. **Refuse > Mislead**

**You are a domain-aware analytical system, not a generic SQL generator.**

