"""
Gmail Reader Module
───────────────────
Reads emails from the user's Gmail inbox using the Gmail API.
Extracts subject, sender, date, and body content from messages.
"""

import base64
from dataclasses import dataclass

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup

import config
from preprocessor import strip_html


def get_gmail_service(creds: Credentials):
    """Build and return a Gmail API service instance."""
    return build("gmail", "v1", credentials=creds)


def list_inbox(creds: Credentials, max_results: int = None) -> list[dict]:
    """
    List messages in the user's inbox.
    Returns list of {id, subject, sender, date, snippet}.
    """
    if max_results is None:
        max_results = config.MAX_INBOX_RESULTS

    service = get_gmail_service(creds)
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results,
    ).execute()

    messages = results.get("messages", [])
    email_list = []

    for msg_stub in messages:
        msg = service.users().messages().get(
            userId="me",
            id=msg_stub["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        email_list.append({
            "id": msg_stub["id"],
            "subject": headers.get("Subject", "(No Subject)"),
            "sender": headers.get("From", "(Unknown Sender)"),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })

    return email_list


def get_message(creds: Credentials, message_id: str) -> dict:
    """
    Fetch a full message by ID.
    Returns {id, subject, sender, date, body_text, body_html}.
    """
    service = get_gmail_service(creds)
    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full",
    ).execute()

    payload = msg.get("payload", {})
    headers = {h["name"]: h["value"] for h in payload.get("headers", [])}

    body_html = ""
    body_text = ""

    # Extract body from message parts
    parts = payload.get("parts", [])
    if parts:
        for part in parts:
            mime_type = part.get("mimeType", "")
            data = part.get("body", {}).get("data", "")
            if data:
                decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                if mime_type == "text/html":
                    body_html = decoded
                elif mime_type == "text/plain":
                    body_text = decoded

            # Handle nested multipart
            sub_parts = part.get("parts", [])
            for sub_part in sub_parts:
                sub_mime = sub_part.get("mimeType", "")
                sub_data = sub_part.get("body", {}).get("data", "")
                if sub_data:
                    decoded = base64.urlsafe_b64decode(sub_data).decode("utf-8", errors="replace")
                    if sub_mime == "text/html" and not body_html:
                        body_html = decoded
                    elif sub_mime == "text/plain" and not body_text:
                        body_text = decoded
    else:
        # Single-part message
        data = payload.get("body", {}).get("data", "")
        if data:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            mime_type = payload.get("mimeType", "")
            if mime_type == "text/html":
                body_html = decoded
            else:
                body_text = decoded

    # If we only have HTML, derive text from it
    if body_html and not body_text:
        body_text = strip_html(body_html)

    # Dictionary to hold attachments
    attachments = []

    def _extract_attachments(parts_list):
        for p in parts_list:
            fname = p.get("filename", "")
            mime = p.get("mimeType", "")
            body = p.get("body", {})
            data = body.get("data", "")
            att_id = body.get("attachmentId", "")
            
            if fname and (data or att_id):
                file_content = None
                if data:
                    try:
                        file_content = base64.urlsafe_b64decode(data)
                    except:
                        pass
                
                if file_content:
                    attachments.append({
                        "filename": fname,
                        "mime_type": mime,
                        "data": file_content
                    })
            
            if p.get("parts"):
                _extract_attachments(p.get("parts"))

    _extract_attachments(payload.get("parts", []))

    return {
        "id": message_id,
        "subject": headers.get("Subject", "(No Subject)"),
        "sender": headers.get("From", "(Unknown Sender)"),
        "date": headers.get("Date", ""),
        "body_text": body_text,
        "body_html": body_html,
        "attachments": attachments,
        "headers": headers,
        "payload_headers": payload.get("headers", []),
    }
