import os
from typing import Optional, List

from llama_index.core import Document, SimpleDirectoryReader, Response
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.schema import NodeWithScore

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.xrag_vector.Neo4jDBManager import Neo4jDBManager


class RAG:
    """
    A hybrid retrieval pipeline utilizing Neo4j for both vector-based document retrieval
    and knowledge graph storage. Supports structured and unstructured query handling.
    """

    def __init__(self, logger: Optional[DebugLogger] = None, db_manager: Optional[Neo4jDBManager] = None) -> None:
        """
        Initializes the RAG pipeline with components for graph and vector-based retrieval.

        :param db_manager: Instance of Neo4jDBManager for database interaction (optional).
        """
        self.logger = logger or DebugLogger(use_panel_for_errors=True)
        self.db_manager = db_manager or Neo4jDBManager()
        self.chat_engine = None
        self.knowledge_manager = None
        self._initialize_managers()

    def _initialize_managers(self) -> None:
        """
        Initializes necessary managers (e.g., RAG Manager).
        Placeholder for future initialization logic.
        """
        # Example initialization (Replace with actual manager setup)
        self.logger.info("Initializing RAG managers...")
        # self.knowledge_manager = RAGManager(self.db_manager)

    def load_and_index_documents(self, folder_path: str, reload_index: bool = False) -> None:
        """
        Loads, chunks, and indexes documents into the Neo4j vector store and knowledge graph.

        :param folder_path: Path to the folder containing document files.
        :param reload_index: If True, reloads the index regardless of existing data.
        """
        self.logger.info(f"{'Reloading' if reload_index else 'Loading'} documents from: {folder_path}")

        docs = [] if reload_index else self._load_docs(folder_path)

        if not docs and not reload_index:
            self.logger.warning("No documents available for indexing.")
            return

        self._index(docs, reload_index=reload_index)

    @staticmethod
    @DebugLogger.profile
    def _load_docs(folder_path: str) -> List[Document]:
        """
        Loads documents from the specified folder.

        :param folder_path: Path to the folder containing document files.
        :return: List of loaded Document objects.
        """
        category = folder_path.split(os.sep)[-1]
        metadata_fn = lambda x: {"file_name": x.split(os.sep)[-1], "category": category}
        reader = SimpleDirectoryReader(input_dir=folder_path, errors="strict", encoding="latin-1",
                                       file_metadata=metadata_fn)
        docs = reader.load_data(show_progress=True)
        return docs

    @DebugLogger.profile
    def _index(self, docs: List[Document], reload_index: bool) -> None:
        """
        Indexes the given documents in the vector store.

        :param docs: List of Document objects to index.
        :param reload_index: If True, reloads the index.
        """
        try:
            self.logger.info("Indexing documents into Neo4j...")
            self.knowledge_manager.index_documents(docs, reload_index)
            self.logger.success("Document indexing completed successfully.")
        except Exception as e:
            self.logger.error(f"Error during indexing: {e}", exc_info=True)

    def _initialize_chat_engine(self) -> None:
        """
        Sets up the RAG chat engine for document retrieval.
        """
        try:
            self.logger.info("Initializing chat engine...")
            self.knowledge_manager.create_chat_engine()
            self.chat_engine = self.knowledge_manager.get_query_engine()
            self.logger.success("Query engine initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize chat engine: {e}", exc_info=True)

    @DebugLogger.profile
    def query(self, question: str) -> Optional[Response]:
        """
        Executes a query using the vector store.

        :param question: The input query as a string.
        :return: Query response or None in case of an error.
        """
        if not self.chat_engine:
            self._initialize_chat_engine()

        try:
            self.logger.debug(f"Executing query: {question}")
            response = self.knowledge_manager.execute_query(question)
            self.logger.success("Query executed successfully.")
            return response
        except Exception as e:
            self.logger.error(f"Error during query execution: {e}", exc_info=True)
            return None

    @staticmethod
    def fetch_sources(nodes: List[NodeWithScore]) -> List[str]:
        """
        Filters nodes by similarity score and extracts unique source filenames.

        :param nodes: List of nodes from the query response.
        :return: List of unique filenames from filtered nodes.
        """
        processor = SimilarityPostprocessor(similarity_cutoff=0.5)
        filtered_nodes = processor.postprocess_nodes(nodes)
        return list({node.node.metadata["file_name"] for node in filtered_nodes if "file_name" in node.node.metadata})

    @staticmethod
    def fetch_source_nodes(nodes: List[NodeWithScore]) -> List[NodeWithScore]:
        """
        Filters nodes by similarity score and extracts unique source filenames.

        :param nodes: List of nodes from the query response.
        :return: List of unique filenames from filtered nodes.
        """
        processor = SimilarityPostprocessor(similarity_cutoff=0.5)
        return processor.postprocess_nodes(nodes)
