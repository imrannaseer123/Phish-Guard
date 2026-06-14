"""
Email Header Route Graph Module
────────────────────────────────
Parses "Received" headers from raw email to build a directed
mail-route graph for visualization.

This module is OPTIONAL and ADDITIVE — it has no effect on the
detection pipeline, risk scores, or any existing functionality.
If it fails, the core system continues unaffected.
"""

import re
from datetime import datetime


def parse_received_headers(payload_headers: list[dict]) -> list[dict]:
    """
    Parse Gmail API payload headers and extract the chain of 'Received' headers.

    Args:
        payload_headers: list of {"name": ..., "value": ...} dicts from
                         Gmail API's message.payload.headers.

    Each hop yields:
      - from_server: the sending server
      - by_server: the receiving server
      - timestamp: when the hop occurred (if parseable)
      - protocol: e.g., SMTP, ESMTPS, HTTPS

    Returns list of hops in chronological order (oldest first).
    """
    if not payload_headers:
        return []

    # Extract all Received header values (there can be many)
    received_blocks = [
        h["value"]
        for h in payload_headers
        if h.get("name", "").lower() == "received" and h.get("value")
    ]

    hops = []
    for block in received_blocks:
        hop = _parse_single_received(block)
        if hop:
            hops.append(hop)

    # Reverse to chronological order (Received headers are newest-first)
    hops.reverse()
    return hops


def _parse_single_received(block: str) -> dict | None:
    """Parse a single Received header block into structured data."""
    if not block:
        return None

    result = {
        "from_server": "Unknown",
        "by_server": "Unknown",
        "timestamp": None,
        "protocol": None,
        "ip": None,
    }

    # Extract "from <server>"
    from_match = re.search(
        r'from\s+([\w.\-]+(?:\.\w+)*)', block, re.IGNORECASE
    )
    if from_match:
        result["from_server"] = from_match.group(1)

    # Extract "by <server>"
    by_match = re.search(
        r'by\s+([\w.\-]+(?:\.\w+)*)', block, re.IGNORECASE
    )
    if by_match:
        result["by_server"] = by_match.group(1)

    # Extract IP address in brackets or parentheses
    ip_match = re.search(r'[\[\(]([\d.]+)[\]\)]', block)
    if ip_match:
        result["ip"] = ip_match.group(1)

    # Extract protocol (with, SMTP, ESMTPS, HTTPS, etc.)
    proto_match = re.search(
        r'with\s+(E?SMTP[SA]?|HTTPS?|LMTP)', block, re.IGNORECASE
    )
    if proto_match:
        result["protocol"] = proto_match.group(1).upper()

    # Extract timestamp after semicolon
    ts_match = re.search(r';\s*(.+)$', block)
    if ts_match:
        ts_str = ts_match.group(1).strip()
        result["timestamp"] = _parse_timestamp(ts_str)

    # Skip if we couldn't extract meaningful data
    if result["from_server"] == "Unknown" and result["by_server"] == "Unknown":
        return None

    return result


def _parse_timestamp(ts_str: str) -> str | None:
    """Try to parse various email timestamp formats into ISO string."""
    # Common formats in Received headers
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",      # Mon, 18 Feb 2026 12:00:00 +0000
        "%d %b %Y %H:%M:%S %z",            # 18 Feb 2026 12:00:00 +0000
        "%a, %d %b %Y %H:%M:%S %Z",       # Mon, 18 Feb 2026 12:00:00 UTC
    ]

    # Clean up: remove extra whitespace, parenthesized timezone names
    cleaned = re.sub(r'\s*\([^)]*\)', '', ts_str).strip()

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        except ValueError:
            continue

    # Return raw string if we can't parse
    return cleaned[:40] if len(cleaned) > 40 else cleaned


def build_graph_data(payload_headers: list[dict]) -> dict | None:
    """
    Build graph visualization data from Gmail API payload headers.

    Args:
        payload_headers: list of {"name": ..., "value": ...} dicts from
                         Gmail API's message.payload.headers.

    Returns:
        dict with 'nodes' and 'edges' for rendering, or None if
        no meaningful route data could be extracted.

    Example output:
    {
        "nodes": [
            {"id": "server1.example.com", "label": "server1", "ip": "1.2.3.4"},
            {"id": "server2.example.com", "label": "server2", "ip": None},
        ],
        "edges": [
            {"from": "server1.example.com", "to": "server2.example.com",
             "protocol": "ESMTPS", "timestamp": "2026-02-18 12:00:00 UTC"}
        ],
        "hop_count": 2,
    }
    """
    hops = parse_received_headers(payload_headers)

    if not hops:
        return None

    nodes = {}
    edges = []

    for hop in hops:
        from_id = hop["from_server"]
        by_id = hop["by_server"]

        # Add nodes
        if from_id != "Unknown" and from_id not in nodes:
            nodes[from_id] = {
                "id": from_id,
                "label": _short_label(from_id),
                "ip": hop.get("ip"),
            }
        if by_id != "Unknown" and by_id not in nodes:
            nodes[by_id] = {
                "id": by_id,
                "label": _short_label(by_id),
                "ip": None,
            }

        # Add edge
        if from_id != "Unknown" and by_id != "Unknown":
            edges.append({
                "from": from_id,
                "to": by_id,
                "protocol": hop.get("protocol", ""),
                "timestamp": hop.get("timestamp", ""),
            })

    if not nodes:
        return None

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "hop_count": len(hops),
    }


def _short_label(server_name: str) -> str:
    """Create a short display label from a full server hostname."""
    parts = server_name.split(".")
    if len(parts) > 2:
        return parts[0]
    return server_name
