import json
import os

# Define paths
MISCLASSIFIED_FILE = "misclassified_contracts_union_intersection.json"
BASELINE_FOLDER = "explanations/baseline"
COMPARISON_FOLDER = "explanations/models_comparison"
DATASET_SOURCE_FOLDER = "dataset/manually-verified-test/source"
OUTPUT_FOLDER = "results"


def load_misclassified_data(file_path):
    """Load misclassified contracts from JSON file."""
    print(f"Loading misclassified contracts from {file_path}...")
    with open(file_path, "r") as f:
        return json.load(f)


def load_baseline_explanation(model, groundtruth_label, contract_id):
    """Load explanation from baseline/model/groundtruth/contract_id.sol.json."""
    explanation_file = os.path.join(BASELINE_FOLDER, model, groundtruth_label, f"{contract_id}.sol.json")

    if os.path.exists(explanation_file):
        try:
            with open(explanation_file, "r") as f:
                data = json.load(f)
                return data.get("explanation", "No explanation found")
        except Exception as e:
            print(f"Error reading {explanation_file}: {e}")
            return "Error loading explanation"

    return "No explanation found"


def load_comparison_explanation(model, data_type, groundtruth_label, contract_id):
    """Load explanation from models_comparison/model/data_type/groundtruth/classification.json."""
    explanation_file = os.path.join(COMPARISON_FOLDER, model, data_type, groundtruth_label, contract_id,
                                    "classification.json")

    if os.path.exists(explanation_file):
        try:
            with open(explanation_file, "r") as f:
                data = json.load(f)
                return data.get("explanation", "No explanation found")
        except Exception as e:
            print(f"Error reading {explanation_file}: {e}")
            return "Error loading explanation"

    return "No explanation found"


def load_contract_source(groundtruth_label, contract_id):
    """Load the source code of a contract from dataset folder."""
    contract_path = os.path.join(DATASET_SOURCE_FOLDER, groundtruth_label, f"{contract_id}.sol")

    if os.path.exists(contract_path):
        try:
            with open(contract_path, "r", encoding="latin1") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading source code for {contract_id}: {e}")
            return "Error loading source code"
    return "Source code not found"


def process_results(misclassified_data):
    """Process misclassified contracts and organize them into structured folders."""
    print("Processing misclassified contracts...")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for model, data_types in misclassified_data.items():
        print(f"Processing model: {model}")

        for data_type, groundtruths in data_types["intersection"].items():
            for groundtruth_label, contract_ids in groundtruths.items():
                for contract_id in contract_ids:
                    # Create folder structure
                    output_dir = os.path.join(OUTPUT_FOLDER, model, data_type, groundtruth_label)
                    os.makedirs(output_dir, exist_ok=True)

                    # Load explanations
                    baseline_explanation = load_baseline_explanation(model, groundtruth_label, contract_id)
                    comparison_explanation = load_comparison_explanation(model, data_type, groundtruth_label,
                                                                         contract_id)

                    # Load source code
                    contract_source = load_contract_source(groundtruth_label, contract_id)

                    # Save results
                    output_file = os.path.join(output_dir, f"{contract_id}.json")
                    contract_data = {
                        "contract_id": contract_id,
                        "groundtruth": groundtruth_label,
                        "model_classification": "misclassified",
                        "baseline_explanation": baseline_explanation,
                        "comparison_explanation": comparison_explanation,
                        "source_code": contract_source
                    }

                    with open(output_file, "w") as f:
                        json.dump(contract_data, f, indent=4)

    print("Processing completed. Data saved to results/.")


if __name__ == "__main__":
    misclassified_data = load_misclassified_data(MISCLASSIFIED_FILE)
    process_results(misclassified_data)
