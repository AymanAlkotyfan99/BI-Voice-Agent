# BI Voice Agent - Developer Quick Reference

## 🎯 System Guarantees

| Guarantee | Description |
|-----------|-------------|
| **Continuity** | Pipeline never aborts for analytical questions |
| **Correctness** | Never generates semantically wrong queries |
| **Type Safety** | All STRING→numeric conversions explicit |
| **Transparency** | Full validation results logged and returned |

## 🔧 Key Components

### Core Files
```
shared/
├── pipeline.py              # Main orchestrator + validation
├── intent_sanitizer.py      # Resilient + semantic-aware
├── sql_compiler.py          # Type casting support
└── intent_validator.py      # 3-pass validation system
```

### Flow
```
Question → Intent → Sanitize → SQL → Validate → Reconstruct → Result
                        ↓         ↓       ↓          ↓
                    Infers   Detects  3 passes  Type casts
                    metrics   types   check     applied
```

## 📋 Multi-Pass Validation

### Pass 1: Intent Semantics
```python
✅ Checks:
  • Metrics align with question
  • Dimensions match grouping keywords
  • Domain relevance scoring
```

### Pass 2: Schema & Types
```python
✅ Checks:
  • Column existence
  • Type compatibility
  • STRING → numeric detection
  
💡 Output:
  • List of required type casts
```

### Pass 3: SQL Executability
```python
✅ Checks:
  • Required clauses present
  • Type casts applied
  • GROUP BY when needed
```

## 🔄 Type Casting Rules

### Automatic Cast Selection

| Column Pattern | Cast Function | Example |
|----------------|---------------|---------|
| `*_id` | `toInt64` | `student_id → toInt64(student_id)` |
| `year`, `age` | `toInt64` | `year → toInt64(year)` |
| `*_score` | `toFloat64` | `math_score → toFloat64(math_score)` |
| `amount`, `price` | `toFloat64` | `amount → toFloat64(amount)` |
| Default numeric | `toFloat64` | `value → toFloat64(value)` |

### Usage
```python
# SQL Compiler automatically applies casts
sql = compile_sql(intent, type_casting=validation['type_casting_needed'])
```

## 🧠 Semantic Awareness

### Domain Detection

```python
Domains:
  • academic: score, grade, student, test
  • financial: revenue, profit, cost, price
  • sales: order, product, customer
  • temporal: year, month, day, date
```

### Scoring
```python
Score calculation:
  • Token overlap: +1 per match
  • Domain match: +5
  • Substring match: +2
  • Special patterns: +1-3
  • ID penalty: -3 (unless requested)

Threshold: ≥2 required for selection
```

## 🛡️ Fallback Strategy

### 3-Level Fallback
```python
Level 1: Infer from question
  ├─ Detect aggregation (avg, sum, max, min, count)
  ├─ Match to domain-relevant column
  └─ Score ≥2 → Use metric

Level 2: First numeric column
  └─ If aggregation detected but no good match

Level 3: COUNT(*) guarantee
  ├─ Always executable
  ├─ Flags: "_semantic_fallback": True
  └─ Confidence reduced by 50%
```

## 📊 Confidence Scoring

### Formula
```python
base = 1.0

# Table/column validity
base *= validation_factor  # 0.3-1.0

# Term coverage
base *= (0.5 + 0.5 * coverage_ratio)

# Adjustments
if semantic_fallback:
    base *= 0.5
if warnings:
    base *= 0.9
```

### Interpretation
- **≥0.8**: High - Query likely correct
- **0.5-0.8**: Medium - Query reasonable  
- **<0.5**: Low - May need clarification

## 🚀 Quick Examples

### Example 1: Type Safety
```python
# Question: "Show average math scores by year"
# Schema: math_score (String)

Initial SQL (Invalid):
SELECT year, AVG(math_score) AS avg_math_score
FROM etl.scores GROUP BY year;

Validation → Type cast needed

Final SQL (Valid):
SELECT year, AVG(toFloat64(math_score)) AS avg_math_score
FROM etl.scores GROUP BY year;
```

### Example 2: Semantic Alignment
```python
# Question: "Show average math scores"
# Columns: student_id, math_score, registration_fee

Scoring:
  • math_score: 8 pts (domain+token+keyword)
  • student_id: -1 pts (ID penalty)
  • registration_fee: 0 pts (wrong domain)

Selected: math_score ✅
```

### Example 3: Resilience
```python
# Extracted metrics: [] (empty)

Fallback activated:
  1. Detect "average" → AVG
  2. Match "math" → math_score
  3. Create: AVG(math_score) ✅

Pipeline continues, no abort
```

## 🔍 Debugging

### Check Validation Results
```python
result = process_question("Show average math scores")

print(result['validation'])
# Output:
# {
#   "passed": True,
#   "warnings": [],
#   "reconstructed": True  # SQL was rebuilt with casts
# }
```

### Check Confidence
```python
if result['confidence'] < 0.5:
    # Low confidence - may need clarification
    print("Warning: Low confidence query")
```

### Check for Semantic Fallback
```python
metrics = result['intent']['metrics']
if any(m.get('_semantic_fallback') for m in metrics):
    # Fallback was used
    print("Warning: Semantic fallback used")
```

## 📝 Console Output

### Successful Validation
```
============================================================
🔍 PERFORMING MULTI-PASS VALIDATION
============================================================
📊 Validation Summary:
   Pass 1 (Intent): ✅ PASS
   Pass 2 (Schema): ✅ PASS
   Pass 3 (SQL):    ✅ PASS

✅ SQL validation passed - no reconstruction needed
============================================================
```

### With Reconstruction
```
============================================================
🔍 PERFORMING MULTI-PASS VALIDATION
============================================================
📊 Validation Summary:
   Pass 1 (Intent): ✅ PASS
   Pass 2 (Schema): ❌ FAIL
   Pass 3 (SQL):    ❌ FAIL

❌ Issues (2):
   • [Schema] Type casting required for AVG on STRING...
   • [SQL] Aggregation AVG on STRING column requires...

🔧 SQL reconstruction required
   Applying 1 type cast(s):
   • math_score (String) → toFloat64

🔧 Type casting applied: math_score → toFloat64(math_score)
✅ SQL reconstructed with type casting
============================================================
```

## 🎓 Best Practices

### For Integration
```python
# Always check validation results
result = process_question(question)

if not result.get('error'):
    sql = result['sql']
    confidence = result['confidence']
    validation = result['validation']
    
    # Act based on confidence
    if confidence >= 0.8:
        # High confidence - execute
        execute_query(sql)
    elif confidence >= 0.5:
        # Medium - execute with monitoring
        execute_with_monitoring(sql)
    else:
        # Low - may need clarification
        request_clarification(question)
```

### For Monitoring
```python
# Log validation failures
if not validation['passed']:
    log_warning("Validation issues", validation['warnings'])

# Log reconstruction
if validation['reconstructed']:
    log_info("SQL reconstructed with type casting")

# Alert on low confidence
if confidence < 0.5:
    alert("Low confidence query", question)
```

## 📚 Documentation

- `COMPLETE_SYSTEM_SUMMARY.md` - Full system overview
- `VALIDATION_SYSTEM_DOCUMENTATION.md` - Validation details
- `METRIC_FIX_DOCUMENTATION.md` - Resilience implementation
- `QUICK_REFERENCE.md` - Usage guide
- `DEV_QUICK_REFERENCE.md` - This file

## 🆘 Common Issues

### Issue: Empty metrics after sanitization
**Solution:** Inference automatically activates
```python
⚠️ No valid metrics after sanitization
✅ Inferred metric: {"column": "math_score", "aggregation": "AVG"}
```

### Issue: Type error on aggregation
**Solution:** Automatic type casting applied
```python
❌ AVG on STRING column
🔧 Type casting: math_score → toFloat64(math_score)
✅ SQL reconstructed
```

### Issue: Low confidence
**Solution:** Check semantic fallback flag
```python
if result['confidence'] < 0.5:
    metrics = result['intent']['metrics']
    if any(m.get('_semantic_fallback') for m in metrics):
        # Ambiguous query, consider clarification
```

---

**Version:** 2.0 (Resilience + Correctness)
**Status:** Production Ready
**Zero Breaking Changes**

