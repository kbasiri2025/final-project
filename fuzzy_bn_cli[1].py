
# fuzzy_bn_cli.py — Shell interface for FBN
# Author: Khujasta Basiri

import json
import argparse
from pysmile import Network

# must mirror the logic in bn_ws.py for consistent grading
LINGUISTIC_MAP = {
    "no": 0.0, "none": 0.0, "false": 0.0, "low": 0.25, "unlikely": 0.2, "rare": 0.2,
    "moderate": 0.5, "possible": 0.5, "maybe": 0.5,
    "likely": 0.8, "high": 0.8, "severe": 0.85, "very high": 0.9, "true": 1.0, "yes": 1.0
}

def to_float(v):
    try:
        return max(0.0, min(1.0, float(v)))
    except:
        return LINGUISTIC_MAP.get(str(v).strip().lower(), 0.5)

def main():
    p = argparse.ArgumentParser(description="Fuzzy BN shell for CYSE 630")
    p.add_argument("--bn", default="attack_flow.xdsl", help="Path to BN file")
    p.add_argument("--report", required=True, help='JSON like {"T1059":"likely","Ransomware":0.9}')
    args = p.parse_args()

    net = Network()
    net.read_file(args.bn)

    report = json.loads(args.report)
    # Build name->id map
    name_to_id = {}
    for nid in net.get_all_node_ids():
        try:
            nm = net.get_node_name(nid)
        except:
            nm = None
        if nm:
            name_to_id[nm.lower()] = nid

    net.clear_all_evidence()

    for key, val in report.items():
        node_id = key if key in net.get_all_node_ids() else name_to_id.get(str(key).lower())
        if not node_id:
            print(f"[skip] unknown node: {key}")
            continue
        prob_true = to_float(val)
        state = "True" if prob_true >= 0.5 else "False"
        try:
            net.set_evidence(node_id, state)
        except Exception as e:
            print(f"[warn] could not set evidence for {node_id}: {e}")

    net.update_beliefs()

    # Print results compactly
    for node_id in net.get_all_node_ids():
        try:
            vals = net.get_node_value(node_id)
            if vals and len(vals) >= 2:
                print(f"{node_id}: True={vals[1]:.4f} False={vals[0]:.4f}")
        except Exception:
            continue

if __name__ == "__main__":
    main()
