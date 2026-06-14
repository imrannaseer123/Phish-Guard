"""
ascend Feature 2 — Threat Intent Ontology Builder
════════════════════════════════════════════════════
Maps Evidence → Intent → Impact chains using a static
knowledge graph. Produces a structured view of *why*
certain evidence matters and *what* it enables.

Boundary: Purely informational. Does NOT affect risk scores.
Uses the knowledge graph defined in ascend_config.ONTOLOGY_MAP.
"""

from ascend import ascend_config


def build_ontology(findings: list[dict]) -> list[dict]:
    """
    Map each finding's indicator to its ontology chain.

    Args:
        findings: List of finding dicts from core engine.

    Returns:
        List of ontology chain dicts:
        [
            {
                "evidence": "shortened_url",
                "evidence_detail": "Found shortened URL: bit.ly/...",
                "chains": [
                    {
                        "intent": "Obfuscation",
                        "impact": "Credential Theft",
                        "description": "Shortened URLs hide..."
                    }
                ]
            },
            ...
        ]
    """
    if not ascend_config.THREAT_ONTOLOGY_ENABLED:
        return []

    if not findings:
        return []

    ontology_results = []
    seen_indicators = set()

    for f in findings:
        indicator = f.get("indicator", "")
        if not indicator or indicator in seen_indicators:
            continue

        chains = ascend_config.ONTOLOGY_MAP.get(indicator, [])
        if chains:
            seen_indicators.add(indicator)
            ontology_results.append({
                "evidence": indicator,
                "evidence_detail": f.get("evidence", ""),
                "analyzer": f.get("analyzer", ""),
                "chains": chains,
            })

    return ontology_results


def get_impact_summary(ontology_data: list[dict]) -> dict:
    """
    Generate a summary of all impacts found.

    Returns:
        {
            "total_chains": 5,
            "unique_intents": ["Obfuscation", "Social Engineering", ...],
            "unique_impacts": ["Credential Theft", "Identity Theft", ...],
            "risk_narrative": "Analysis revealed 5 threat chains..."
        }
    """
    if not ontology_data:
        return {
            "total_chains": 0,
            "unique_intents": [],
            "unique_impacts": [],
            "risk_narrative": "No threat ontology chains identified.",
        }

    all_intents = set()
    all_impacts = set()
    total = 0

    for entry in ontology_data:
        for chain in entry.get("chains", []):
            all_intents.add(chain["intent"])
            all_impacts.add(chain["impact"])
            total += 1

    intents = sorted(all_intents)
    impacts = sorted(all_impacts)

    narrative = (
        f"Analysis revealed {total} threat chain{'s' if total != 1 else ''} "
        f"across {len(intents)} intent categor{'ies' if len(intents) != 1 else 'y'} "
        f"with {len(impacts)} potential impact{'s' if len(impacts) != 1 else ''}. "
        f"Primary intents: {', '.join(intents[:3])}."
    )

    return {
        "total_chains": total,
        "unique_intents": intents,
        "unique_impacts": impacts,
        "risk_narrative": narrative,
    }
