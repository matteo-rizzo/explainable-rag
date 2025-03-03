import json

import grakel
import networkx as nx
from grakel import WeisfeilerLehman, VertexHistogram


class CFGProcessor:
    @staticmethod
    def build_cfg_graph(cfg_json):
        """
        Convert a CFG JSON representation into a NetworkX directed graph with labeled nodes.
        :param cfg_json: JSON representation of a CFG.
        :return: A NetworkX directed graph or None if invalid.
        """
        if isinstance(cfg_json, str):  # Ensure it's a dictionary
            try:
                cfg_json = json.loads(cfg_json)  # Convert string to dict if needed
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid CFG JSON format: {e}")
                return None

        if not isinstance(cfg_json, dict) or "nodes" not in cfg_json or "edges" not in cfg_json:
            print("[ERROR] Invalid CFG format. Missing 'nodes' or 'edges' keys.")
            return None

        graph = nx.DiGraph()
        nodes = cfg_json.get("nodes", [])
        edges = cfg_json.get("edges", [])

        # Assign unique node IDs and labels
        normalized_nodes = {}
        for i, node in enumerate(nodes):
            node_name = str(node).strip()
            normalized_nodes[node_name] = i  # Assign integer ID
            graph.add_node(i, label=node_name)  # Store the label in node attributes

        # Add edges using the normalized integer IDs
        for edge in edges:
            source = normalized_nodes.get(str(edge.get("source")).strip())
            target = normalized_nodes.get(str(edge.get("target")).strip())

            if source is not None and target is not None:
                graph.add_edge(source, target)

        return graph

    @staticmethod
    def compute_similarity(cfg1, cfg2):
        """
        Compute similarity between two CFGs using Weisfeiler-Lehman Kernel.
        :param cfg1: The first CFG JSON object.
        :param cfg2: The second CFG JSON object.
        :return: A similarity score between 0 and 1.
        """
        graph1 = CFGProcessor.build_cfg_graph(cfg1)
        graph2 = CFGProcessor.build_cfg_graph(cfg2)

        if graph1 is None or graph2 is None:
            print("[ERROR] One of the CFG graphs is invalid.")
            return 0.0

        if not graph1.nodes or not graph2.nodes:
            print("[ERROR] One of the CFG graphs has no nodes.")
            return 0.0

        gk = WeisfeilerLehman(n_iter=3, base_graph_kernel=VertexHistogram)

        graphs = grakel.graph_from_networkx([graph1, graph2], node_labels_tag="label")

        kernel_matrix = gk.fit_transform(graphs)
        similarity_score = kernel_matrix[0, 1]
        return round(similarity_score, 4)
