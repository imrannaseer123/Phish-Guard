"""
Gmail OAuth Authentication Module
─────────────────────────────────
Handles Google OAuth 2.0 flow for Flask web application.
Uses read-only Gmail scope for privacy.
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

import config


def get_flow(redirect_uri: str) -> Flow:
    """
    Create an OAuth 2.0 flow instance for the web application.
    Requires credentials.json to be present in the project root.
    """
    if not os.path.exists(config.CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"credentials.json not found at {config.CREDENTIALS_FILE}. "
            f"Please download it from Google Cloud Console. "
            f"See README.md for instructions."
        )

    flow = Flow.from_client_secrets_file(
        config.CREDENTIALS_FILE,
        scopes=config.GMAIL_SCOPES,
        redirect_uri=redirect_uri,
    )
    return flow


def get_credentials() -> Credentials | None:
    """
    Load stored credentials from token.json.
    Returns None if no valid credentials exist.
    """
    if not os.path.exists(config.TOKEN_FILE):
        return None

    creds = Credentials.from_authorized_user_file(
        config.TOKEN_FILE, config.GMAIL_SCOPES
    )

    # Refresh expired credentials
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_credentials(creds)
        except Exception:
            # Token is invalid, need re-auth
            os.remove(config.TOKEN_FILE)
            return None

    if creds and creds.valid:
        return creds

    return None


def save_credentials(creds: Credentials):
    """Save credentials to token.json for future sessions."""
    with open(config.TOKEN_FILE, "w") as f:
        f.write(creds.to_json())


def clear_credentials():
    """Remove stored credentials (logout)."""
    if os.path.exists(config.TOKEN_FILE):
        os.remove(config.TOKEN_FILE)
