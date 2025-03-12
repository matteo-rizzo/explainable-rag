import json
import os
from collections import defaultdict
from tqdm import tqdm

def load_classification_results(base_path):
    """
    Load classification results from the directory structure:
    baseline > model_name > groundtruth_folder (reentrant/safe) > contract_id_json
    """
    misclassified = defaultdict(lambda: {
        "total": 0,
        "reentrant": 0,
        "safe": 0,
        "misclassified_reentrant": 0,
        "misclassified_safe": 0,
        "misclassified_contracts": []
    })

    models = [model for model in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, model))]

    for model in tqdm(models, desc=f"Processing models in {base_path}", leave=False):
        model_path = os.path.join(base_path, model)

        for groundtruth in ['reentrant', 'safe']:
            groundtruth_path = os.path.join(model_path, groundtruth)
            if not os.path.isdir(groundtruth_path):
                continue

            contract_files = [f for f in os.listdir(groundtruth_path) if f.endswith(".json")]
            misclassified[model][groundtruth] += len(contract_files)
            misclassified[model]["total"] += len(contract_files)

            for contract_file in tqdm(contract_files, desc=f"Checking {model} in {groundtruth}", leave=False):
                contract_path = os.path.join(groundtruth_path, contract_file)
                try:
                    with open(contract_path, 'r') as f:
                        data = json.load(f)
                        contract_id = contract_file.replace(".sol.json", "")
                        predicted_label = data.get("classification").lower()

                        # If model prediction does not match the ground truth, log the contract ID
                        if predicted_label != groundtruth:
                            if groundtruth == "reentrant":
                                misclassified[model]["misclassified_reentrant"] += 1
                            else:
                                misclassified[model]["misclassified_safe"] += 1
                            misclassified[model]["misclassified_contracts"].append({
                                "contract_id": contract_id,
                                "groundtruth": groundtruth,
                                "predicted": predicted_label
                            })
                except Exception as e:
                    print(f"Error processing {contract_path}: {e}")

    return misclassified

def save_misclassified_results(misclassified, output_file):
    """
    Save misclassified results to a JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(misclassified, f, indent=4)
    print(f"Misclassified contract IDs saved to {output_file}")

def print_misclassification_stats(misclassified):
    """
    Print misclassification statistics for each model.
    """
    print("\nMisclassification Statistics:")
    for model, stats in misclassified.items():
        print(f"Model: {model}")
        print(f"  Total Contracts: {stats['total']}")
        print(f"  Reentrant: {stats['reentrant']}, Safe: {stats['safe']}")
        print(f"  Misclassified Reentrant: {stats['misclassified_reentrant']}, Misclassified Safe: {stats['misclassified_safe']}")
        print(f"  Misclassified Contracts: {len(stats['misclassified_contracts'])}")

if __name__ == "__main__":
    BASE_DIR = "explanations/baseline"  # Update this with the actual path
    OUTPUT_FILE = "misclassified_contracts_baseline.json"

    misclassified_results = load_classification_results(BASE_DIR)
    save_misclassified_results(misclassified_results, OUTPUT_FILE)
    print_misclassification_stats(misclassified_results)
