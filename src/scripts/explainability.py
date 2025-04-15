import argparse
import json
import os
import time

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.utils.EnvLoader import EnvLoader
from src.classes.xrag.LLMHandler import LLMHandler

# Load environment configuration.
EnvLoader(env_dir="src").load_env_files()

logger = DebugLogger()


def evaluate(path_to_contracts: str, model_name: str = None) -> None:
    """
    Evaluates Solidity contracts in the given directory by having the LLM classify and explain each contract.
    """
    if not os.path.isdir(path_to_contracts):
        logger.error(f"Directory not found: {path_to_contracts}")
        return

    # Use the directory name as the ground truth category (e.g., "reentrant" or "safe").
    gt_category = os.path.basename(os.path.normpath(path_to_contracts))

    # Create a unique log directory.
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_dir = os.path.join("logs", "baseline", f"{model_name}/{gt_category}_{timestamp}")
    os.makedirs(log_dir, exist_ok=True)

    # Get sorted list of Solidity files.
    files = sorted(os.listdir(path_to_contracts))
    total_files = len(files)

    if total_files == 0:
        logger.warning(f"No Solidity (.sol) files found in {path_to_contracts}.")
        return

    logger.info(f"Testing {model_name} on {total_files} files from category: {gt_category}")
    logger.info(f"Results will be logged at: {log_dir}")

    llm = LLMHandler()

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

        try:
            # Ask the LLM to classify and explain.
            answer = json.loads(llm.analyze_contract(contract_content).text)
        except Exception as e:
            logger.error(f"Error generating completion for file {filename}: {e}")
            continue

        # Write the structured output (as JSON) to a file in the log directory.
        output_path = os.path.join(log_dir, f"{filename.split('.')[0]}.json")
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
    logger.info(f"Final classification accuracy for {model_name} - '{gt_category}': {accuracy:.2%}")
    logger.debug(f"Processed {total_files} files. Final Accuracy: {accuracy:.2%}")


def main(args) -> None:
    """
    Main function to evaluate test datasets for both the 'reentrant' and 'safe' categories.
    """
    path_to_reentrant = os.path.join(args.dataset_path, "source", "reentrant")
    path_to_safe = os.path.join(args.dataset_path, "source", "safe")

    os.environ["MODEL_NAME"] = args.model_name

    evaluate(path_to_reentrant, args.model_name)
    evaluate(path_to_safe, args.model_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contract Analysis CLI for analyzing manually verified contracts.")
    parser.add_argument("--dataset-path", type=str, default="dataset/manually-verified",
                        help="Base path for the dataset.")
    parser.add_argument("--model-name", type=str, required=True, help="OpenAI or Google model name.",
                        choices=['gpt-4o', 'o3-mini', 'gemini-2.0-flash-lite', 'gemini-1.5-flash'])
    args = parser.parse_args()
    main(args)
