import json
import sqlite3
from typing import Optional, List, Dict

from tqdm import tqdm

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.xrag.Document import Document


class KnowledgeBase:
    """
    A class to manage a knowledge base of smart contracts using an SQLite database.
    """

    def __init__(self, db_path: str = "knowledge_base.db"):
        """
        Initialize the knowledge base.

        :param db_path: Path to the SQLite database file.
        """
        self.logger = DebugLogger()
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        """
        Initialize the SQLite database and ensure the smart_contracts table exists.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Enable WAL mode for better performance
                cursor.execute("PRAGMA journal_mode=WAL;")

                # Ensure the table exists first
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS smart_contracts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        contract_id TEXT UNIQUE NOT NULL,
                        source_files TEXT NOT NULL,
                        json_content TEXT NOT NULL,
                        label TEXT
                    )
                """)

                cursor.execute("CREATE INDEX IF NOT EXISTS idx_contract_id ON smart_contracts (contract_id)")
                conn.commit()

                # Check for missing columns and add them dynamically
                cursor.execute("PRAGMA table_info(smart_contracts)")
                existing_columns = {row[1] for row in cursor.fetchall()}  # Extract column names

                if "label" not in existing_columns:
                    self.logger.warning("Column 'label' is missing in the database. Adding it now...")
                    cursor.execute("ALTER TABLE smart_contracts ADD COLUMN label TEXT")
                    conn.commit()
                    self.logger.info("Column 'label' added successfully.")

                self.logger.info("Database initialized successfully.")

        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise

    def clear_contracts(self) -> None:
        """
        Clear all stored contracts from the database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM smart_contracts")
                conn.commit()
            self.logger.info("Cleared all contracts from the database.")
        except sqlite3.Error as e:
            self.logger.error(f"Error clearing database: {e}")

    def store_combined_contract(self, contract_id: str, source_files: List[str], combined_json: Dict,
                                label: Optional[str] = None) -> None:
        """
        Store a combined contract (merged AST and/or CFG) along with its label into the database.

        :param contract_id: Unique identifier of the smart contract.
        :param source_files: List of source file paths.
        :param combined_json: Merged AST and/or CFG data in JSON format.
        :param label: Label associated with the contract (e.g., "safe", "reentrant").
        """
        try:
            source_files_json = json.dumps(source_files)
            json_str = json.dumps(combined_json)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO smart_contracts (contract_id, source_files, json_content, label)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(contract_id) DO UPDATE SET
                    source_files = excluded.source_files,
                    json_content = excluded.json_content,
                    label = excluded.label
                """, (contract_id, source_files_json, json_str, label))
                conn.commit()

            self.logger.info(f"Stored contract '{contract_id}' with label '{label}' from files: {source_files}")
        except sqlite3.Error as e:
            self.logger.error(f"Error storing contract '{contract_id}': {e}")

    def load_all_contracts(self) -> List[Document]:
        """
        Load all stored contracts from the database and convert them to Document objects.

        :return: A list of Document objects.
        """
        documents = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT contract_id, source_files, json_content, label FROM smart_contracts")
                rows = cursor.fetchall()

            for contract_id, source_files_json, json_str, label in tqdm(rows, desc="Loading contracts"):
                json_data = json.loads(json_str)
                doc = Document(
                    text=json.dumps(json_data, indent=2),
                    metadata={
                        "contract_id": contract_id,
                        "source_files": json.loads(source_files_json),
                        "json": json_data,
                        "label": label
                    }
                )
                documents.append(doc)

        except sqlite3.Error as e:
            self.logger.error(f"Error loading contracts: {e}")
        return documents
