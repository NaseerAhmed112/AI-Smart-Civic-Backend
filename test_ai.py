import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_analyzer import ai_analyzer

TEST_CASES = [
    {
        "name": "Water Pipeline Burst (Critical Safety)",
        "input": "High-pressure water main pipeline burst on 5th Main Road flooding local shops and electrical meters.",
        "expected_category": "Water & Sewage",
        "expected_priority": ["High", "Critical"]
    },
    {
        "name": "Dangerous Pothole (Road Hazard)",
        "input": "Deep crater pothole in the middle of flyover ramp causing two-wheelers to crash.",
        "expected_category": "Roads & Traffic",
        "expected_priority": ["High", "Critical"]
    },
    {
        "name": "Garbage Overflow (Sanitation)",
        "input": "Uncleared community trash bins overflowing with rotting organic waste outside residential colony.",
        "expected_category": "Waste Management",
        "expected_priority": ["Medium", "High"]
    },
    {
        "name": "Transformer Sparking (Power Hazard)",
        "input": "Live electric wire hanging from transformer pole sparking near children's playground.",
        "expected_category": "Electricity & Power",
        "expected_priority": ["Critical"]
    },
    {
        "name": "Stray Dog Pack (Public Health)",
        "input": "Aggressive pack of stray dogs barking and chasing pedestrians in park area.",
        "expected_category": "Public Health",
        "expected_priority": ["Medium", "High"]
    }
]

def run_ai_tests():
    print("=" * 70)
    print("AI SMART CIVIC SERVICES — AUTOMATED AI MODEL ACCURACY TEST SUITE")
    print("=" * 70)
    
    passed = 0
    total = len(TEST_CASES)

    for idx, test in enumerate(TEST_CASES, 1):
        print(f"\n[Test {idx}/{total}]: {test['name']}")
        print(f"   Input: '{test['input']}'")
        
        result = ai_analyzer.analyze(test['input'])
        
        cat_match = result['category'] == test['expected_category']
        prio_match = result['priority'] in test['expected_priority']

        status = "PASSED" if (cat_match and prio_match) else "PARTIAL/WARN"
        if cat_match and prio_match:
            passed += 1

        print(f"   Output Category   : {result['category']} (Expected: {test['expected_category']}) -> {'MATCH' if cat_match else 'DIFF'}")
        print(f"   Output Priority   : {result['priority']} (Expected: {test['expected_priority']}) -> {'MATCH' if prio_match else 'DIFF'}")
        print(f"   Assigned Dept     : {result['assigned_department']}")
        print(f"   AI Executive Summary: {result['ai_summary']}")
        print(f"   AI Confidence     : {result['ai_confidence']}")
        print(f"   Test Result       : [{status}]")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed}/{total} tests fully passed benchmark criteria ({(passed/total)*100:.1f}% accuracy).")
    print("=" * 70)

if __name__ == "__main__":
    run_ai_tests()
