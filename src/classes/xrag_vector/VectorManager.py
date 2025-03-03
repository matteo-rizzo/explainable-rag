from typing import List

from llama_index.core import StorageContext, Document, VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStore

from src.classes.xrag_vector.KnowledgeManager import KnowledgeManager
from src.classes.xrag_vector.UnstructuredTransform import UnstructuredTransform


class VectorManager(KnowledgeManager):
    """
    Manages vector store operations, including document indexing, retrieval,
    and querying within a vector-based storage system.
    """

    def __init__(self, store: VectorStore, storage_context: StorageContext) -> None:
        """
        Initialize the VectorManager with a vector storage backend and context configuration.

        :param store: The vector store used for managing indexed data.
        :param storage_context: Context or configuration for managing vector storage.
        """
        super().__init__(store, storage_context)
        self.persist_dir = "vector_index"
        self.logger.info("VectorManager initialized with vector storage backend.")

    def create_index(self, documents: List[Document]) -> None:
        """
        Index a list of documents into the vector store.

        :param documents: List of Document objects to be indexed.
        """
        self.logger.info("Starting vector document indexing... This may take a while.")

        try:
            # Create the vector index with the given documents and context
            self.index = VectorStoreIndex.from_documents(
                documents=documents,
                storage_context=self.storage_context,
                show_progress=True,
                store_nodes_override=True,
                transformations=[UnstructuredTransform()]
            )

            # Debugging output for indexed documents
            self.logger.debug(f"Indexed documents: {self.index.storage_context.docstore.docs}")
            self.logger.success("Vector document indexing completed successfully.")
        except Exception as e:
            self.logger.error("Error occurred during vector document indexing:", exc_info=True)
            raise RuntimeError("Vector document indexing failed.") from e

    def load_index(self) -> bool:
        """
        Load the index from the vector store if available.

        :return: True if the index was successfully loaded, False otherwise.
        """
        try:
            self.logger.info("Attempting to load the index from the vector store.")
            self.index = VectorStoreIndex.from_vector_store(vector_store=self.store)
            self.logger.success("Index loaded successfully from the vector store.")
            return True
        except Exception as e:
            self.logger.error("Error occurred while loading the index:", exc_info=True)
            return False
