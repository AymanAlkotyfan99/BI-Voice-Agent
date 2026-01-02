from llm_app.intent_service import extract_intent
from shared.intent_sanitizer import sanitize_intent
from shared.sql_compiler import compile_sql
from shared.sql_validator import validate_sql
from shared.chart_recommender import recommend_chart
from shared.intent_validator import perform_multi_pass_validation
from reasoning_app.runner import run_reasoning


def process_question(question: str):
    """
    Full analytical pipeline: Intent → SQL → Chart
    WITH STRICT MULTI-PASS VALIDATION
    """
    result = extract_intent(question)

    if result.get("error"):
        return result

    intent_in = result["intent"]
    schema = result["schema"]

    table = intent_in.get("table")
    resolved_table = _resolve_table_name(table, schema, question, intent_in)
    intent_in["table"] = resolved_table

    _adapt_intent_columns(intent_in, schema)

    intent = sanitize_intent(
        intent_in,
        schema,
        question
    )

    # ✅ FIRST SQL GENERATION (may need reconstruction)
    sql_initial = compile_sql(intent)
    
    # ✅ MULTI-PASS VALIDATION
    print("\n" + "="*60)
    print("🔍 PERFORMING MULTI-PASS VALIDATION")
    print("="*60)
    
    validation_result = perform_multi_pass_validation(intent, sql_initial, question, schema)
    
    # Log validation results
    print(f"\n📊 Validation Summary:")
    print(f"   Pass 1 (Intent): {'✅ PASS' if validation_result['pass1']['valid'] else '❌ FAIL'}")
    print(f"   Pass 2 (Schema): {'✅ PASS' if validation_result['pass2']['valid'] else '❌ FAIL'}")
    print(f"   Pass 3 (SQL):    {'✅ PASS' if validation_result['pass3']['valid'] else '❌ FAIL'}")
    
    if validation_result["overall_warnings"]:
        print(f"\n⚠️  Warnings ({len(validation_result['overall_warnings'])}):")
        for warning in validation_result["overall_warnings"]:
            print(f"   • {warning}")
    
    if not validation_result["valid"]:
        print(f"\n❌ Issues ({len(validation_result['overall_issues'])}):")
        for issue in validation_result["overall_issues"]:
            print(f"   • {issue}")
    
    # ✅ RECONSTRUCT SQL IF NEEDED (with re-validation loop)
    sql = sql_initial
    reconstruction_count = 0
    max_reconstructions = 2  # Prevent infinite loops
    
    while validation_result["requires_reconstruction"] and reconstruction_count < max_reconstructions:
        reconstruction_count += 1
        print(f"\n🔧 SQL reconstruction required (Attempt {reconstruction_count})")
        
        type_casting_needed = validation_result.get("type_casting_needed", [])
        if type_casting_needed:
            print(f"   Applying {len(type_casting_needed)} type cast(s):")
            for tc in type_casting_needed:
                print(f"   • {tc['column']} ({tc['current_type']}) → {tc['required_cast']}")
            
            # Recompile SQL with type casting
            sql = compile_sql(intent, type_casting=type_casting_needed)
            print(f"\n✅ SQL reconstructed with type casting")
            
            # 🔧 RE-VALIDATION LOOP: Validate again after auto-repair
            print(f"\n🔄 Re-validating after auto-repair...")
            validation_result = perform_multi_pass_validation(intent, sql, question, schema)
            
            print(f"   Pass 1 (Intent):  {'✅ PASS' if validation_result['pass1']['valid'] else '❌ FAIL'}")
            print(f"   Pass 2 (Schema):  {'✅ PASS' if validation_result['pass2']['valid'] else '❌ FAIL'}")
            print(f"   Pass 3 (SQL):     {'✅ PASS' if validation_result['pass3']['valid'] else '❌ FAIL'}")
            
            if validation_result["valid"]:
                print(f"✅ Re-validation PASSED")
                break
        else:
            # No type casting, but reconstruction needed - might be semantic issue
            break
    
    # After reconstruction attempts, check for critical semantic failures
    if validation_result["requires_reconstruction"]:
        # Still has issues after reconstruction attempts
        print(f"\n🔧 SQL reconstruction did not resolve all issues")
        
        # 🔴 STRICT MODE: If semantic validation failed, REFUSE
        if not validation_result["pass1"]["valid"]:
            semantic_issues = [i for i in validation_result["overall_issues"] if "[Intent]" in i]
            # Exclude auto-repair warnings
            critical_semantic = [i for i in semantic_issues if "auto-repaired" not in i.lower()]
            
            if critical_semantic:
                error_msg = "Semantic validation failed: " + "; ".join(critical_semantic)
                print(f"\n❌ {error_msg}")
                print(f"🔴 REFUSING to generate semantically incorrect SQL")
                return {
                    "error": True,
                    "message": error_msg,
                    "requires_clarification": True,
                    "validation": validation_result
                }
        
        # If there are still critical issues, refuse execution
        if not validation_result["valid"]:
            critical_issues = [i for i in validation_result["overall_issues"] 
                             if "domain mismatch" in i.lower() or "generic" in i.lower()]
            if critical_issues:
                error_msg = "Critical validation failures: " + "; ".join(critical_issues)
                print(f"\n❌ {error_msg}")
                print(f"🔴 REFUSING to generate misleading SQL")
                return {
                    "error": True,
                    "message": error_msg,
                    "requires_clarification": True,
                    "validation": validation_result
                }
            
            print(f"\n⚠️  WARNING: SQL generated but validation issues remain")
            print(f"   This query may not fully match user intent")
    else:
        print(f"\n✅ SQL validation passed - no reconstruction needed")
    
    print("="*60 + "\n")
    
    # ✅ FINAL SQL VALIDATION BEFORE RETURNING
    try:
        validate_sql(sql)
    except ValueError as e:
        return {
            "error": True,
            "message": f"SQL validation failed: {str(e)}"
        }
    
    chart = recommend_chart(intent)

    # ✅ CALCULATE CONFIDENCE (adjusted for auto-repair and validation)
    confidence = _calculate_confidence(intent, question, schema)
    
    # 🔧 Reduce confidence for auto-repaired metrics
    has_auto_repair = any(m.get("_auto_repaired") for m in intent.get("metrics", []))
    has_weak_match = any(m.get("_weak_match") for m in intent.get("metrics", []))
    
    if has_weak_match:
        confidence *= 0.6  # Significant reduction for weak matches
        print("⚠️  Confidence reduced: Weak semantic match in auto-repair")
    elif has_auto_repair:
        confidence *= 0.85  # Minor reduction for strong auto-repair
        print("⚠️  Confidence adjusted: Auto-repair applied")
    
    # Reduce confidence if validation warnings exist
    if validation_result["overall_warnings"]:
        confidence *= 0.9
    
    return {
        "intent": intent,
        "sql": sql,
        "chart": chart,
        "confidence": confidence,
        "validation": {
            "passed": validation_result["valid"],
            "warnings": validation_result["overall_warnings"],
            "reconstructed": validation_result["requires_reconstruction"]
        }
    }


def _columns_from_intent(intent: dict) -> list:
    cols = set()
    for m in intent.get("metrics", []):
        col = m.get("column")
        if col:
            cols.add(col)
    for d in intent.get("dimensions", []):
        cols.add(d)
    for f in intent.get("filters", []):
        col = f.get("column")
        if col:
            cols.add(col)
    for o in intent.get("order_by", []):
        col = o.get("column")
        if col:
            cols.add(col)
    return sorted(cols)


def _resolve_table_name(table: str, schema: dict, question: str, intent: dict) -> str:
    if not table:
        return table
    if table in schema:
        return table
    suffix_matches = [t for t in schema.keys() if t.split(".")[-1] == table]
    if len(suffix_matches) == 1:
        return suffix_matches[0]
    suffix_ci = [t for t in schema.keys() if t.split(".")[-1].lower() == table.lower()]
    if len(suffix_ci) == 1:
        return suffix_ci[0]
    qt = _tokens(question)
    ref_tokens = set()
    for m in intent.get("metrics", []):
        ref_tokens |= _tokens(m.get("column") or "")
    for d in intent.get("dimensions", []):
        ref_tokens |= _tokens(d)
    for f in intent.get("filters", []):
        ref_tokens |= _tokens(f.get("column") or "")
    for o in intent.get("order_by", []):
        ref_tokens |= _tokens(o.get("column") or "")
    best = None
    best_score = 0
    for t in schema.keys():
        suffix = t.split(".")[-1]
        score = len(_tokens(suffix) & qt)
        cols = schema[t]
        for c in cols:
            ct = _tokens(c)
            if ct & qt:
                score += 1
            if ct & ref_tokens:
                score += 2
        if score > best_score:
            best = t
            best_score = score
    return best or table


def _adapt_intent_columns(intent: dict, schema: dict):
    table = intent.get("table")
    cols = schema.get(table) or []
    cols = schema.get(table) or []
    col_names = [c["name"] for c in cols]

    def map_col(name: str) -> str:
        if not name:
            return name
        if name in col_names:
            return name
        return _best_match(name, cols) or name

    metrics = []
    for m in intent.get("metrics", []):
        col = map_col(m.get("column"))
        metrics.append({
            "column": col,
            "aggregation": m.get("aggregation"),
            "alias": m.get("alias")
        })
    intent["metrics"] = metrics
    intent["dimensions"] = [map_col(d) for d in intent.get("dimensions", [])]
    filters = []
    for f in intent.get("filters", []):
        filters.append({
            "column": map_col(f.get("column")),
            "operator": f.get("operator"),
            "value": f.get("value")
        })
    intent["filters"] = filters
    order_by = []
    for o in intent.get("order_by", []):
        order_by.append({
            "column": map_col(o.get("column")),
            "direction": o.get("direction")
        })
    intent["order_by"] = order_by


def _tokens(name: str) -> set:
    return set((name or "").replace("_", " ").lower().split())


def _best_match(name: str, columns: list) -> str | None:
    target = (name or "").replace("_", " ").lower()
    best = None
    best_score = 0

    for c in columns:
        col_name = c["name"]  # ✅ استخراج اسم العمود
        cn = col_name.replace("_", " ").lower()

        if cn == target:
            return col_name

        score = 0
        ct = set(cn.split())
        tt = set(target.split())

        score += len(ct & tt)

        if target in cn or cn in target:
            score += 1

        if score > best_score:
            best = col_name
            best_score = score

    return best


def _calculate_confidence(intent: dict, question: str, schema: dict) -> float:
    """
    Calculate confidence score for the generated intent.
    Returns a value between 0.0 and 1.0
    """
    confidence = 1.0
    
    # Check if table exists in schema
    table = intent.get("table")
    if table not in schema:
        confidence *= 0.3
    else:
        # Check if all columns exist in schema
        table_columns = [c["name"] for c in schema[table]]
        
        for metric in intent.get("metrics", []):
            if metric.get("column") not in table_columns:
                confidence *= 0.7
        
        for dim in intent.get("dimensions", []):
            if dim not in table_columns:
                confidence *= 0.7
        
        for filt in intent.get("filters", []):
            if filt.get("column") not in table_columns:
                confidence *= 0.8
    
    # Check if key terms from question are covered
    question_lower = question.lower()
    covered_terms = 0
    total_terms = 0
    
    for word in question_lower.split():
        if len(word) > 3:  # Only check meaningful words
            total_terms += 1
            # Check if word appears in any column or table name
            if table and word in table.lower():
                covered_terms += 1
            elif any(word in col.lower() for col in table_columns):
                covered_terms += 1
    
    if total_terms > 0:
        coverage_ratio = covered_terms / total_terms
        confidence *= (0.5 + 0.5 * coverage_ratio)
    
    # Ensure confidence is between 0 and 1
    return max(0.0, min(1.0, confidence))



def process_after_whisper(text: str):
    """
    Complete pipeline after Whisper transcription:
    1. Reasoning layer (classify question type)
    2. If analytical → Intent extraction → SQL + Chart
    """
    state = run_reasoning(text)

    reasoning = {
        "question_type": state.get("question_type"),
        "needs_sql": state.get("needs_sql", False),
        "needs_chart": state.get("needs_chart", False),
    }

    if not reasoning["needs_sql"] or reasoning["question_type"] != "analytical":
        message = "The question does not require data analysis. SQL generation was skipped."
        reasoning["message"] = message
        return reasoning, None

    try:
        llm_stage = process_question(text)
    except ValueError as e:
        # 🔴 STRICT MODE: Semantic alignment failure
        # Return clarification request instead of generic result
        error_msg = str(e)
        if "Semantic alignment failure" in error_msg:
            print(f"⚠️ CLARIFICATION REQUIRED: {error_msg}")
            reasoning["message"] = f"Clarification needed: {error_msg}"
            reasoning["requires_clarification"] = True
            reasoning["clarification_reason"] = "semantic_alignment_failure"
            return reasoning, None
        else:
            # Other validation errors
            print(f"❌ {error_msg}")
            reasoning["message"] = f"Analytical stage failed: {error_msg}"
            reasoning["analytical_error"] = error_msg
            return reasoning, None
    except Exception as e:
        # ✅ Show actual error instead of misleading message
        error_msg = f"Analytical stage failed: {str(e)}"
        print(f"❌ {error_msg}")
        reasoning["message"] = error_msg
        reasoning["analytical_error"] = str(e)
        return reasoning, None
    
    if llm_stage.get("error"):
        reasoning["message"] = llm_stage.get("message")
        return reasoning, None

    intent = llm_stage["intent"]
    sql = llm_stage["sql"]
    chart = llm_stage["chart"]
    confidence = llm_stage.get("confidence", 0.5)
    columns = _columns_from_intent(intent)

    llm = {
        "intent": intent,
        "sql": sql,
        "chart": chart,
        "confidence": confidence,
        "columns": columns,
    }

    return reasoning, llm
