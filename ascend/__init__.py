"""
ascend — Future Enhancement Framework for PhishGuard
═══════════════════════════════════════════════════════
An add-on layer providing explainable, rule-based security
analysis enhancements. All modules are:
  • Read-only (never modify core detection)
  • Deterministic & explainable (no black-box ML)
  • Fail-safe (if disabled, PhishGuard works as before)

Modules:
  1. counterfactual   — "What-if" explanations for risk scores
  2. threat_ontology  — Evidence → Intent → Impact mapping
  3. risk_forecast    — User vulnerability forecasting
  4. psych_analyzer   — Psychological manipulation detection
  5. rule_feedback    — Adaptive rule weight suggestions
  6. incident_reporter— Formal incident report generation
  7. whatif_sandbox   — Interactive weight simulation
"""

__version__ = "1.0.0"
__all__ = [
    "counterfactual",
    "threat_ontology",
    "risk_forecast",
    "psych_analyzer",
    "rule_feedback",
    "incident_reporter",
    "whatif_sandbox",
]
