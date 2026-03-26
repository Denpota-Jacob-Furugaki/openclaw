"""
Wrapper to run interview check and save results to file (avoiding console encoding issues)
"""
import json
import sys
from check_interview_requests import check_interviews, format_alert

if __name__ == "__main__":
    result = check_interviews()
    
    if result:
        # Save raw result
        with open('last_interview_check.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Generate alert
        alert = format_alert(result)
        
        # Write alert to file instead of stdout
        with open('interview_alert.txt', 'w', encoding='utf-8') as f:
            if alert:
                f.write(alert)
            else:
                f.write("✅ No interview requests found.")
        
        # Output simple status to console
        if alert:
            print(f"ALERT: {result['count']} interview request(s) found. See interview_alert.txt")
        else:
            print("OK: No interview requests found.")
    else:
        print("ERROR: Failed to check Gmail")
        sys.exit(1)
