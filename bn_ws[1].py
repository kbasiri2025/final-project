
"""
bn_ws.py — Fuzzy-aware web service
Author: Khujasta Basiri
Notes:
- Accepts linguistic inputs at /report (POST)
- Exposes beliefs at /inference (GET)
- Prometheus metrics at /metrics
"""

import pysmile_license  # keep license import if needed for your SMILE setup

from flask import Flask, request, jsonify
from pysmile import Network
from prometheus_client import start_http_server, Gauge, generate_latest
import threading

app = Flask(__name__)

BN_PATH = "attack_flow.xdsl"
net = Network()
net.read_file(BN_PATH)

# Create a gauge for the True-belief of every node
belief_gauges = {}
for node_id in net.get_all_node_ids():
    belief_gauges[node_id] = Gauge(f"belief_{node_id}", f"Belief value of {node_id} (True)")

# Simple linguistic → numeric mapping (0..1). You can tweak these later.
LINGUISTIC_MAP = {
    "no": 0.0, "none": 0.0, "false": 0.0, "low": 0.25, "unlikely": 0.2, "rare": 0.2,
    "moderate": 0.5, "possible": 0.5, "maybe": 0.5,
    "likely": 0.8, "high": 0.8, "severe": 0.85, "very high": 0.9, "true": 1.0, "yes": 1.0
}

def to_float(v):
    if isinstance(v, (int, float)):
        return max(0.0, min(1.0, float(v)))
    if isinstance(v, str):
        key = v.strip().lower()
        if key in LINGUISTIC_MAP:
            return LINGUISTIC_MAP[key]
        # try to parse numeric strings
        try:
            return max(0.0, min(1.0, float(key)))
        except:
            pass
    # default: treat as unknown/neutral
    return 0.5

def apply_evidence(evidence_dict):
    """
    evidence_dict: { node_id: linguistic_or_numeric_value }
    Strategy: convert linguistic to numeric in [0,1], then binarize to True/False
    threshold at 0.5 for now (keep it simple and transparent).
    """
    # Clear existing evidence
    net.clear_all_evidence()

    for node_id, val in evidence_dict.items():
        if node_id not in net.get_all_node_ids():
            # allow using node "names" if present; try mapping by matching Node name
            # build a map once
            pass

    # Build name->id map so users can send either "T1059" or "Command and Scripting Interpreter"
    name_to_id = {}
    for nid in net.get_all_node_ids():
        try:
            nm = net.get_node_name(nid)
        except:
            nm = None
        if nm:
            name_to_id[nm.lower()] = nid

    for key, val in evidence_dict.items():
        node_id = key if key in net.get_all_node_ids() else name_to_id.get(str(key).lower())
        if not node_id:
            continue  # skip unknown keys
        prob_true = to_float(val)
        # Simple binarization (you can later switch to virtual evidence if desired)
        state = "True" if prob_true >= 0.5 else "False"
        try:
            net.set_evidence(node_id, state)
        except Exception as e:
            # ignore if node is not boolean; you can extend to multi-state later
            continue

    net.update_beliefs()

def collect_beliefs():
    """
    Returns beliefs for all nodes as dict: {node_id: {"False": p0, "True": p1}}
    """
    out = {}
    for node_id in net.get_all_node_ids():
        try:
            beliefs = net.get_node_value(node_id)
            if beliefs and len(beliefs) >= 2:
                out[node_id] = {"False": round(beliefs[0], 4), "True": round(beliefs[1], 4)}
                # update Prometheus for True belief
                belief_gauges[node_id].set(beliefs[1])
        except Exception:
            continue
    return out

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True}), 200

@app.route("/report", methods=["POST"])
def report():
    """
    Accepts JSON like:
    { "processDelay": "moderate", "T1059": "likely", "Ransomware": 0.9 }
    """
    try:
        payload = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    apply_evidence(payload)
    beliefs = collect_beliefs()
    return jsonify({"ok": True, "beliefs": beliefs}), 200

@app.route("/inference", methods=["GET"])
def inference():
    beliefs = collect_beliefs()
    return jsonify(beliefs), 200

@app.route("/metrics", methods=["GET"])
def metrics():
    data = generate_latest()
    return data, 200, {"Content-Type": "text/plain"}

def start_prometheus():
    start_http_server(8000)

if __name__ == "__main__":
    threading.Thread(target=start_prometheus, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
