"""
ascend Framework — Standalone Test Suite
════════════════════════════════════════════
Tests all 7 ascend feature modules independently.
Run with: python test_ascend.py

Follows the same testing pattern as test_engine.py.
"""

import sys
import os
import json

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name} — {detail}")
        failed += 1


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: Counterfactual Reasoning
# ═══════════════════════════════════════════════════════════════════════════════

print("\n🔄 Test 1: Counterfactual Reasoning")
print("─" * 50)

from ascend.counterfactual import generate_counterfactuals

findings = [
    {"analyzer": "keyword", "indicator": "phishing_keyword", "score": 15.0, "evidence": "verify", "explanation": "Phishing keyword"},
    {"analyzer": "keyword", "indicator": "credential_request", "score": 10.0, "evidence": "password", "explanation": "Credential request"},
    {"analyzer": "url", "indicator": "shortened_url", "score": 12.0, "evidence": "bit.ly/abc", "explanation": "Shortened URL"},
    {"analyzer": "urgency", "indicator": "urgency_phrase", "score": 8.0, "evidence": "act now", "explanation": "Urgency"},
]

cfs = generate_counterfactuals(45.0, findings)
test("Returns a list", isinstance(cfs, list))
test("Has entries for each category", len(cfs) == 3, f"Got {len(cfs)} instead of 3")
test("Keyword category has correct delta", any(cf["delta"] == 25.0 and cf["category"] == "keyword" for cf in cfs), f"Entries: {cfs}")
test("Each entry has a narrative", all("narrative" in cf for cf in cfs))
test("Hypothetical score is non-negative", all(cf["hypothetical_score"] >= 0 for cf in cfs))
test("Empty findings returns empty list", generate_counterfactuals(50.0, []) == [])


# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Threat Intent Ontology
# ═══════════════════════════════════════════════════════════════════════════════

print("\n🧬 Test 2: Threat Intent Ontology")
print("─" * 50)

from ascend.threat_ontology import build_ontology, get_impact_summary

ontology_findings = [
    {"indicator": "shortened_url", "evidence": "bit.ly/abc", "analyzer": "url"},
    {"indicator": "brand_impersonation", "evidence": "paypal.com", "analyzer": "sender"},
    {"indicator": "unknown_indicator", "evidence": "", "analyzer": ""},  # Should be skipped
]

ontology = build_ontology(ontology_findings)
test("Returns a list", isinstance(ontology, list))
test("Maps known indicators", len(ontology) == 2, f"Got {len(ontology)}")
test("Shortened URL maps to Obfuscation", any(
    e["evidence"] == "shortened_url" and e["chains"][0]["intent"] == "Obfuscation"
    for e in ontology
))
test("Brand impersonation maps to Social Engineering", any(
    e["evidence"] == "brand_impersonation" and e["chains"][0]["intent"] == "Social Engineering"
    for e in ontology
))

summary = get_impact_summary(ontology)
test("Summary has total_chains", summary["total_chains"] == 2, f"Got {summary['total_chains']}")
test("Summary has unique_intents", len(summary["unique_intents"]) == 2)
test("Summary has narrative", "threat chain" in summary["risk_narrative"])
test("Empty input returns empty summary", get_impact_summary([])["total_chains"] == 0)


# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: Human Risk Forecasting
# ═══════════════════════════════════════════════════════════════════════════════

print("\n📊 Test 3: Human Risk Forecasting")
print("─" * 50)

from ascend.risk_forecast import compute_risk_forecast

# Simulate history (most recent first)
high_risk_history = [
    {"risk_score": 85}, {"risk_score": 78}, {"risk_score": 92},
    {"risk_score": 71}, {"risk_score": 80}, {"risk_score": 88},
]

low_risk_history = [
    {"risk_score": 15}, {"risk_score": 22}, {"risk_score": 18},
    {"risk_score": 10}, {"risk_score": 12}, {"risk_score": 20},
]

forecast_high = compute_risk_forecast(high_risk_history)
test("High-risk history yields High vulnerability", forecast_high["vulnerability_level"] == "High",
     f"Got {forecast_high['vulnerability_level']}")
test("Has confidence explanation", len(forecast_high["confidence_explanation"]) > 0)
test("Has stats", forecast_high["stats"]["total_analyses"] == 6)

forecast_low = compute_risk_forecast(low_risk_history)
test("Low-risk history yields Low vulnerability", forecast_low["vulnerability_level"] == "Low",
     f"Got {forecast_low['vulnerability_level']}")

forecast_empty = compute_risk_forecast([])
test("Empty history returns Unknown", forecast_empty["vulnerability_level"] == "Unknown")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Psychological Manipulation Analyzer
# ═══════════════════════════════════════════════════════════════════════════════

print("\n🧠 Test 4: Psychological Manipulation Analyzer")
print("─" * 50)

from ascend.psych_analyzer import analyze_manipulation

result = analyze_manipulation(
    "URGENT: Your account will be closed",
    "Dear Customer, act now to verify your account. Your account has been compromised. "
    "Click here to claim your prize. This is an official notice from the security team."
)

test("Returns enabled=True", result["enabled"] == True)
test("Detects fear", result["categories"]["fear"]["intensity"] > 0)
test("Detects urgency", result["categories"]["urgency"]["intensity"] > 0)
test("Detects reward", result["categories"]["reward"]["intensity"] > 0)
test("Detects authority", result["categories"]["authority"]["intensity"] > 0)
test("Overall level is not None", result["overall_level"] != "None")
test("Has dominant type", result["dominant_type"] is not None)
test("Has narrative", len(result["narrative"]) > 0)

clean_result = analyze_manipulation("Meeting tomorrow", "See you at the conference.")
test("Clean email has None level", clean_result["overall_level"] == "None")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: Adaptive Rule Feedback Loop
# ═══════════════════════════════════════════════════════════════════════════════

print("\n🔁 Test 5: Adaptive Rule Feedback Loop")
print("─" * 50)

from ascend.rule_feedback import (
    init_rule_feedback_db, submit_rule_feedback,
    get_rule_feedback, compute_weight_suggestions,
)

# DB table created on import — just verify operations work
test_msg_id = "__test_ascend_feedback__"
success = submit_rule_feedback(
    message_id=test_msg_id,
    feedback_type="helpful",
    risk_score=75.0,
    risk_level="High",
    triggered_rules=["keyword", "url"],
)
test("Submit feedback succeeds", success)

retrieved = get_rule_feedback(test_msg_id)
test("Retrieve feedback works", retrieved is not None)
test("Feedback type is correct", retrieved["feedback_type"] == "helpful")
test("Triggered rules preserved", retrieved["triggered_rules"] == ["keyword", "url"])

# Update feedback
submit_rule_feedback(test_msg_id, "false_alarm", 75.0, "High", ["keyword", "url"])
updated = get_rule_feedback(test_msg_id)
test("Feedback update works", updated["feedback_type"] == "false_alarm")

suggestions = compute_weight_suggestions()
test("Suggestions returns a dict", isinstance(suggestions, dict))
test("Has total_feedback count", "total_feedback" in suggestions)

# Clean up test data
import sqlite3
import config
conn = sqlite3.connect(config.DATABASE_PATH)
conn.execute("DELETE FROM ascend_rule_feedback WHERE message_id = ?", (test_msg_id,))
conn.commit()
conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Test 6: Autonomous Incident Reporter
# ═══════════════════════════════════════════════════════════════════════════════

print("\n📋 Test 6: Autonomous Incident Reporter")
print("─" * 50)

from ascend.incident_reporter import (
    should_generate_report, generate_incident_report, export_as_text,
)

test("Score 85 triggers report", should_generate_report(85.0))
test("Score 50 does NOT trigger", not should_generate_report(50.0))
test("Score 80 triggers report (boundary)", should_generate_report(80.0))

report = generate_incident_report(
    email_meta={"id": "msg123", "subject": "Test Phishing", "sender": "bad@evil.com", "date": "2026-01-01"},
    risk_score=85.0,
    risk_level="High",
    intent="Credential Harvesting",
    findings=[
        {"analyzer": "keyword", "indicator": "phishing_keyword", "score": 15.0, "evidence": "verify", "explanation": "Phishing keyword"},
    ],
    ontology_data=[
        {"evidence": "phishing_keyword", "chains": [{"intent": "Social Engineering", "impact": "Credential Theft"}]}
    ],
    summary="High-risk phishing email detected.",
)
test("Report has report_id", report["report_id"].startswith("IR-"))
test("Report has executive_summary", len(report["executive_summary"]) > 0)
test("Report has evidence list", len(report["evidence"]) == 1)
test("Report has threat_chains", len(report["threat_chains"]) == 1)
test("Report has mitigations", len(report["mitigations"]) > 0)
test("Report has disclaimer", "advisory" in report["disclaimer"])

text = export_as_text(report)
test("Text export is non-empty", len(text) > 100)
test("Text export has header", "PHISHING INCIDENT REPORT" in text)
test("Text export has evidence", "phishing_keyword" in text)


# ═══════════════════════════════════════════════════════════════════════════════
# Test 7: What-If Sandbox
# ═══════════════════════════════════════════════════════════════════════════════

print("\n🎛️ Test 7: What-If Sandbox")
print("─" * 50)

from ascend.whatif_sandbox import simulate_risk_score, get_default_weights

sandbox_findings = [
    {"analyzer": "keyword", "score": 15.0},
    {"analyzer": "url", "score": 10.0},
    {"analyzer": "urgency", "score": 8.0},
]
default_w = {"keyword": 25, "url": 20, "urgency": 15}
custom_w = {"keyword": 30, "url": 10, "urgency": 15}

result = simulate_risk_score(sandbox_findings, custom_w, default_w)
test("Mode is Educational Simulation", result["mode"] == "Educational Simulation")
test("Original score calculated", result["original_score"] > 0)
test("Simulated score calculated", result["simulated_score"] > 0)
test("Delta is a number", isinstance(result["delta"], float))
test("Has analyzer_breakdown", len(result["analyzer_breakdown"]) > 0)
test("Has explanation", len(result["explanation"]) > 0)

# Verify that increasing a weight increases score
test("Keyword increase → higher contribution",
     result["analyzer_breakdown"]["keyword"]["simulated_contribution"] >=
     result["analyzer_breakdown"]["keyword"]["original_contribution"])

weights = get_default_weights()
test("Default weights returned", len(weights) > 0)


# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 50)
total = passed + failed
print(f"  Results: {passed}/{total} passed, {failed}/{total} failed")
if failed == 0:
    print("  ✅ All ascend tests passed!")
else:
    print(f"  ❌ {failed} test(s) failed!")
print("═" * 50)

sys.exit(0 if failed == 0 else 1)
