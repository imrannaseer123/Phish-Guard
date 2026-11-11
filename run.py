"""
PhishGuard — Application Runner
═══════════════════════════════
Entry point script to start the PhishGuard Flask web application.

Usage:
  python run.py [--port 5000] [--host 127.0.0.1] [--no-debug]
"""

import argparse
import os
import sys

# Ensure project root and core are in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config
import database
from app import app


def main():
    parser = argparse.ArgumentParser(description="Run PhishGuard Web Application")
    parser.add_argument("--port", type=int, default=config.PORT, help=f"Port to bind (default: {config.PORT})")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug mode")
    args = parser.parse_args()

    # Ensure database is initialized
    database.init_db()

    use_debug = False if args.no_debug else config.DEBUG

    print("=" * 65)
    print("  🛡️  PhishGuard — Phishing Email Risk Analyzer")
    print("=" * 65)
    print(f"  • Environment:  {'Development (Debug)' if use_debug else 'Production'}")
    print(f"  • Database:     {config.DATABASE_PATH}")
    print(f"  • ascend:       {'Enabled' if config.ASCEND_ENABLED else 'Disabled'}")
    print(f"  • Chatbot:      {'Enabled' if config.ENABLE_CHATBOT else 'Disabled'}")
    print(f"  • URL:          http://{args.host}:{args.port}")
    print("=" * 65)
    print("Press CTRL+C to stop the server.\n")

    app.run(host=args.host, port=args.port, debug=use_debug)


if __name__ == "__main__":
    main()

