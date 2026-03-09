
from berqun_client import get_berqun_client
from berqun_report_generator import TEAM_DOMAIN_MAP, PERSON_DOMAIN_MAP
from datetime import datetime, timedelta
import json

def debug_vpn():
    client = get_berqun_client()
    print("Fetching staff list...")
    staff_list = client.get_staff_list()
    
    targets = ["Kamil Köse", "Burak Eder", "Esra Hayta", "Mehmet Yılmaz"]
    
    three_days_ago = datetime.now() - timedelta(days=3)
    
    print("-" * 120)
    print(f"{'Name':<20} | {'Last Seen':<25} | {'Domain':<40} | {'VPN Missing?'}")
    print("-" * 120)

    for staff in staff_list:
        fullname = staff.get("full_name", str(staff.get("name")) + " " + str(staff.get("surname")))
        
        is_target = False
        for t in targets:
            if t.lower() in fullname.lower():
                is_target = True
                break
        
        if is_target:
            last_seen_str = staff.get("last_seen_date")
            status = "UNKNOWN"
            
            if not last_seen_str:
                status = "YES (Missing)"
            else:
                try:
                    ts = last_seen_str.replace("T", " ").split(".")[0]
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    if dt < three_days_ago:
                        status = "YES (Missing)"
                    else:
                        status = "NO (Active)"
                except:
                    status = "ERROR"
            
            # Mapping Logic
            team_name = staff.get("team_name", "")
            mapped_domain = "Unknown"
            
            if fullname in PERSON_DOMAIN_MAP:
                mapped_domain = f"{PERSON_DOMAIN_MAP[fullname]} (Person Map)"
            else:
                best_match = None
                max_len = -1
                for prefix, domain in TEAM_DOMAIN_MAP.items():
                    if team_name.startswith(prefix):
                        if len(prefix) > max_len:
                            max_len = len(prefix)
                            best_match = domain
                if best_match:
                    mapped_domain = best_match
            
            print(f"{fullname:<20} | {str(last_seen_str):<25} | {mapped_domain:<40} | {status}")

if __name__ == "__main__":
    debug_vpn()
