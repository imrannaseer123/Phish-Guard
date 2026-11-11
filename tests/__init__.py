"""
PhishGuard Test Suite Package
"""
import os
import sys

# Ensure root and core are in sys.path when test package is imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
import config  # registers core/ in sys.path

