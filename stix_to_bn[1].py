import pysmile_license  # Activate license

import json
import sys
from pysmile import Network

def extract_ttps(stix_data):
    ttps = {}
    relationships = []
    for obj in stix_data["objects"]:
        if obj["type"] == "attack-pattern":
            ttps[obj["id"]] = {
                "id": obj["id"],
                "name": obj.get("name", ""),
                "technique_id": obj["external_references"][0]["external_id"] if obj.get("external_references") else "",
                "tactic": obj.get("kill_chain_phases", [{}])[0].get("phase_name", "")
            }
        elif obj["type"] == "relationship":
            relationships.append((obj["source_ref"], obj["target_ref"]))
    return ttps, relationships

def build_bayesian_network(ttps, relationships, output_file="attack_flow.xdsl"):
    net = Network()
    id_map = {}
    for stix_id, info in ttps.items():
        node_id = info["technique_id"]
        if not node_id:
            continue
        net.add_node(Network.NODE_TYPE_CPT, node_id)
        net.set_node_name(node_id, info["name"])
        net.set_outcome_id(node_id, 0, "False")
        net.set_outcome_id(node_id, 1, "True")
        net.set_node_definition(node_id, [0.99, 0.01])
        id_map[stix_id] = node_id

    for src, tgt in relationships:
        if src in id_map and tgt in id_map:
            net.add_arc(id_map[src], id_map[tgt])

    for stix_id, info in ttps.items():
        node_id = info["technique_id"]
        if node_id is None or not net.get_parents(node_id):
            continue
        num_parents = len(net.get_parents(node_id))
        size = 2 ** num_parents
        cpt = []
        for i in range(size):
            if i > 0:
                cpt.extend([0.2, 0.8])
            else:
                cpt.extend([0.99, 0.01])
        net.set_node_definition(node_id, cpt)

    net.write_file(output_file)
    print(f"Saved to {output_file}")

def main(stix_path):
    with open(stix_path, "r") as f:
        stix_data = json.load(f)
    ttps, relationships = extract_ttps(stix_data)
    build_bayesian_network(ttps, relationships)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python stix_to_bn.py example_stix.json")
        sys.exit(1)
    main(sys.argv[1])
