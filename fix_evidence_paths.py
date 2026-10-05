import os
import json

print("Fixing evidence JSON files...")
print()

evidence_dir = 'evidence'
json_files = [f for f in os.listdir(evidence_dir) if f.endswith('.json')]

print(f"Found {len(json_files)} JSON files")
print()

fixed_count = 0
for fname in json_files:
    filepath = os.path.join(evidence_dir, fname)
    
    try:
        # Read JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Fix image_path - remove folder name from path
        old_path = data.get('image_path', '')
        new_path = os.path.basename(old_path)
        
        if old_path != new_path:
            data['image_path'] = new_path
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"Fixed: {fname}")
            print(f"  Old path: {old_path}")
            print(f"  New path: {new_path}")
            fixed_count += 1
        else:
            print(f"OK: {fname}")
    
    except Exception as e:
        print(f"ERROR: {fname} - {e}")

print()
print(f"Fixed {fixed_count} files")
print()
print("Now restart dashboard and refresh browser!")
