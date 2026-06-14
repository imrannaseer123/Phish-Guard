import sys
import os
import sqlite3

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

import database
import user_profile

def test_risk_profiling():
    print("Testing User Risk Profiling...")
    
    # 1. Log some dummy data
    print("Logging dummy risk trends...")
    database.log_risk_trend(10.0, "Low")
    database.log_risk_trend(50.0, "Medium")
    database.log_risk_trend(90.0, "High")
    
    # 2. Test Stats
    stats = user_profile.get_profile_stats()
    print(f"Profile Stats: {stats}")
    
    # We expect at least 3 items (plus any previous runs)
    if stats['total_scanned'] < 3:
        print("[FAIL] Total scanned count is too low.")
        return
        
    # Average of 10, 50, 90 is 50. But there might be other data.
    # We just check if it runs and returns valid types.
    if not isinstance(stats['average_score'], (int, float)):
        print("[FAIL] Average score is not a number.")
        return
        
    print("[PASS] Profile stats calculation working.")
    
    # 3. Test Trends
    trends = user_profile.get_weekly_trend()
    print(f"Weekly Trend Data Points: {len(trends)}")
    
    if len(trends) < 3:
        print("[FAIL] Trend data missing.")
        return
        
    print(f"Sample Trend: {trends[-1]}")
    if 'date' not in trends[-1] or 'score' not in trends[-1]:
        print("[FAIL] Trend data format incorrect.")
        return
        
    print("[PASS] Weekly trend retrieval working.")

if __name__ == "__main__":
    try:
        # Initialize DB just in case
        database.init_db()
        test_risk_profiling()
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()
