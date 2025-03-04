from typing import List, Any, Dict

from tqdm import tqdm

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.xrag.SimilarityCalculator import SimilarityCalculator


class Retriever:
    def __init__(self, documents: List[Any], similarity_mode: str = "ast_cfg", weights: Dict[str, float] = None):
        """
        Initializes the Retriever with a list of documents and a similarity calculator.

        :param documents: List of documents to retrieve from.
        :param similarity_mode: The mode used for similarity calculation.
        :param weights: Optional weights for similarity computation.
        """
        self.logger = DebugLogger()
        self.documents = documents
        self.similarity_mode = similarity_mode
        self.similarity_calculator = SimilarityCalculator(similarity_mode, weights)

        self.logger.info(f"Retriever initialized with {len(documents)} documents, similarity_mode='{similarity_mode}'")

    def retrieve(self, input_doc: Any, k: int = 3) -> List[Any]:
        """
        Retrieves the top-k most similar documents to the input document.

        :param input_doc: The document used as the query.
        :param k: Number of documents to retrieve.
        :return: List of top-k most similar documents.
        """
        input_json = input_doc.metadata.get("json", {})
        if self.similarity_mode != "ast_cfg":
            input_json = input_json[self.similarity_mode]

        scored_docs = []
        for doc in tqdm(self.documents, desc="Retrieving documents"):
            candidate_json = doc.metadata.get("json", {})
            if self.similarity_mode != "ast_cfg":
                candidate_json = candidate_json[self.similarity_mode]
            score = self.similarity_calculator.compute_similarity(input_json, candidate_json)
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_k_docs = [doc for _, doc in scored_docs[:k]]

        self.logger.info(f"Retrieved top {k} documents.")
        for score, doc in scored_docs[:k]:
            doc_id = doc.metadata.get("contract_id", "unknown").split(".")[0]
            label = doc.metadata.get("label", "unknown")
            self.logger.debug("Contract ID ({}): {} - Score {}".format(label, doc_id, score))

        return top_k_docs
