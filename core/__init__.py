"""
PhishGuard Core Package
──────────────────────
Contains detection engines, analyzers, scoring, threat intelligence,
user behavioral profiling, and service integrations.
"""

from .phishing_engine import EmailData, Finding, AnalysisReport, analyze_email
from .risk_scorer import generate_report
from .database import init_db, get_connection

__all__ = [
    "EmailData",
    "Finding",
    "AnalysisReport",
    "analyze_email",
    "generate_report",
    "init_db",
    "get_connection",
]

