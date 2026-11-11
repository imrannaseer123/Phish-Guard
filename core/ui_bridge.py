"""
UI Bridge for PhishGuard React + Tailwind Frontend
──────────────────────────────────────────────────
Serializes Flask route contexts into JSON payloads for either:
1. Initial server-hydrated HTML shell (`templates/react_app.html`)
2. Seamless client-side SPA transitions (`X-PhishGuard-SPA: 1`)

Preserves 100% of backend logic, OAuth redirects, and file downloads.
"""

from dataclasses import asdict, is_dataclass
from flask import current_app, get_flashed_messages, jsonify, render_template, request

import config


def _to_json_safe(value):
    """Recursively convert dataclasses and nested objects into JSON-safe structures."""
    if is_dataclass(value) and not isinstance(value, type):
        return _to_json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(k): _to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _is_gmail_authenticated() -> bool:
    """Safely check Gmail OAuth credential status without circular import overhead."""
    try:
        import gmail_auth
        return gmail_auth.get_credentials() is not None
    except Exception:
        return False


def render_ui(page: str, title: str = "PhishGuard", **props):
    """
    Render a React view via SPA JSON response or server-hydrated HTML shell.

    Args:
        page:  Logical React view identifier (e.g. "home", "inbox", "report").
        title: Document title for browser tab.
        props: Route-specific data matching existing backend outputs.
    """
    flashes = [
        {"category": cat, "message": msg}
        for cat, msg in get_flashed_messages(with_categories=True)
    ]

    ascend_active = current_app.config.get("ASCEND_ACTIVE", config.ASCEND_ENABLED)
    chatbot_active = current_app.config.get("CHATBOT_ACTIVE", config.ENABLE_CHATBOT)

    payload = {
        "page": page,
        "path": request.path,
        "title": title,
        "props": _to_json_safe(props),
        "flash": flashes,
        "config": {
            "authenticated": _is_gmail_authenticated(),
            "ENABLE_CHATBOT": bool(chatbot_active),
            "ASCEND_ENABLED": bool(ascend_active),
        },
    }

    if (
        request.headers.get("X-PhishGuard-SPA") == "1"
        or request.args.get("format") == "json"
    ):
        return jsonify(payload)

    return render_template("react_app.html", payload=payload)

