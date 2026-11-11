"""
Cross-Email Campaign Detection Module (Feature 3)
──────────────────────────────────────────────────
Detects repeated phishing templates across multiple analyzed emails.

Algorithm:
    1. For each analyzed email, compute a "fingerprint" from:
       - Normalized subject line SimHash (locality-sensitive hash)
       - Body token set for Jaccard similarity
       - Sender domain
    2. Compare new fingerprints against stored ones.
    3. Group similar emails into campaign clusters.

Storage:
    New SQLite table `email_fingerprints` — stores hashes per email.
    Never modifies the core `analysis_logs` table.

Design Constraints:
    - Does NOT alter individual email risk scores
    - Read-only clustering (no write to analysis_logs)
    - Fail-safe: database errors cause graceful fallback
    - No external dependencies (pure Python heuristics)
"""

import sqlite3
import json
import hashlib
import re
from datetime import datetime, timezone
from collections import Counter

import config


# ─── Database Setup ───────────────────────────────────────────────────────────

def _get_connection():
    """Get a connection to the phishing logs database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_fingerprint_db():
    """Create the email_fingerprints table if it doesn't exist."""
    try:
        conn = _get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS email_fingerprints (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id    TEXT UNIQUE,
                subject_hash  TEXT,
                body_tokens   TEXT,
                sender_domain TEXT,
                intent        TEXT,
                risk_level    TEXT,
                timestamp     TEXT,
                campaign_id   TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass  # Fail silently — feature degrades gracefully


# Initialize on import
_init_fingerprint_db()


# ─── Fingerprinting ──────────────────────────────────────────────────────────

def _normalize_subject(subject):
    """
    Normalize subject for comparison.
    Strips Re:/Fwd:, lowercases, removes extra whitespace.
    """
    if not subject:
        return ""
    # Remove Re: Fwd: prefixes
    cleaned = re.sub(r"^(re:|fwd?:|fw:)\s*", "", subject.strip(), flags=re.IGNORECASE)
    # Lowercase and normalize whitespace
    return re.sub(r"\s+", " ", cleaned.lower()).strip()


def _simhash_text(text):
    """
    Compute a simple locality-sensitive hash of text.

    Uses word-level hashing combined into a 64-bit fingerprint.
    Similar texts produce similar hashes (low Hamming distance).
    """
    if not text:
        return "0" * 16

    words = text.split()
    if not words:
        return "0" * 16

    # Compute per-word hashes and accumulate bit positions
    bit_counts = [0] * 64
    for word in words:
        word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
        for i in range(64):
            if word_hash & (1 << i):
                bit_counts[i] += 1
            else:
                bit_counts[i] -= 1

    # Convert to binary fingerprint
    fingerprint = 0
    for i in range(64):
        if bit_counts[i] > 0:
            fingerprint |= (1 << i)

    return format(fingerprint, "016x")


def _extract_body_tokens(body_text, limit=100):
    """
    Extract significant tokens from email body for similarity comparison.
    Removes common stop words and short words.
    """
    if not body_text:
        return []

    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "and", "but", "or",
        "nor", "not", "so", "yet", "both", "either", "neither", "each",
        "every", "all", "any", "few", "more", "most", "other", "some", "such",
        "no", "only", "own", "same", "than", "too", "very", "this", "that",
        "these", "those", "it", "its", "he", "she", "they", "we", "you",
        "i", "me", "my", "your", "his", "her", "our", "their",
    }

    words = re.findall(r"[a-z]{3,}", body_text.lower())
    tokens = [w for w in words if w not in stop_words]
    return tokens[:limit]


def _hamming_distance(hash1, hash2):
    """Compute Hamming distance between two hex-encoded SimHashes."""
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        xor = val1 ^ val2
        return bin(xor).count("1")
    except (ValueError, TypeError):
        return 64  # Maximum distance


def _jaccard_similarity(tokens1, tokens2):
    """Compute Jaccard similarity between two token sets."""
    if not tokens1 or not tokens2:
        return 0.0
    set1 = set(tokens1)
    set2 = set(tokens2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


# ─── Core Functions ──────────────────────────────────────────────────────────

def store_fingerprint(message_id, subject, body_text, sender_domain,
                      intent="", risk_level=""):
    """
    Compute and store the fingerprint for an analyzed email.

    Parameters
    ----------
    message_id : str
    subject : str
    body_text : str
    sender_domain : str
    intent : str
    risk_level : str
    """
    try:
        normalized_subject = _normalize_subject(subject)
        subject_hash = _simhash_text(normalized_subject)
        tokens = _extract_body_tokens(body_text)

        # Check for matching campaign
        campaign_id = _find_matching_campaign(subject_hash, tokens, sender_domain)

        conn = _get_connection()
        conn.execute("""
            INSERT OR REPLACE INTO email_fingerprints
            (message_id, subject_hash, body_tokens, sender_domain,
             intent, risk_level, timestamp, campaign_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message_id,
            subject_hash,
            json.dumps(tokens),
            sender_domain,
            intent,
            risk_level,
            datetime.now(timezone.utc).isoformat(),
            campaign_id,
        ))
        conn.commit()
        conn.close()

        return campaign_id

    except Exception:
        return None


def _find_matching_campaign(subject_hash, tokens, sender_domain):
    """
    Search existing fingerprints for similar emails.

    Similarity criteria:
        - Subject SimHash Hamming distance ≤ 8 (out of 64 bits), OR
        - Body token Jaccard similarity ≥ 0.4
        - AND same sender domain (optional but boosts confidence)

    Returns existing campaign_id if found, or generates a new one.
    """
    try:
        conn = _get_connection()
        rows = conn.execute("""
            SELECT message_id, subject_hash, body_tokens, sender_domain, campaign_id
            FROM email_fingerprints
            ORDER BY id DESC LIMIT 200
        """).fetchall()
        conn.close()

        best_campaign = None
        best_score = 0.0

        for row in rows:
            # Subject similarity
            hamming = _hamming_distance(subject_hash, row["subject_hash"])
            subject_sim = max(0, 1.0 - hamming / 64.0)

            # Body similarity
            existing_tokens = json.loads(row["body_tokens"]) if row["body_tokens"] else []
            body_sim = _jaccard_similarity(tokens, existing_tokens)

            # Domain match bonus
            domain_match = (sender_domain == row["sender_domain"]) if sender_domain else False
            domain_bonus = 0.2 if domain_match else 0.0

            # Combined score
            combined = (subject_sim * 0.4) + (body_sim * 0.4) + domain_bonus

            # Threshold: 0.5 combined score to be considered same campaign
            if combined >= 0.5 and combined > best_score:
                best_score = combined
                best_campaign = row["campaign_id"]

        if best_campaign:
            return best_campaign

        # No match found — generate new campaign ID
        return f"camp_{hashlib.md5(subject_hash.encode()).hexdigest()[:8]}"

    except Exception:
        return f"camp_{hashlib.md5(subject_hash.encode()).hexdigest()[:8]}"


def get_campaigns(limit=20):
    """
    Retrieve detected campaign groups.

    Returns
    -------
    list[dict]
        Each dict has: campaign_id, email_count, sender_domains,
        intents, risk_levels, first_seen, last_seen, sample_subjects.
    """
    try:
        conn = _get_connection()
        rows = conn.execute("""
            SELECT f.campaign_id, COUNT(*) as email_count,
                   GROUP_CONCAT(DISTINCT f.sender_domain) as domains,
                   GROUP_CONCAT(DISTINCT f.intent) as intents,
                   GROUP_CONCAT(DISTINCT f.risk_level) as risk_levels,
                   MIN(f.timestamp) as first_seen,
                   MAX(f.timestamp) as last_seen
            FROM email_fingerprints f
            WHERE f.campaign_id IS NOT NULL
            GROUP BY f.campaign_id
            HAVING email_count >= 2
            ORDER BY email_count DESC
            LIMIT ?
        """, (limit,)).fetchall()

        campaigns = []
        for row in rows:
            campaigns.append({
                "campaign_id": row["campaign_id"],
                "email_count": row["email_count"],
                "sender_domains": (row["domains"] or "").split(","),
                "intents": (row["intents"] or "").split(","),
                "risk_levels": (row["risk_levels"] or "").split(","),
                "first_seen": row["first_seen"],
                "last_seen": row["last_seen"],
            })

        conn.close()
        return campaigns

    except Exception:
        return []


def get_campaign_match(message_id):
    """
    Check if a specific email belongs to a known campaign.

    Returns
    -------
    dict or None
        Campaign info if the email is part of a campaign with ≥2 emails.
    """
    try:
        conn = _get_connection()
        row = conn.execute("""
            SELECT campaign_id FROM email_fingerprints WHERE message_id = ?
        """, (message_id,)).fetchone()

        if not row or not row["campaign_id"]:
            conn.close()
            return None

        campaign_id = row["campaign_id"]

        # Count emails in this campaign
        count_row = conn.execute("""
            SELECT COUNT(*) as cnt FROM email_fingerprints WHERE campaign_id = ?
        """, (campaign_id,)).fetchone()

        conn.close()

        if count_row and count_row["cnt"] >= 2:
            return {
                "campaign_id": campaign_id,
                "email_count": count_row["cnt"],
            }

        return None

    except Exception:
        return None
