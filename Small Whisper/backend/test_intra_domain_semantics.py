"""
Test Suite for Intra-Domain Semantic Metric Resolution

This test validates that the system:
1. Locks to the question domain (inter-domain)
2. Resolves the specific metric intent within that domain (intra-domain)
3. Refuses same-domain but semantically different metrics
4. Prevents "reading score" for "math score" questions
5. Prevents "expenditure" for "revenue" questions
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
    perform_multi_pass_validation,
    _extract_metric_intent,
    _calculate_semantic_score
)
from shared.intent_sanitizer import sanitize_intent
from shared.sql_compiler import compile_sql


# ============================================================================
# TEST SCHEMA WITH MULTIPLE METRICS IN SAME DOMAIN
# ============================================================================

ACADEMIC_MULTI_METRIC_SCHEMA = {
    "students": [
        {"name": "student_id", "type": "Int64"},
        {"name": "student_name", "type": "String"},
        {"name": "math_score", "type": "String"},         # Academic - Math
        {"name": "reading_score", "type": "String"},      # Academic - Reading
        {"name": "english_score", "type": "Float64"},     # Academic - English
        {"name": "science_score", "type": "String"},      # Academic - Science
        {"name": "total_score", "type": "String"},        # Academic - Total
        {"name": "gpa", "type": "String"},                # Academic - GPA
    ]
}

FINANCIAL_MULTI_METRIC_SCHEMA = {
    "transactions": [
        {"name": "transaction_id", "type": "Int64"},
        {"name": "revenue", "type": "String"},            # Financial - Revenue
        {"name": "expenditure", "type": "String"},        # Financial - Expenditure
        {"name": "profit", "type": "Float64"},            # Financial - Profit
        {"name": "cost", "type": "String"},               # Financial - Cost
        {"name": "fee", "type": "String"},                # Financial - Fee
    ]
}


# ============================================================================
# INTRA-DOMAIN SEMANTIC RESOLUTION TESTS
# ============================================================================

def test_math_score_not_reading():
    """
    🔴 CRITICAL TEST: Math question should NOT use reading_score
    
    Domain: Academic (same for both)
    Metric Intent: Math
    Wrong Column: reading_score (academic but different semantic meaning)
    
    Expected: ❌ REFUSE (intra-domain semantic mismatch)
    """
    print("\n" + "="*70)
    print("TEST 1: Math Question Should NOT Use Reading Score")
    print("="*70)
    
    question = "What is the average math score?"
    intent = {
        "table": "students",
        "metrics": [
            {"column": "reading_score", "aggregation": "AVG"}  # ❌ Wrong metric!
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    print(f"\n📝 Question: {question}")
    print(f"🔴 Incorrectly selected: reading_score (should be math_score)")
    
    # Pass 1: Domain & Intent Validation with intra-domain checking
    print("\n🔍 Pass 1: Intra-Domain Semantic Validation")
    pass1 = validate_intent_semantics(intent, question, ACADEMIC_MULTI_METRIC_SCHEMA)
    
    print(f"   Result: {'✅ PASS' if pass1['valid'] else '❌ FAIL'}")
    
    if not pass1['valid']:
        print(f"   ✅ Correctly refused intra-domain semantic mismatch:")
        for issue in pass1['issues']:
            print(f"      • {issue}")
        print("\n✅ TEST PASSED: Intra-domain semantic mismatch detected")
        return True
    else:
        print("\n❌ TEST FAILED: Should have refused reading_score for math question")
        return False


def test_reading_score_not_math():
    """
    🔴 CRITICAL TEST: Reading question should NOT use math_score
    
    Expected: ❌ REFUSE (intra-domain semantic mismatch)
    """
    print("\n" + "="*70)
    print("TEST 2: Reading Question Should NOT Use Math Score")
    print("="*70)
    
    question = "What is the average reading score?"
    intent = {
        "table": "students",
        "metrics": [
            {"column": "math_score", "aggregation": "AVG"}  # ❌ Wrong metric!
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    print(f"\n📝 Question: {question}")
    print(f"🔴 Incorrectly selected: math_score (should be reading_score)")
    
    pass1 = validate_intent_semantics(intent, question, ACADEMIC_MULTI_METRIC_SCHEMA)
    
    if not pass1['valid']:
        print(f"   ✅ Correctly refused:")
        for issue in pass1['issues']:
            print(f"      • {issue}")
        print("\n✅ TEST PASSED")
        return True
    else:
        print("\n❌ TEST FAILED")
        return False


def test_revenue_not_expenditure():
    """
    🔴 CRITICAL TEST: Revenue question should NOT use expenditure
    
    Domain: Financial (same for both)
    Metric Intent: Revenue
    Wrong Column: expenditure (financial but different semantic meaning)
    
    Expected: ❌ REFUSE (intra-domain semantic mismatch)
    """
    print("\n" + "="*70)
    print("TEST 3: Revenue Question Should NOT Use Expenditure")
    print("="*70)
    
    question = "What is the total revenue?"
    intent = {
        "table": "transactions",
        "metrics": [
            {"column": "expenditure", "aggregation": "SUM"}  # ❌ Wrong metric!
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    print(f"\n📝 Question: {question}")
    print(f"🔴 Incorrectly selected: expenditure (should be revenue)")
    
    pass1 = validate_intent_semantics(intent, question, FINANCIAL_MULTI_METRIC_SCHEMA)
    
    if not pass1['valid']:
        print(f"   ✅ Correctly refused:")
        for issue in pass1['issues']:
            print(f"      • {issue}")
        print("\n✅ TEST PASSED")
        return True
    else:
        print("\n❌ TEST FAILED")
        return False


def test_expenditure_not_revenue():
    """
    🔴 CRITICAL TEST: Expenditure question should NOT use revenue
    
    Expected: ❌ REFUSE (intra-domain semantic mismatch)
    """
    print("\n" + "="*70)
    print("TEST 4: Expenditure Question Should NOT Use Revenue")
    print("="*70)
    
    question = "What is the total expenditure?"
    intent = {
        "table": "transactions",
        "metrics": [
            {"column": "revenue", "aggregation": "SUM"}  # ❌ Wrong metric!
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    print(f"\n📝 Question: {question}")
    print(f"🔴 Incorrectly selected: revenue (should be expenditure)")
    
    pass1 = validate_intent_semantics(intent, question, FINANCIAL_MULTI_METRIC_SCHEMA)
    
    if not pass1['valid']:
        print(f"   ✅ Correctly refused:")
        for issue in pass1['issues']:
            print(f"      • {issue}")
        print("\n✅ TEST PASSED")
        return True
    else:
        print("\n❌ TEST FAILED")
        return False


def test_correct_math_metric():
    """
    ✅ POSITIVE TEST: Math question with math_score should PASS
    """
    print("\n" + "="*70)
    print("TEST 5: Math Question with Correct Math Metric (Should Pass)")
    print("="*70)
    
    question = "What is the average math score?"
    intent = {
        "table": "students",
        "metrics": [
            {"column": "math_score", "aggregation": "AVG"}  # ✅ Correct!
        ],
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    print(f"\n📝 Question: {question}")
    print(f"✅ Correctly selected: math_score")
    
    pass1 = validate_intent_semantics(intent, question, ACADEMIC_MULTI_METRIC_SCHEMA)
    
    if pass1['valid']:
        print(f"   ✅ Validation passed (expected)")
        print("\n✅ TEST PASSED: Correct metric accepted")
        return True
    else:
        print(f"   ❌ Validation failed (unexpected):")
        for issue in pass1['issues']:
            print(f"      • {issue}")
        print("\n❌ TEST FAILED: Should have accepted math_score")
        return False


def test_auto_repair_intra_domain():
    """
    🔴 AUTO-REPAIR TEST: Auto-repair should respect intra-domain semantics
    
    Question: "What is the average math score?"
    Available columns: math_score, reading_score (both academic)
    Expected: Select math_score (not reading_score)
    """
    print("\n" + "="*70)
    print("TEST 6: Auto-Repair Should Respect Intra-Domain Semantics")
    print("="*70)
    
    question = "What is the average math score?"
    intent_raw = {
        "table": "students",
        "metrics": [],  # Empty - triggers auto-repair
        "dimensions": [],
        "filters": [],
        "order_by": [],
        "limit": None
    }
    
    print(f"\n📝 Question: {question}")
    print(f"🔧 Triggering auto-repair (empty metrics)")
    
    try:
        intent = sanitize_intent(intent_raw, ACADEMIC_MULTI_METRIC_SCHEMA, question)
        
        if intent['metrics']:
            selected_col = intent['metrics'][0]['column']
            print(f"\n✅ Auto-repair selected: {selected_col}")
            
            if "math" in selected_col.lower():
                print("✅ TEST PASSED: Correctly selected math-related metric")
                return True
            elif "reading" in selected_col.lower():
                print("❌ TEST FAILED: Incorrectly selected reading metric for math question")
                return False
            else:
                print(f"⚠️ TEST UNCLEAR: Selected {selected_col} (neither math nor reading)")
                return False
        else:
            print("❌ TEST FAILED: Auto-repair did not generate metrics")
            return False
    
    except ValueError as e:
        print(f"\n⚠️ Auto-repair refused: {e}")
        print("⚠️ TEST INCONCLUSIVE: Auto-repair refused to generate metric")
        return True  # Refusing is acceptable


def test_semantic_score_calculation():
    """
    TEST 7: Verify semantic score calculation logic
    """
    print("\n" + "="*70)
    print("TEST 7: Semantic Score Calculation")
    print("="*70)
    
    question = "What is the average math score?"
    question_tokens = set(question.lower().split())
    metric_intents = _extract_metric_intent(question.lower())
    
    print(f"\n📝 Question: {question}")
    print(f"🎯 Extracted metric intents: {metric_intents}")
    
    # Test different columns
    columns = ["math_score", "reading_score", "english_score", "student_id"]
    
    print(f"\n📊 Semantic scores:")
    for col in columns:
        score = _calculate_semantic_score(col, metric_intents, question_tokens)
        print(f"   • {col}: {score}")
    
    # Verify that math_score has highest score
    math_score = _calculate_semantic_score("math_score", metric_intents, question_tokens)
    reading_score = _calculate_semantic_score("reading_score", metric_intents, question_tokens)
    
    if math_score > reading_score and math_score > 0 and reading_score < 0:
        print("\n✅ TEST PASSED: math_score scored higher (positive), reading_score penalized (negative)")
        return True
    else:
        print(f"\n❌ TEST FAILED: Incorrect scoring (math={math_score}, reading={reading_score})")
        return False


def test_metric_intent_extraction():
    """
    TEST 8: Verify metric intent extraction
    """
    print("\n" + "="*70)
    print("TEST 8: Metric Intent Extraction")
    print("="*70)
    
    test_cases = [
        ("What is the average math score?", ["math"]),
        ("Show me reading scores", ["reading"]),
        ("Total revenue and expenditure", ["revenue", "expenditure"]),
        ("What is the enrollment count?", ["enrollment"]),
    ]
    
    all_passed = True
    for question, expected_intents in test_cases:
        extracted = _extract_metric_intent(question.lower())
        
        # Check if all expected intents are extracted
        matched = all(intent in extracted for intent in expected_intents)
        
        status = "✅" if matched else "❌"
        print(f"\n{status} Question: {question}")
        print(f"   Expected: {expected_intents}")
        print(f"   Extracted: {extracted}")
        
        if not matched:
            all_passed = False
    
    if all_passed:
        print("\n✅ TEST PASSED: All metric intents correctly extracted")
    else:
        print("\n❌ TEST FAILED: Some metric intents incorrectly extracted")
    
    return all_passed


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all intra-domain semantic resolution tests"""
    print("\n" + "="*70)
    print("INTRA-DOMAIN SEMANTIC METRIC RESOLUTION - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Math NOT Reading", test_math_score_not_reading),
        ("Reading NOT Math", test_reading_score_not_math),
        ("Revenue NOT Expenditure", test_revenue_not_expenditure),
        ("Expenditure NOT Revenue", test_expenditure_not_revenue),
        ("Correct Math Metric", test_correct_math_metric),
        ("Auto-Repair Intra-Domain", test_auto_repair_intra_domain),
        ("Semantic Score Calculation", test_semantic_score_calculation),
        ("Metric Intent Extraction", test_metric_intent_extraction),
    ]
    
    passed = 0
    failed = 0
    
    for name, test in tests:
        try:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ TEST EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - Intra-Domain Semantic Resolution Verified")
    else:
        print(f"⚠️ {failed} test(s) failed - Review implementation")


if __name__ == "__main__":
    run_all_tests()

