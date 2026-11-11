"""
PhishGuard — Unified Test Suite Runner
══════════════════════════════════════
Executes all project test suites and displays a unified results report.

Usage:
  python run_tests.py
"""

import os
import sys
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(BASE_DIR, "tests")
PYTHON_EXE = sys.executable

TEST_SUITES = [
    ("Core Detection Pipeline", "test_engine.py"),
    ("ascend Framework (7 modules)", "test_ascend.py"),
    ("Header Forensics & Routing", "test_header_features.py"),
    ("Media (OCR & QR Code)", "test_image_features.py"),
    ("Multilingual Threat Analysis", "test_multilingual.py"),
    ("User Risk Profiling", "test_risk_profiling.py"),
    ("External Threat Intelligence", "test_threat_intel.py"),
    ("AI Chatbot Context Injection", "test_chatbot_context.py"),
]


def run_all_tests():
    print("=" * 70)
    print("  🛡️  PhishGuard Unified Test Suite Runner")
    print("=" * 70)
    print(f"Python interpreter: {PYTHON_EXE}")
    print(f"Test directory:     {TESTS_DIR}\n")

    results = []
    total_start = time.time()

    for title, filename in TEST_SUITES:
        filepath = os.path.join(TESTS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"⚠️  Skipping {title}: {filename} not found.")
            results.append((title, filename, "SKIPPED", 0.0, "File not found"))
            continue

        print(f"\n▶ Running: {title} ({filename})...")
        print("-" * 70)

        start = time.time()
        proc = subprocess.run(
            [PYTHON_EXE, filepath],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        duration = round(time.time() - start, 2)

        # Print suite stdout
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            print(proc.stderr.strip())

        if proc.returncode == 0:
            print(f"  --> ✅ PASSED in {duration}s")
            results.append((title, filename, "PASSED", duration, ""))
        else:
            print(f"  --> ❌ FAILED in {duration}s (exit code {proc.returncode})")
            results.append((title, filename, "FAILED", duration, proc.stderr.strip()))

    total_duration = round(time.time() - total_start, 2)

    print("\n" + "=" * 70)
    print("  📊 TEST EXECUTION SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, _, status, _, _ in results if status == "PASSED")
    failed_count = sum(1 for _, _, status, _, _ in results if status == "FAILED")
    skipped_count = sum(1 for _, _, status, _, _ in results if status == "SKIPPED")

    for title, filename, status, duration, error in results:
        status_icon = "✅ PASS" if status == "PASSED" else ("❌ FAIL" if status == "FAILED" else "⚠️ SKIP")
        print(f"  {status_icon:<8} | {title:<32} | {filename:<24} ({duration}s)")

    print("-" * 70)
    print(f"Total Suites: {len(results)} | Passed: {passed_count} | Failed: {failed_count} | Skipped: {skipped_count}")
    print(f"Total Time:   {total_duration}s")
    print("=" * 70)

    return failed_count == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

