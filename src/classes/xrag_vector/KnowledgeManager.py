from abc import ABC, abstractmethod
from typing import Optional, List

from llama_index.core import StorageContext, Document
from llama_index.core.chat_engine.types import BaseChatEngine, AgentChatResponse
from llama_index.core.indices.base import BaseIndex
from llama_index.core.vector_stores.types import VectorStore

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.xrag_vector.UnstructuredTransform import UnstructuredTransform


class KnowledgeManager(ABC):
    """
    Abstract base class for managing indexing, retrieval, and querying of knowledge data.
    Provides methods for indexing documents, creating a chat engine, and executing queries.
    """

    def __init__(self, store: VectorStore, storage_context: StorageContext) -> None:
        """
        Initialize the KnowledgeManager with a store and storage context.

        :param store: The storage backend for managing knowledge data.
        :param storage_context: Configuration context for the storage backend.
        """
        self.store = store
        self.storage_context = storage_context
        self.persist_dir: str = ""
        self.index: Optional[BaseIndex] = None
        self.chat_engine: Optional[BaseChatEngine] = None
        self.logger = DebugLogger(use_panel_for_errors=True)

    def get_index(self) -> Optional[BaseIndex]:
        """
        Get the current index, if available.

        :return: The current index or None if not initialized.
        """
        return self.index

    def get_query_engine(self) -> Optional[BaseChatEngine]:
        """
        Get the current chat engine, if available.

        :return: The current chat engine or None if not initialized.
        """
        return self.chat_engine

    def index_documents(self, documents: List[Document], reload_index: bool = False) -> None:
        """
        Index a list of documents into the knowledge store.

        :param documents: List of Document objects to be indexed.
        :param reload_index: Whether to reload an existing index if available.
        :raises Exception: If an error occurs during indexing.
        """
        try:
            if reload_index and self.load_index():
                self.logger.success("Index loaded successfully. Skipping re-indexing.")
                return

            if self.index:
                self.refresh_index(documents)

            self.logger.info("Starting document indexing... This may take a while.")
            self.create_index(documents)
            self.logger.success("Document indexing completed successfully.")
        except Exception as e:
            self.logger.error("Error during document indexing:", exc_info=True)
            raise

    def refresh_index(self, documents: List[Document]):
        try:
            if not self.index and self.load_index():
                self.logger.success("Index loaded successfully.")

            self.logger.info("Re-indexing with new documents.")
            self.index.refresh(documents, transformations=[UnstructuredTransform()])

        except Exception as e:
            self.logger.error("Error during new document indexing:", exc_info=True)
            raise

    def create_chat_engine(self) -> None:
        """
        Initialize the chat engine using the current retriever.

        :raises ValueError: If the chat engine setup fails.
        """
        if not self.index:
            error_message = "Cannot create chat engine: Index is not initialized."
            self.logger.error(error_message)
            raise ValueError(error_message)

        try:
            self.chat_engine = self.index.as_chat_engine(verbose=False)
            self.logger.success("Query engine initialized successfully.")
        except Exception as e:
            error_message = f"Failed to initialize chat engine: {e}"
            self.logger.error(error_message, exc_info=True)
            raise ValueError(error_message) from e

    def execute_query(self, query: str) -> Optional[AgentChatResponse]:
        """
        Execute a query on the knowledge store and return the result.

        :param query: The query string to execute.
        :return: The response object if the query is successful, or None otherwise.
        """
        if not self.chat_engine:
            self.logger.info("Query engine not initialized. Creating a new chat engine...")
            self.create_chat_engine()

        try:
            return self.chat_engine.chat(query)
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}", exc_info=True)
            return None

    @abstractmethod
    def create_index(self, documents: List[Document]) -> None:
        """
        Abstract method to create an index from a list of documents.

        :param documents: List of Document objects to be indexed.
        """
        pass

    @abstractmethod
    def load_index(self) -> bool:
        """
        Abstract method to load an existing index from storage.

        :return: True if the index was loaded successfully, False otherwise.
        """
        pass
