# graph_helpers.py

def generate_network_graph_data(devices):
    # Placeholder: create mock node/edge structure
    nodes = [{"id": d.ip_address, "label": d.hostname or d.ip_address} for d in devices]
    edges = [{"from": nodes[i]["id"], "to": nodes[i + 1]["id"]} for i in range(len(nodes) - 1)]
    return {"nodes": nodes, "edges": edges}
