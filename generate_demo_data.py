"""
Demo Data Generator
Generates realistic synthetic data with threat scenarios
"""
import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Threat scenarios
THREAT_USERS = [
    "user_005",  # Data Exfiltration
    "user_017",  # Privilege Escalation
    "user_023",  # After-Hours Access
    "user_034",  # Unusual Resource Access
    "user_042",  # Rapid Behavior Change
    "user_056",  # Mass Download
    "user_067",  # Lateral Movement
    "user_078",  # Account Sharing
    "user_089",  # Data Deletion
    "user_091"   # Credential Harvesting
]

RESOURCE_TYPES = [
    "classified_documents",
    "source_code",
    "customer_data",
    "financial_records",
    "hr_records",
    "internal_communications",
    "public_resources"
]

ACTIONS = ["read", "write", "delete", "download", "share"]


def generate_normal_user_activities(user_id, start_date, days=90):
    """Generate normal user activities"""
    activities = []
    current_date = start_date
    
    for day in range(days):
        # Normal users work 9-5, Monday-Friday
        if current_date.weekday() < 5:  # Weekday
            num_activities = random.randint(15, 40)
            
            for _ in range(num_activities):
                hour = random.choices(
                    range(24),
                    weights=[1]*8 + [10]*9 + [1]*7,  # Peak 9-17
                    k=1
                )[0]
                
                minute = random.randint(0, 59)
                timestamp = current_date.replace(hour=hour, minute=minute)
                
                activity = {
                    "user_id": user_id,
                    "timestamp": timestamp.isoformat(),
                    "action": random.choices(
                        ACTIONS,
                        weights=[50, 20, 5, 15, 10],
                        k=1
                    )[0],
                    "resource_id": f"resource_{random.randint(1, 500)}",
                    "resource_type": random.choices(
                        RESOURCE_TYPES,
                        weights=[5, 15, 20, 10, 8, 25, 17],
                        k=1
                    )[0],
                    "metadata": {}
                }
                activities.append(activity)
        
        current_date += timedelta(days=1)
    
    return activities


def generate_threat_activities(user_id, start_date, days=90):
    """Generate activities with threat patterns"""
    activities = []
    current_date = start_date
    threat_start_day = days - 30  # Threat behavior starts in last 30 days
    
    for day in range(days):
        is_threat_period = day >= threat_start_day
        
        if current_date.weekday() < 5:  # Weekday
            if is_threat_period:
                # Threat behavior
                num_activities = random.randint(40, 80)  # Increased activity
                
                for _ in range(num_activities):
                    # More after-hours activity
                    hour = random.choices(
                        range(24),
                        weights=[5]*8 + [10]*9 + [8]*7,
                        k=1
                    )[0]
                    
                    minute = random.randint(0, 59)
                    timestamp = current_date.replace(hour=hour, minute=minute)
                    
                    # More sensitive resources and downloads
                    activity = {
                        "user_id": user_id,
                        "timestamp": timestamp.isoformat(),
                        "action": random.choices(
                            ACTIONS,
                            weights=[30, 15, 10, 35, 10],  # More downloads
                            k=1
                        )[0],
                        "resource_id": f"resource_{random.randint(1, 500)}",
                        "resource_type": random.choices(
                            RESOURCE_TYPES,
                            weights=[25, 20, 25, 15, 5, 5, 5],  # More sensitive
                            k=1
                        )[0],
                        "metadata": {}
                    }
                    activities.append(activity)
            else:
                # Normal behavior before threat
                activities.extend(generate_normal_user_activities(user_id, current_date, days=1))
        
        current_date += timedelta(days=1)
    
    return activities


def main():
    parser = argparse.ArgumentParser(description="Generate demo data for Drishti")
    parser.add_argument("--output-dir", default="demo_data", help="Output directory")
    parser.add_argument("--users", type=int, default=100, help="Number of users")
    parser.add_argument("--days", type=int, default=90, help="Days of data")
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"Generating demo data...")
    print(f"   Users: {args.users}")
    print(f"   Days: {args.days}")
    print(f"   Threat users: {len(THREAT_USERS)}")
    
    start_date = datetime.now() - timedelta(days=args.days)
    all_activities = []
    
    for i in range(args.users):
        user_id = f"user_{i:03d}"
        
        if user_id in THREAT_USERS:
            print(f"   [!] Generating threat user: {user_id}")
            activities = generate_threat_activities(user_id, start_date, args.days)
        else:
            activities = generate_normal_user_activities(user_id, start_date, args.days)
        
        all_activities.extend(activities)
    
    # Save to JSON
    output_file = output_dir / "activities.json"
    with open(output_file, 'w') as f:
        json.dump(all_activities, f, indent=2)
    
    print(f"[OK] Generated {len(all_activities):,} activities")
    print(f"[*] Saved to: {output_file}")


if __name__ == "__main__":
    main()
