import os

from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore

from src.classes.utils.DebugLogger import DebugLogger


class Neo4jDBManager:
    """
    Manages the configuration and creation of Neo4j graph and vector stores.
    """

    def __init__(self, url: str = None, username: str = None, password: str = None, database: str = None):
        """
        Initialize Neo4j connection parameters.

        :param url: The URL for the Neo4j instance, defaults to "bolt://localhost:7687".
        :param username: Username for Neo4j authentication, defaults to "neo4j".
        :param password: Password for Neo4j authentication, retrieved from environment if not provided.
        :param database: Name of the Neo4j database, defaults to "neo4j".
        """
        self.logger = DebugLogger(use_panel_for_errors=True)
        self.url = url or os.getenv("NEO4J_URL", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")

        self._validate_password()
        self.logger.success(f"Neo4jDBManager initialized with URL: '{self.url}', Database: '{self.database}'.")

    def _validate_password(self):
        """
        Validate that a Neo4j password is set.

        :raises ValueError: If the password is not provided.
        """
        if not self.password:
            error_message = (
                "Neo4j password is required. Set it in the environment or pass it directly."
            )
            self.logger.error(error_message)
            raise ValueError(error_message)

    def create_graph_store(self) -> Neo4jPropertyGraphStore:
        """
        Create and return a Neo4jPropertyGraphStore instance.

        :return: Configured Neo4jPropertyGraphStore instance.
        """
        return self._create_store(Neo4jPropertyGraphStore, "Neo4jPropertyGraphStore")

    def create_vector_store(self, embedding_dimension: int = 384, hybrid_search: bool = True) -> Neo4jVectorStore:
        """
        Create and return a Neo4jVectorStore instance.

        :param embedding_dimension: Dimension of embeddings, defaults to 1536.
        :param hybrid_search: Enables hybrid search, defaults to True.
        :return: Configured Neo4jVectorStore instance.
        """
        return self._create_store(
            Neo4jVectorStore,
            "Neo4jVectorStore",
            embedding_dimension=embedding_dimension,
            hybrid_search=hybrid_search,
        )

    def _create_store(self, store_class: type, store_name: str, **kwargs):
        """
        Helper method to create a store instance with the provided configuration.

        :param store_class: The class of the store to be created.
        :param store_name: The name of the store, used for logging purposes.
        :param kwargs: Additional configuration parameters for the store.
        :return: Configured store instance.
        :raises RuntimeError: If store creation fails.
        """
        try:
            store_instance = store_class(
                username=self.username,
                password=self.password,
                url=self.url,
                database=self.database,
                **kwargs,
            )
            self.logger.success(f"{store_name} instance created successfully.")
            return store_instance
        except Exception as e:
            error_message = f"Failed to create {store_name}: {e}"
            self.logger.error(error_message)
            raise RuntimeError(error_message) from e
