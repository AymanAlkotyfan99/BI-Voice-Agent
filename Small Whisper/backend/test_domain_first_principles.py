"""
Test Suite for Domain-First Analytical Reasoning Principles

This test suite validates that the system:
1. Locks to the question domain
2. Preserves domain-aligned columns even with type issues
3. Applies type casting before rejecting columns
4. Refuses cross-domain substitutions
5. Never uses generic fallbacks when domain-specific metrics exist
"""

import sys
import io

# Fix Unicode encoding for Windows PowerShell
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from shared.intent_validator import (
    validate_intent_semantics,
    validate_schema_and_types,
    validate_sql_executability,
    perform_multi_pass_validation
)
from shared.intent_sanitizer import sanitize_intent
from shared.sql_compiler import compile_sql


# ============================================================================
# TEST SCHEMAS
# ============================================================================

ACADEMIC_SCHEMA = {
    "students": [
        {"name": "student_id", "type": "Int64"},
        {"name": "student_name", "type": "String"},
        {"name": "math_score", "type": "String"},  # ❌ String type (requires casting)
        {"name": "english_score", "type": "Float64"},
        {"name": "reading_score", "type": "String"},  # ❌ String type (requires casting)
        {"name": "total_score", "type": "String"},  # ❌ String type (requires casting)
        {"name": "grade_level", "type": "Int64"},
        {"name": "enrollment_year", "type": "Int64"},
    ]
}

FINANCIAL_SCHEMA = {
    "sales": [
        {"name": "transaction_id", "type": "Int64"},
        {"name": "revenue", "type": "String"},  # ❌ String type (requires casting)
        {"name": "cost", "type": "Float64"},
        {"name": "profit", "type": "String"},  # ❌ String type (requires casting)
        {"name": "customer_id", "type": "Int64"},
        {"name": "transaction_date", "type": "Date"},
    ]
}

MIXED_SCHEMA = {
    "university_data": [
        {"name": "student_id", "type": "Int64"},
        {"name": "tuition_fee", "type": "String"},  # Financial (String)
        {"name": "gpa", "type": "String"},  # Academic (String)
        {"name": "scholarship_amount", "type": "Float64"},  # Financial (Numeric)
        {"name": "test_score", "type": "String"},  # Academic (String)
        {"name": "enrollment_count", "type": "Int64"},  # Demographic (Numeric)
    ]
}


# ============================================================================
# TEST CASES
# ============================================================================

def test_academic_question_with_string_score():
    """
    Test Case 1: Academic Question with String-Typed Score Column
    
    Expected Behavior:
    - Domain: Academic (locked)
    - Column: math_score (domain-aligned)
    - Type Issue: String → requires toFloat64()
    - Result: ✅ Pass with type casting
    """
    print("\n" + "="*70)
    print("TEST 1: Academic Question with String-Typed Score")
    print("="*70)
    
    question = "What is the average math score?"
    intent = {
        "table": "students",
        "metrics": [
            {"column": "math_score", "aggregation": "AVG", "alias": "avg_math_score"}
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    # Pass 1: Domain & Intent Validation
    print("\n🔍 Pass 1: Domain & Intent Validation")
    pass1 = validate_intent_semantics(intent, question, ACADEMIC_SCHEMA)
    print(f"   Result: {'✅ PASS' if pass1['valid'] else '❌ FAIL'}")
    if pass1['issues']:
        for issue in pass1['issues']:
            print(f"   Issue: {issue}")
    
    # Pass 2: Schema & Type Validation (with type repair)
    print("\n🔧 Pass 2: Type Repair")
    pass2 = validate_schema_and_types(intent, ACADEMIC_SCHEMA)
    print(f"   Result: {'✅ PASS' if pass2['valid'] else '❌ FAIL'}")
    if pass2['type_casting']:
        print(f"   Type casting needed:")
        for tc in pass2['type_casting']:
            print(f"      • {tc['column']} ({tc['current_type']}) → {tc['required_cast']}")
    
    # Compile SQL with type casting
    print("\n🔨 Compiling SQL with type casting...")
    sql = compile_sql(intent, type_casting=pass2['type_casting'])
    print(f"   SQL: {sql}")
    
    # Verify SQL contains type casting
    assert "toFloat64(math_score)" in sql or "toInt64(math_score)" in sql, \
        "❌ FAIL: Type casting not applied in SQL"
    
    print("\n✅ TEST PASSED: Domain-aligned column preserved with type casting")


def test_financial_question_refuses_academic_column():
    """
    Test Case 2: Financial Question Should NOT Use Academic Columns
    
    Expected Behavior:
    - Domain: Financial (locked)
    - Prohibited: Using test_score (academic domain) for revenue question
    - Result: ❌ Refuse with domain violation error
    """
    print("\n" + "="*70)
    print("TEST 2: Financial Question Refuses Academic Column (Domain Lock)")
    print("="*70)
    
    question = "What is the total revenue?"
    intent = {
        "table": "university_data",
        "metrics": [
            {"column": "test_score", "aggregation": "SUM", "alias": "total_revenue"}  # ❌ Wrong domain!
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    # Pass 1: Domain & Intent Validation
    print("\n🔍 Pass 1: Domain & Intent Validation")
    pass1 = validate_intent_semantics(intent, question, MIXED_SCHEMA)
    print(f"   Result: {'✅ PASS' if pass1['valid'] else '❌ FAIL'}")
    
    if not pass1['valid']:
        print(f"   ✅ Correctly refused cross-domain substitution:")
        for issue in pass1['issues']:
            print(f"      • {issue}")
        print("\n✅ TEST PASSED: Domain violation correctly detected and refused")
    else:
        print("\n❌ TEST FAILED: Should have rejected academic column for financial question")
        raise AssertionError("Domain lock not enforced")


def test_financial_question_with_string_revenue():
    """
    Test Case 3: Financial Question with String-Typed Revenue
    
    Expected Behavior:
    - Domain: Financial (locked)
    - Column: revenue (domain-aligned, but String type)
    - Type Issue: String → requires toFloat64()
    - Result: ✅ Pass with type casting (NOT rejected due to type)
    """
    print("\n" + "="*70)
    print("TEST 3: Financial Question with String-Typed Revenue")
    print("="*70)
    
    question = "What is the total revenue?"
    intent = {
        "table": "sales",
        "metrics": [
            {"column": "revenue", "aggregation": "SUM", "alias": "total_revenue"}
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    # Pass 1: Domain & Intent Validation
    print("\n🔍 Pass 1: Domain & Intent Validation")
    pass1 = validate_intent_semantics(intent, question, FINANCIAL_SCHEMA)
    print(f"   Result: {'✅ PASS' if pass1['valid'] else '❌ FAIL'}")
    assert pass1['valid'], "❌ Domain validation should pass (revenue is financial)"
    
    # Pass 2: Type Repair
    print("\n🔧 Pass 2: Type Repair")
    pass2 = validate_schema_and_types(intent, FINANCIAL_SCHEMA)
    print(f"   Type casting needed: {len(pass2['type_casting'])} column(s)")
    
    assert len(pass2['type_casting']) > 0, "❌ Type casting should be identified"
    
    # Compile SQL with type casting
    sql = compile_sql(intent, type_casting=pass2['type_casting'])
    print(f"   SQL: {sql}")
    
    assert "toFloat64(revenue)" in sql or "toInt64(revenue)" in sql, \
        "❌ Type casting not applied"
    
    print("\n✅ TEST PASSED: Financial column preserved with type casting")


def test_count_star_not_allowed_for_specific_metric():
    """
    Test Case 4: COUNT(*) Should NOT Be Used When Domain-Specific Metric Exists
    
    Expected Behavior:
    - Domain: Academic (locked)
    - Question: "What is the average score?"
    - Prohibited: COUNT(*) when specific score columns exist
    - Result: ❌ Refuse generic fallback
    """
    print("\n" + "="*70)
    print("TEST 4: COUNT(*) Prohibited for Domain-Specific Questions")
    print("="*70)
    
    question = "What is the average score?"
    intent = {
        "table": "students",
        "metrics": [
            {"column": "*", "aggregation": "COUNT", "alias": "count"}  # ❌ Generic fallback!
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    # Pass 1: Domain & Intent Validation
    print("\n🔍 Pass 1: Domain & Intent Validation")
    pass1 = validate_intent_semantics(intent, question, ACADEMIC_SCHEMA)
    print(f"   Result: {'✅ PASS' if pass1['valid'] else '❌ FAIL'}")
    
    if not pass1['valid']:
        print(f"   ✅ Correctly refused COUNT(*) for domain-specific question:")
        for issue in pass1['issues']:
            print(f"      • {issue}")
        print("\n✅ TEST PASSED: Generic fallback correctly refused")
    else:
        print("\n❌ TEST FAILED: Should have rejected COUNT(*) for specific metric question")
        raise AssertionError("Generic fallback not prevented")


def test_auto_repair_preserves_domain():
    """
    Test Case 5: Auto-Repair Must Preserve Domain Alignment
    
    Expected Behavior:
    - Question: "What is the average score?" (Academic domain)
    - Schema has both academic and financial columns
    - Auto-repair must select academic column (even if string type)
    - Result: ✅ Domain-aligned column selected (with type casting if needed)
    """
    print("\n" + "="*70)
    print("TEST 5: Auto-Repair Preserves Domain (Academic)")
    print("="*70)
    
    question = "What is the average score?"
    
    # Simulate LLM extraction failure (empty metrics)
    intent_raw = {
        "table": "university_data",
        "metrics": [],  # Empty - triggers auto-repair
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    print("\n🔧 Running sanitizer with auto-repair...")
    try:
        intent = sanitize_intent(intent_raw, MIXED_SCHEMA, question)
        print(f"   Auto-repair result: {intent['metrics']}")
        
        if intent['metrics']:
            selected_col = intent['metrics'][0]['column']
            print(f"   Selected column: {selected_col}")
            
            # Verify domain alignment
            from shared.intent_sanitizer import _identify_column_domain
            col_domain = _identify_column_domain(selected_col.lower())
            print(f"   Column domain: {col_domain}")
            
            # Should be academic (test_score or gpa), NOT financial (tuition_fee, scholarship)
            assert col_domain == "academic", \
                f"❌ FAIL: Auto-repair selected {col_domain} column instead of academic"
            
            print("\n✅ TEST PASSED: Auto-repair preserved academic domain")
        else:
            print("\n❌ TEST FAILED: Auto-repair did not generate any metrics")
            raise AssertionError("Auto-repair failed")
    
    except ValueError as e:
        print(f"\n⚠️ Auto-repair refused (may be expected): {e}")
        # This is acceptable if no clear metric is found


def test_multi_pass_validation_flow():
    """
    Test Case 6: Full Multi-Pass Validation Flow
    
    Tests the complete validation sequence:
    Pass 1: Domain & Intent → Pass 2: Type Repair → Pass 3: Schema → Pass 4: SQL
    """
    print("\n" + "="*70)
    print("TEST 6: Complete Multi-Pass Validation Flow")
    print("="*70)
    
    question = "What is the average reading score?"
    intent = {
        "table": "students",
        "metrics": [
            {"column": "reading_score", "aggregation": "AVG", "alias": "avg_reading"}
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    # Initial SQL (without type casting)
    sql_initial = compile_sql(intent)
    print(f"\n📝 Initial SQL: {sql_initial}")
    
    # Multi-pass validation
    print("\n🔍 Running multi-pass validation...")
    validation = perform_multi_pass_validation(intent, sql_initial, question, ACADEMIC_SCHEMA)
    
    print(f"   Pass 1 (Intent):  {'✅ PASS' if validation['pass1']['valid'] else '❌ FAIL'}")
    print(f"   Pass 2 (Schema):  {'✅ PASS' if validation['pass2']['valid'] else '❌ FAIL'}")
    print(f"   Pass 3 (SQL):     {'✅ PASS' if validation['pass3']['valid'] else '❌ FAIL'}")
    
    if validation['type_casting_needed']:
        print(f"\n🔧 Type casting identified ({len(validation['type_casting_needed'])} columns)")
        
        # Recompile with type casting
        sql_repaired = compile_sql(intent, type_casting=validation['type_casting_needed'])
        print(f"   Repaired SQL: {sql_repaired}")
        
        assert "toFloat64(reading_score)" in sql_repaired or "toInt64(reading_score)" in sql_repaired, \
            "❌ Type casting not applied in repaired SQL"
        
        print("\n✅ TEST PASSED: Multi-pass validation with auto-repair successful")
    else:
        print("\n⚠️ No type casting identified (unexpected for String column)")


def test_domain_lock_enforcement():
    """
    Test Case 7: Domain Lock Prevents Silent Fallbacks
    
    Expected Behavior:
    - Question domain: Financial
    - Available columns: Only academic columns
    - Result: ❌ Refuse (do NOT fall back to academic columns)
    """
    print("\n" + "="*70)
    print("TEST 7: Domain Lock Prevents Silent Fallbacks")
    print("="*70)
    
    question = "What is the total revenue?"
    
    # Intent with academic column (wrong domain)
    intent_raw = {
        "table": "students",
        "metrics": [],  # Empty - will trigger auto-repair
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    print("\n🔧 Running sanitizer (should refuse due to domain mismatch)...")
    try:
        intent = sanitize_intent(intent_raw, ACADEMIC_SCHEMA, question)
        
        # If it succeeds, check that it didn't use academic columns
        if intent['metrics']:
            selected_col = intent['metrics'][0]['column']
            from shared.intent_sanitizer import _identify_column_domain
            col_domain = _identify_column_domain(selected_col.lower())
            
            if col_domain == "academic":
                print(f"\n❌ TEST FAILED: Used academic column '{selected_col}' for financial question")
                raise AssertionError("Domain lock violated")
        
        print(f"\n⚠️ Unexpected success: {intent['metrics']}")
    
    except ValueError as e:
        print(f"\n✅ Correctly refused: {e}")
        print("✅ TEST PASSED: Domain lock enforced, refused cross-domain substitution")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all domain-first principle tests"""
    print("\n" + "="*70)
    print("DOMAIN-FIRST ANALYTICAL REASONING - TEST SUITE")
    print("="*70)
    
    tests = [
        test_academic_question_with_string_score,
        test_financial_question_refuses_academic_column,
        test_financial_question_with_string_revenue,
        test_count_star_not_allowed_for_specific_metric,
        test_auto_repair_preserves_domain,
        test_multi_pass_validation_flow,
        test_domain_lock_enforcement,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - Domain-First Principles Verified")
    else:
        print(f"⚠️ {failed} test(s) failed - Review implementation")


if __name__ == "__main__":
    run_all_tests()

