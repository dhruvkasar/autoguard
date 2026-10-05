import os
import json
from datetime import datetime

print("="*60)
print("AutoGuard Dashboard Diagnostic Tool")
print("="*60)
print()

# Check 1: Evidence files
evidence_dir = 'evidence'
json_files = [f for f in os.listdir(evidence_dir) if f.endswith('.json')]
jpg_files = [f for f in os.listdir(evidence_dir) if f.endswith('.jpg')]

print(f"Step 1: Evidence Files")
print(f"  JSON files: {len(json_files)}")
print(f"  JPG files: {len(jpg_files)}")
print()

# Check 2: Load evidence data
print(f"Step 2: Loading Evidence Data")
evidence_list = []
for fname in json_files[:5]:  # Check first 5
    try:
        with open(os.path.join(evidence_dir, fname), 'r', encoding='utf-8') as f:
            data = json.load(f)
            evidence_list.append(data)
            print(f"  OK {fname}")
            print(f"    Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"    Rule: {data.get('rule', 'N/A')}")
            print(f"    Person ID: {data.get('person_id', 'N/A')}")
    except Exception as e:
        print(f"  ERROR {fname}: {e}")
print()

# Check 3: Current time vs incident times
print(f"Step 3: Date/Time Check")
print(f"  Current time: {datetime.now()}")
if evidence_list:
    print(f"  First incident: {evidence_list[0].get('timestamp', 'N/A')}")
    try:
        incident_time = datetime.strptime(evidence_list[0]['timestamp'], "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff = now - incident_time
        print(f"  Time difference: {diff.days} days, {diff.seconds // 3600} hours ago")
    except:
        print(f"  Could not parse timestamp")
print()

# Check 4: Dashboard filter test
print(f"Step 4: Dashboard Filter Simulation")
from datetime import datetime, timedelta
now = datetime.now()

# Load all evidence
all_evidence = []
for fname in json_files:
    try:
        with open(os.path.join(evidence_dir, fname), 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_evidence.append(data)
    except:
        pass

print(f"  Total incidents: {len(all_evidence)}")

# Simulate "today" filter
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
today_incidents = []
for e in all_evidence:
    try:
        e_time = datetime.strptime(e['timestamp'], "%Y-%m-%d %H:%M:%S")
        if e_time >= today_start:
            today_incidents.append(e)
    except:
        pass

print(f"  Incidents from today: {len(today_incidents)}")

# Simulate "week" filter
week_ago = now - timedelta(days=7)
week_incidents = [e for e in all_evidence if datetime.strptime(e['timestamp'], "%Y-%m-%d %H:%M:%S") >= week_ago]
print(f"  Incidents from last 7 days: {len(week_incidents)}")

print()

# Check 5: Image paths
print(f"Step 5: Image Path Verification")
if evidence_list:
    for i, e in enumerate(evidence_list[:3]):
        img_path = e.get('image_path', '')
        img_name = os.path.basename(img_path)
        exists = os.path.exists(img_path) if img_path else False
        print(f"  {i+1}. Image: {img_name}")
        print(f"     Path: {img_path}")
        print(f"     Exists: {exists}")
print()

# Check 6: Sample JSON structure
print(f"Step 6: Sample JSON Structure")
if evidence_list:
    sample = evidence_list[0]
    print(f"  Keys in JSON: {list(sample.keys())}")
    print(f"  Has 'timestamp': {'timestamp' in sample}")
    print(f"  Has 'rule': {'rule' in sample}")
    print(f"  Has 'person_id': {'person_id' in sample}")
    print(f"  Has 'image_path': {'image_path' in sample}")
print()

print("="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)
print()

# Final diagnosis
if len(all_evidence) > 0 and len(today_incidents) == 0:
    print("⚠️ ISSUE FOUND:")
    print("   - Evidence exists but NO incidents from today")
    print("   - Dashboard default filter is 'Today'")
    print("   - Your incidents are older than today")
    print()
    print("🔧 SOLUTION:")
    print("   On dashboard page, change filter from 'Today' to 'All Time'")
elif len(all_evidence) == 0:
    print("⚠️ ISSUE FOUND:")
    print("   - JSON files exist but could not be loaded")
    print("   - Check JSON format errors")
else:
    print("✓ Evidence should be visible on dashboard")
    print("  Check browser console for errors (F12)")

print()
