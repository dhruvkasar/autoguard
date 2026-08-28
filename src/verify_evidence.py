import os
import json
import argparse
from .utils import sha256_file


def verify_dir(evidence_dir: str) -> int:
    mismatches = 0
    for fname in os.listdir(evidence_dir):
        if not fname.endswith('.json'):
            continue
        meta_path = os.path.join(evidence_dir, fname)
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        img_path = meta.get('image_path')
        expected = meta.get('sha256')
        if not img_path or not expected or not os.path.exists(img_path):
            print(f"[WARN] Missing fields or image for {meta_path}")
            mismatches += 1
            continue
        actual = sha256_file(img_path)
        if actual != expected:
            print(f"[FAIL] Hash mismatch: {img_path}\n expected={expected}\n actual  ={actual}")
            mismatches += 1
        else:
            print(f"[OK] {img_path} integrity verified.")
    return mismatches


def main():
    ap = argparse.ArgumentParser(description='Verify evidence integrity')
    ap.add_argument('--dir', type=str, default='evidence', help='Evidence directory')
    args = ap.parse_args()
    mismatches = verify_dir(args.dir)
    if mismatches:
        print(f"Completed with {mismatches} mismatches.")
        raise SystemExit(1)
    else:
        print("All evidence OK.")


if __name__ == '__main__':
    main()
