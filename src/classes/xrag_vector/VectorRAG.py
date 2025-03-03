from llama_index.core import StorageContext

from src.classes.xrag_vector.RAG import RAG
from src.classes.xrag_vector.VectorManager import VectorManager


class VectorRAG(RAG):
    """
    A specialized implementation of the Retrieval-Augmented Generation (RAG) pipeline
    that focuses on vector-based document retrieval.

    This class integrates vector-based storage and retrieval functionality, supporting
    efficient query execution and management of vector embeddings.
    """

    def __init__(self) -> None:
        """
        Initializes the VectorRAG pipeline by setting up components for vector-based retrieval.
        """
        super().__init__()

    def _initialize_managers(self) -> None:
        """
        Configures the vector manager and its associated storage context.

        This method sets up the vector store and initializes the vector manager,
        enabling efficient storage, retrieval, and management of vector embeddings.

        :raises Exception:
            Logs any errors encountered during the initialization process.
        """
        try:
            self.logger.info("Initializing vector manager...")

            # Create the vector store and its associated storage context
            vector_store = self.db_manager.create_vector_store()
            vector_storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # Initialize the VectorManager with the configured store and context
            self.knowledge_manager = VectorManager(vector_store, vector_storage_context)

            self.logger.success("Vector manager initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize vector manager: {e}", exc_info=True)
