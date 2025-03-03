from typing import Dict, Any

from src.classes.xrag.ASTProcessor import ASTProcessor
from src.classes.xrag.CFGProcessor import CFGProcessor


class SimilarityCalculator:
    def __init__(self, similarity_mode: str = "aggregated", weights: Dict[str, float] = None):
        self.similarity_mode = similarity_mode.lower()
        self.weights = weights if weights else {"ast": 0.5, "cfg": 0.5}

    def compute_similarity(self, json1: Dict[str, Any], json2: Dict[str, Any]) -> float:
        if self.similarity_mode == "ast":
            return ASTProcessor.compute_similarity(json1, json2)
        elif self.similarity_mode == "cfg":
            return CFGProcessor.compute_similarity(json1, json2)
        elif self.similarity_mode == "aggregated":
            return self.aggregated_similarity(json1, json2)
        else:
            raise ValueError(f"Unknown similarity mode: {self.similarity_mode}")

    def aggregated_similarity(self, json1: Dict[str, Any], json2: Dict[str, Any]) -> float:
        ast1, cfg1 = json1.get("ast", {}), json1.get("cfg", {})
        ast2, cfg2 = json2.get("ast", {}), json2.get("cfg", {})

        sim_ast = ASTProcessor.compute_similarity(ast1, ast2)
        sim_cfg = CFGProcessor.compute_similarity(cfg1, cfg2)

        return (self.weights["ast"] * sim_ast) + (self.weights["cfg"] * sim_cfg)
