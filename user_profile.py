
from datetime import datetime
import statistics
import database

def get_profile_stats() -> dict:
    """
    Calculate high-level risk statistics for the user.
    Returns:
        {
            "average_score": float,
            "total_scanned": int,
            "current_risk_level": str
        }
    """
    trends = database.get_risk_trends(limit=50)
    
    if not trends:
        return {
            "average_score": 0.0,
            "total_scanned": 0,
            "current_risk_level": "Unknown"
        }
    
    scores = [t['risk_score'] for t in trends]
    avg_score = statistics.mean(scores)
    
    # Simple risk level based on average
    if avg_score < 30:
        level = "Low"
    elif avg_score < 70:
        level = "Medium"
    else:
        level = "High"
        
    return {
        "average_score": round(avg_score, 1),
        "total_scanned": len(trends),
        "current_risk_level": level,
        # "trend_direction": ... (could implement slope check)
    }

def get_weekly_trend() -> list[dict]:
    """
    Get data prepared for a trend chart (Date vs Score).
    Returns list of {'date': 'YYYY-MM-DD', 'score': float}
    """
    trends = database.get_risk_trends(limit=20) # Last 20 scans
    data = []
    
    for t in trends:
        # Parse ISO timestamp to YYYY-MM-DD
        dt = datetime.fromisoformat(t['timestamp'])
        date_str = dt.strftime("%Y-%m-%d %H:%M") 
        data.append({
            "date": date_str,
            "score": t['risk_score']
        })
        
    return data
