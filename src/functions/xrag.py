import json
from pathlib import Path
from typing import Any, Dict, Tuple, Optional, List

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.xrag.ContractFileProcessor import ContractFileProcessor
from src.classes.xrag.Document import Document
from src.classes.xrag.LLMHandler import LLMHandler
from src.classes.xrag.Retriever import Retriever


def _save_json(file_path: Path, data: Dict[str, Any], logger: DebugLogger) -> None:
    """
    Helper function to save data as JSON to a file.

    :param file_path: Path where the JSON file should be saved.
    :param data: Dictionary to be saved.
    :param logger: Logger instance for logging errors.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved: {file_path}")
    except IOError as e:
        logger.error(f"Failed to save results to {file_path}: {e}")


def process_input_contract_worker(args: Tuple) -> Optional[str]:
    """
    Worker function for processing a single input contract.
    This function is defined at the module level so that it can be pickled.

    :param args: Tuple containing input document metadata, directories, retriever docs, etc.
    :return: Contract ID if processing was successful, None otherwise.
    """
    logger = DebugLogger()

    try:
        (
            input_doc,
            retriever_docs_data,
            input_dirs,
            candidate_dirs,
            log_dir,
            mode,
        ) = args

        input_doc = Document.from_dict(input_doc)
        contract_id = input_doc.metadata.get("contract_id", "unknown").split(".")[0]
        label = input_doc.metadata.get("label", "unknown")

        logger.info(f"Processing contract: {contract_id} (Label: {label})")

        # Load source code
        source_code = ContractFileProcessor.load_source_code(contract_id, input_dirs["src"], label)
        logger.debug(f"Loaded source code for contract {contract_id}.")

        # Create contract-specific log directory
        local_log_dir = Path(log_dir) / label / contract_id
        local_log_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created log directory: {local_log_dir}")

        # Convert retriever docs from dicts to Document objects
        retriever_docs = [Document.from_dict(doc) for doc in retriever_docs_data]

        # Retrieve similar documents
        retriever = Retriever(retriever_docs, similarity_mode=mode)
        similar_docs = retriever.retrieve(input_doc, k=3)

        # Initialize LLM handler
        llm_processor = LLMHandler()

        # Retrieve similar documents and analyze
        similar_contexts: List[str] = []
        logger.info(f"Retrieving similar documents for contract {contract_id}.")

        for doc in similar_docs:
            similar_id = doc.metadata.get("contract_id", "unknown").split(".")[0]
            similar_label = doc.metadata.get("label", "unknown")

            try:
                similar_source_code = ContractFileProcessor.load_source_code(
                    similar_id, candidate_dirs["src"], similar_label
                )

                # Analyze similar contract using LLM
                analysis_response = llm_processor.analyze_similar_contract(similar_source_code, similar_label)

                similar_contexts.append(
                    f"### {similar_id} - Label {similar_label}\n#### Analysis:\n{analysis_response}\n\n"
                )

                logger.debug(f"Analyzed similar contract {similar_id} (Label: {similar_label}).")

                # Save individual analysis
                _save_json(
                    local_log_dir / f"analysis_{similar_id}.json",
                    {
                        "contract_id": similar_id,
                        "label": similar_label,
                        "analysis": str(analysis_response),
                    },
                    logger,
                )

            except Exception as e:
                logger.warning(f"Skipping similar contract {similar_id} due to error: {e}")

        # Analyze the input contract using the gathered similar contexts
        try:
            response = llm_processor.analyze_contract(source_code, similar_contexts)

            # Parse LLM response safely
            response_data = json.loads(response.text) if isinstance(response.text, str) else response

            classification = response_data.get("classification", "unknown")
            explanation = response_data.get("explanation", "No explanation provided.")

            logger.info(f"Classification completed for contract {contract_id}.")
        except Exception as e:
            logger.error(f"Error during classification for contract {contract_id}: {e}")
            return None

        # Save final classification results
        _save_json(
            local_log_dir / "classification.json",
            {
                "contract_id": contract_id,
                "label": label,
                "classification": classification,
                "explanation": explanation,
            },
            logger,
        )

        return contract_id

    except Exception as e:
        logger.error(f"Unexpected error in processing contract: {e}")
        return None
