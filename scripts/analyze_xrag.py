import json
import os
from collections import defaultdict

def load_classification_results(base_path):
    """
    Load classification results from the directory structure:
    baseline > model_name > data_type (ast/cfg/ast_cfg) > groundtruth_folder (reentrant/safe) > contract_id_folder > classification.json
    """
    misclassified = defaultdict(lambda: {
        "total": 0,
        "reentrant": 0,
        "safe": 0,
        "misclassified_reentrant": 0,
        "misclassified_safe": 0,
        "misclassified_by_data_type": defaultdict(lambda: {"reentrant": {"misclassified": 0, "total": 0}, "safe": {"misclassified": 0, "total": 0}}),
        "misclassified_contracts": []
    })

    for model in os.listdir(base_path):
        model_path = os.path.join(base_path, model)
        if not os.path.isdir(model_path):
            continue

        for data_type in os.listdir(model_path):
            data_type_path = os.path.join(model_path, data_type)
            if not os.path.isdir(data_type_path):
                continue

            for groundtruth in ['reentrant', 'safe']:
                groundtruth_path = os.path.join(data_type_path, groundtruth)
                if not os.path.isdir(groundtruth_path):
                    continue

                for contract_id in os.listdir(groundtruth_path):
                    contract_id_path = os.path.join(groundtruth_path, contract_id)
                    classification_file = os.path.join(contract_id_path, "classification.json")

                    if not os.path.isfile(classification_file):
                        continue

                    try:
                        with open(classification_file, 'r') as f:
                            data = json.load(f)
                            predicted_label = data.get("classification", "").lower()

                            misclassified[model][groundtruth] += 1
                            misclassified[model]["total"] += 1
                            misclassified[model]["misclassified_by_data_type"][data_type][groundtruth]["total"] += 1

                            if predicted_label != groundtruth:
                                if groundtruth == "reentrant":
                                    misclassified[model]["misclassified_reentrant"] += 1
                                else:
                                    misclassified[model]["misclassified_safe"] += 1
                                misclassified[model]["misclassified_by_data_type"][data_type][groundtruth]["misclassified"] += 1
                                misclassified[model]["misclassified_contracts"].append({
                                    "contract_id": contract_id,
                                    "groundtruth": groundtruth,
                                    "predicted": predicted_label,
                                    "data_type": data_type
                                })
                    except Exception as e:
                        print(f"Error processing {classification_file}: {e}")

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
        print(
            f"  Misclassified Reentrant: {stats['misclassified_reentrant']}, Misclassified Safe: {stats['misclassified_safe']}")
        print(f"  Misclassified Contracts: {len(stats['misclassified_contracts'])}")
        print("  Misclassification by Data Type and Groundtruth:")
        for data_type, groundtruth_stats in stats["misclassified_by_data_type"].items():
            print(f"    Data Type: {data_type}")
            for groundtruth, counts in groundtruth_stats.items():
                print(f"      {groundtruth}: {counts['misclassified']} misclassified out of {counts['total']}")

if __name__ == "__main__":
    BASE_DIR = "explanations/models_comparison"  # Update this with the actual path
    OUTPUT_FILE = "misclassified_contracts_xrag.json"

    misclassified_results = load_classification_results(BASE_DIR)
    save_misclassified_results(misclassified_results, OUTPUT_FILE)
    print_misclassification_stats(misclassified_results)
