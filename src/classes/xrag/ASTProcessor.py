import json
import grakel
import networkx as nx
from grakel import WeisfeilerLehman, VertexHistogram


class ASTProcessor:
    @staticmethod
    def find_valid_root(ast_json):
        """
        Find the first valid AST node that contains a "name" or "nodeType" key.
        :param ast_json: JSON representation of an AST.
        :return: The valid root AST node or None.
        """
        if isinstance(ast_json, dict):
            if "name" in ast_json or "nodeType" in ast_json:
                return ast_json  # Found a valid root

            # If "name" is missing, check "nodes" or "children" for the first valid node
            for key in ["nodes", "children"]:
                if key in ast_json and isinstance(ast_json[key], list):
                    for child in ast_json[key]:
                        valid_root = ASTProcessor.find_valid_root(child)
                        if valid_root:
                            return valid_root

        return None

    @staticmethod
    def validate_ast(ast_json):
        """
        Ensures the AST JSON is in the expected format.
        :param ast_json: JSON representation of an AST.
        :return: Validated AST JSON or None if invalid.
        """
        if isinstance(ast_json, str):  # Convert from string if needed
            try:
                ast_json = json.loads(ast_json)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid AST JSON format: {e}")
                return None

        if isinstance(ast_json, list):
            print(f"[WARNING] AST is a list, expected a dictionary. Taking first element.")
            ast_json = ast_json[0] if ast_json else None

        if not isinstance(ast_json, dict):
            print("[ERROR] AST JSON is not a dictionary.")
            return None

        # Automatically find the valid root node
        valid_ast = ASTProcessor.find_valid_root(ast_json)

        if valid_ast is None:
            print("[ERROR] Invalid AST format. No valid root node found.")
            print(f"[DEBUG] AST keys: {list(ast_json.keys())}")  # Show only top-level keys
            return None

        return valid_ast

    @staticmethod
    def build_ast_graph(ast_json):
        """
        Convert an AST JSON structure into a NetworkX graph.
        :param ast_json: JSON representation of an AST.
        :return: A NetworkX directed graph.
        """
        ast_json = ASTProcessor.validate_ast(ast_json)
        if ast_json is None:
            print("[ERROR] AST validation failed. Returning None.")
            return None

        graph = nx.DiGraph()
        node_counter = 0  # Unique integer ID for each node

        def add_nodes_edges(node_json, parent_id=None):
            nonlocal node_counter

            if not isinstance(node_json, dict) or ("name" not in node_json and "nodeType" not in node_json):
                print(f"[WARNING] Skipping malformed AST node with keys: {list(node_json.keys())[:3]}")
                return None

            node_label = str(node_json.get("name", node_json.get("nodeType", "UNKNOWN"))).strip()

            node_id = node_counter  # Assign a unique counter to every node
            graph.add_node(node_id, label=node_label)
            node_counter += 1

            if parent_id is not None:
                graph.add_edge(parent_id, node_id)

            # Process children, depending on the structure
            for key in ["children", "nodes"]:
                for child in node_json.get(key, []):
                    if isinstance(child, dict):
                        add_nodes_edges(child, node_id)
                    else:
                        print("[WARNING] Ignoring non-dictionary child node.")

        add_nodes_edges(ast_json)

        if not graph.nodes:
            print("[ERROR] Graph contains no nodes. AST may be empty or improperly processed.")
            print(f"[DEBUG] AST keys: {list(ast_json.keys())}")  # Show only top-level keys
            return None

        return graph

    @staticmethod
    def compute_similarity(ast1, ast2):
        """
        Compute similarity between two ASTs using Weisfeiler-Lehman Graph Kernel.
        :param ast1: First AST JSON object.
        :param ast2: Second AST JSON object.
        :return: Similarity score between 0 and 1.
        """
        graph1 = ASTProcessor.build_ast_graph(ast1)
        graph2 = ASTProcessor.build_ast_graph(ast2)

        if graph1 is None or graph2 is None:
            print("[ERROR] One of the AST graphs is invalid.")
            return 0.0

        if not graph1.nodes or not graph2.nodes:
            print("[ERROR] One of the AST graphs has no nodes.")
            return 0.0

        gk = WeisfeilerLehman(n_iter=3, base_graph_kernel=VertexHistogram)

        try:
            # Convert networkx graphs to grakel graphs with labeled nodes
            graphs = list(
                grakel.graph_from_networkx(
                    [graph1, graph2], node_labels_tag="label"
                )
            )

            # Compute the Weisfeiler-Lehman kernel (similarity matrix)
            kernel_matrix = gk.fit_transform(graphs)
            similarity_score = kernel_matrix[0, 1]
            return round(similarity_score, 4)

        except Exception as e:
            print(f"[ERROR] Failed to compute similarity: {e}")
            return 0.0
