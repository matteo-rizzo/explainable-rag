import json
import os
import time

from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, Field

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.utils.EnvLoader import EnvLoader

# Load environment configuration.
EnvLoader(env_dir="src/config").load_env_files()


# Define a Pydantic model to enforce the structured output format.
class EvaluationResult(BaseModel):
    classification: str = Field(
        ...,
        description="The classification label indicating whether the contract is 'Reentrant' or 'Safe'."
    )
    explanation: str = Field(
        ...,
        description="A detailed explanation for the classification, citing specific lines or functions in the contract as evidence."
    )
    analysis: str = Field(
        ...,
        description="Key observations about the contract, including specific functions, external calls, and state update sequences."
    )


# Initialize the LLM (and set it into Settings, if needed elsewhere).
llm = OpenAI(model=os.getenv("OPENAI_MODEL_NAME_CHAT")).as_structured_llm(output_cls=EvaluationResult)
Settings.llm = llm

logger = DebugLogger()

# Updated prompt instructing the LLM on the required structured output.
EVAL_PROMPT = """
You must follow these steps precisely to evaluate the target Solidity contract:

1. **Classify the Contract**:
   - Classify the contract as **Reentrant** if it contains patterns or vulnerabilities matching reentrant behavior.
   - Classify the contract as **Safe** if it implements proper safeguards or mitigations that align with non-reentrant examples.

2. **Explain the Classification**:
   - Provide a detailed explanation for the classification, citing specific lines or functions in the contract.
   - Support your reasoning with evidence derived solely from the contract content.

### Input Contract:
"""


def evaluate(path_to_contracts: str) -> None:
    """
    Evaluates Solidity contracts in the given directory by having the LLM classify and explain each contract.

    Parameters:
        path_to_contracts (str): Path to a directory containing Solidity (.sol) contract files.
    """
    if not os.path.isdir(path_to_contracts):
        logger.error(f"Directory not found: {path_to_contracts}")
        return

    # Use the directory name as the ground truth category (e.g., "reentrant" or "safe").
    gt_category = os.path.basename(os.path.normpath(path_to_contracts))

    # Create a unique log directory.
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_dir = os.path.join("log", f"baseline_{gt_category}_{timestamp}")
    os.makedirs(log_dir, exist_ok=True)

    path_to_ast = path_to_contracts.replace("source", "ast")

    # Get sorted list of Solidity files.
    files = sorted(
        f.replace(".ast.json", ".sol") for f in os.listdir(path_to_ast)
        if f.endswith(".ast.json") and os.path.isfile(os.path.join(path_to_ast, f))
    )
    total_files = len(files)

    if total_files == 0:
        logger.warning(f"No Solidity (.sol) files found in {path_to_contracts}.")
        return

    logger.info(f"Testing LLM on {total_files} files from category: {gt_category}")
    logger.info(f"Results will be logged in: {log_dir}")

    correct = 0
    for index, filename in enumerate(files, start=1):
        path_to_file = os.path.join(path_to_contracts, filename)
        try:
            with open(path_to_file, 'r', encoding='latin-1') as file:
                contract_content = file.read()
        except Exception as e:
            logger.error(f"Error reading file {path_to_file}: {e}")
            continue

        logger.debug(f"[{index}/{total_files}] Processing file: {filename}")

        # Combine the evaluation prompt with the contract content.
        prompt = EVAL_PROMPT + contract_content

        try:
            # Ask the LLM to classify and explain.
            answer = json.loads(llm.complete(prompt).text)
        except Exception as e:
            logger.error(f"Error generating completion for file {filename}: {e}")
            continue

        # Write the structured output (as JSON) to a file in the log directory.
        output_path = os.path.join(log_dir, f"{filename}.json")
        try:
            with open(output_path, 'w', encoding='utf-8') as output_file:
                json.dump(answer, output_file, indent=4, ensure_ascii=True)
        except Exception as e:
            logger.error(f"Error writing output file {output_path}: {e}")

        # Check classification accuracy (using case-insensitive comparison).
        if answer["classification"].strip().lower() == gt_category.lower():
            correct += 1

        running_accuracy = correct / index
        logger.info(f"Processed {index}/{total_files} files. Running accuracy: {running_accuracy:.2%}")

    accuracy = correct / total_files
    logger.info(f"Final classification accuracy for '{gt_category}': {accuracy:.2%}")
    logger.debug(f"Processed {total_files} files. Final Accuracy: {accuracy:.2%}")


def main() -> None:
    """
    Main function to evaluate test datasets for both the 'reentrant' and 'safe' categories.
    """
    path_to_data_test = os.path.join("dataset", "manually-verified-test", "source")
    path_to_test_reentrant = os.path.join(path_to_data_test, "reentrant")
    path_to_test_safe = os.path.join(path_to_data_test, "safe")

    evaluate(path_to_test_reentrant)
    evaluate(path_to_test_safe)


if __name__ == "__main__":
    main()
