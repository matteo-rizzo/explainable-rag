import argparse
import os
import sys

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.utils.EnvLoader import EnvLoader
from src.classes.xrag.ContractAnalyzer import ContractAnalyzer

# Load environment variables
EnvLoader(env_dir="src/config").load_env_files()


def parse_args():
    """
    Parses command-line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Contract Analysis CLI for analyzing manually verified contracts."
    )

    parser.add_argument(
        "--dataset-path",
        type=str,
        default="dataset/manually-verified-{}",
        help="Base path for the dataset, with '{}' as a placeholder for dataset type.",
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["ast_cfg", "ast", "cfg"],
        default="ast_cfg",
        help="Mode of analysis. Options: 'ast_cfg', 'ast', 'cfg'. Default: 'cfg'.",
    )

    parser.add_argument(
        "--model-name",
        type=str,
        help="OpenAI model name for processing. Example: 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'. Defaults to openai.env",
    )

    parser.add_argument(
        "--use-multiprocessing",
        action="store_true",
        help="Enable multiprocessing for contract analysis.",
    )

    return parser.parse_args()


def main():
    """
    Main script to initialize and run the ContractAnalyzer.
    """
    logger = DebugLogger()
    args = parse_args()

    try:
        # Set OpenAI model name as an environment variable
        os.environ["OPENAI_MODEL_NAME_CHAT"] = args.model_name

        # Initialize ContractAnalyzer with user-defined arguments
        analyzer = ContractAnalyzer(
            dataset_base=args.dataset_path,
            mode=args.mode,
            model=args.model_name,
            use_multiprocessing=args.use_multiprocessing,
        )

        # Start contract analysis
        logger.info(f"Starting contract analysis in '{args.mode}' mode with model '{args.model_name}'...")
        analyzer.analyze_contracts()
        logger.info("Contract analysis completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during contract analysis: {e}")
        sys.exit(1)  # Exit with a non-zero code on failure


if __name__ == "__main__":
    main()
