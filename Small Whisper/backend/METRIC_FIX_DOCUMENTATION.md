# Metric Sanitization Fix - Documentation

## Problem

The BI Voice Agent pipeline was failing at the analytical stage with the error:
```
"No valid metrics after sanitization"
```

This occurred when:
1. Whisper transcription worked correctly
2. Intent classification correctly marked the question as analytical
3. LLM was called successfully
4. BUT metric extraction/sanitization removed all extracted metrics

Example failing question: **"Show average math scores by year"**

## Root Cause

In `backend/shared/intent_sanitizer.py`, line 69, the code raised a `ValueError` when no metrics survived the sanitization process:

```python
if not sanitized_metrics:
    raise ValueError("No valid metrics after sanitization")
```

This was too strict because:
- The LLM might extract metrics with columns that don't pass numeric validation
- Column name matching might fail even when the intent is clear
- The system would abort instead of attempting to recover

## Solution

### 1. Enhanced Metric Inference (`intent_sanitizer.py`)

Added `_infer_metric_from_question()` function that:
- Detects aggregation keywords (average, sum, max, min, count) in the question
- Matches these to appropriate numeric columns in the schema
- Uses intelligent scoring to find the best column match
- Falls back to `COUNT(*)` if no specific metric can be inferred

**Key features:**
- Token-based matching between question and column names
- Special boosting for common patterns (e.g., "score" in question + "score" in column)
- Multi-level fallback strategy

### 2. Improved Numeric Type Detection

Added `_is_numeric_type()` function that:
- Checks actual ClickHouse column types (Int*, Float*, Decimal*, etc.)
- Covers nullable and nested type variants
- Supplements keyword-based numeric column detection

**Before:** Only checked column names for keywords like "id", "count", "amount"
**After:** Also validates against actual database type information

### 3. Better Column Matching Logic

Enhanced the column matching in `_infer_metric_from_question()`:
- Uses set intersection for token matching
- Considers substring matches
- Applies scoring system with special boosts for strong matches
- Selects the best matching column instead of just the first match

### 4. SQL Compiler Fix (`sql_compiler.py`)

Updated SQL generation to handle `COUNT(*)` properly:

```python
if col == "*":
    select_parts.append(f"{agg}(*) AS {alias}")
else:
    select_parts.append(f"{agg}({col}) AS {alias}")
```

### 5. Improved Error Logging (`pipeline.py`)

Added better error messages to distinguish between:
- Non-analytical questions (expected skip)
- Analytical stage failures (actual errors)

**Before:** "Analytical stage failed: {e}"
**After:** Includes error details and separates error types clearly

## Fallback Strategy

When sanitization removes all metrics, the system now follows this hierarchy:

1. **Try to infer specific metric from question**
   - Detect aggregation keyword (AVG, SUM, MAX, MIN, COUNT)
   - Find best matching numeric column
   - Create appropriate metric

2. **Use COUNT with numeric column**
   - If no specific match but aggregation detected
   - Use first available numeric column

3. **Use COUNT(*) as last resort**
   - Always works
   - Ensures pipeline never aborts due to empty metrics

## Files Modified

1. `backend/shared/intent_sanitizer.py`
   - Added `_is_numeric_type()` helper
   - Added `_infer_metric_from_question()` helper
   - Removed the strict `raise ValueError` 
   - Implemented metric inference and fallback logic

2. `backend/shared/sql_compiler.py`
   - Fixed handling of `COUNT(*)` in SQL generation

3. `backend/shared/pipeline.py`
   - Improved error logging and messaging

## Testing

Created `test_metric_fix.py` with 5 test scenarios:
1. Valid metric (should pass through unchanged)
2. Invalid metric that gets removed (should infer from question)
3. Empty metrics list (should infer from question)
4. No matching column (should use first numeric column)
5. Count query (should use COUNT appropriately)

## Impact

### Before Fix
- Questions with metric extraction issues would **fail completely**
- Pipeline would abort at analytical stage
- No fallback or recovery mechanism
- Misleading error messages

### After Fix
- Questions with metric extraction issues **continue to SQL generation**
- System attempts intelligent metric inference
- Multiple fallback levels ensure resilience
- Clear, actionable error messages
- Questions like "Show average math scores by year" now work correctly

## Non-Breaking Changes

- All existing functionality preserved
- Only affects error/edge cases that previously failed
- No changes to successful metric extraction paths
- No API or interface changes

## Future Enhancements

Potential improvements for consideration:
1. LLM retry with improved prompt when metrics fail
2. Multi-metric inference for complex questions
3. Column type learning from query history
4. User feedback loop for metric inference accuracy

