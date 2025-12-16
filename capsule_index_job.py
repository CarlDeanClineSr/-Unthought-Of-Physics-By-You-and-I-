#!/usr/bin/env python3
"""
LUFT Capsule Manifest Index Job – Paste me in the main root of your master repo.
Scans folders for manifest files, merges, and builds master index.
"""

import os, json, yaml
from datetime import datetime

MANIFEST_PATTERNS = ("manifest_", ".json", ".yaml", ".yml")
MASTER_INDEX_FILE = "manifest_master_index.yaml"

def load_yaml_or_json(path):
    with open(path, "r") as f:
        if path.endswith(".json"):
            return json.load(f)
        else:
            return yaml.safe_load(f)

def validate_schema(capsule):
    required = ["capsule_id","timestamp_utc","status","hash"]
    return all(field in capsule for field in required)

def merge_capsules(all_capsules):
    master_index = {}
    for capsule, repo, path in all_capsules:
        cid = capsule["capsule_id"]
        if cid not in master_index:
            master_index[cid] = {**capsule, "source_repo": repo, "manifest_path": path}
        else:
            existing = master_index[cid]
            if capsule["status"] == "green" and existing["status"] != "green":
                master_index[cid] = {**capsule, "source_repo": repo, "manifest_path": path}
            elif capsule["timestamp_utc"] < existing["timestamp_utc"]:
                master_index[cid] = {**capsule, "source_repo": repo, "manifest_path": path}
            else:
                tags = set(existing.get("tags", [])) | set(capsule.get("tags", []))
                master_index[cid]["tags"] = list(tags)
    return master_index

def save_master_index(master_index, filename=MASTER_INDEX_FILE):
    with open(filename, "w") as f:
        yaml.safe_dump(master_index, f, sort_keys=False)

def main():
    # Edit this block: add folders (repo clones/nodes) to scan for manifests
    repo_dirs = ["./"]  # . means current folder, add subfolders for others
    manifest_paths = []
    for repo in repo_dirs:
        for root, dirs, files in os.walk(repo):
            for file in files:
                if file.startswith("manifest_") and file.endswith((".json",".yaml",".yml")):
                    manifest_paths.append((repo, os.path.join(root,file)))
    all_capsules = []
    for repo, path in manifest_paths:
        manifest = load_yaml_or_json(path)
        for capsule in manifest.get("capsules", []):
            if validate_schema(capsule):
                all_capsules.append((capsule, repo, path))
    master_index = merge_capsules(all_capsules)
    save_master_index(master_index)
    print(f"Master index saved to {MASTER_INDEX_FILE} with {len(master_index)} capsules.")

if __name__ == "__main__":
    main()
