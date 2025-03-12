import json
from collections import defaultdict


def load_misclassified_data(file_path):
    """ Load misclassified contracts from a JSON file. """
    print(f"Loading misclassified data from {file_path}...")
    with open(file_path, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} models from {file_path}.")
    return data


def compute_union_intersection(baseline_data, comparison_data):
    """ Compute the union and intersection of misclassified contracts, broken down by reentrant, safe, and data type. """
    print("Computing union and intersection of misclassified contracts...")
    results = {}

    for model in baseline_data.keys() | comparison_data.keys():
        print(f"Processing model: {model}")
        results[model] = {
            "union": defaultdict(lambda: {"reentrant": set(), "safe": set()}),
            "intersection": defaultdict(lambda: {"reentrant": set(), "safe": set()}),
            "improvement": defaultdict(lambda: {"reentrant": 0, "safe": 0})
        }

        baseline_reentrant = set(
            contract["contract_id"] for contract in baseline_data.get(model, {}).get("misclassified_contracts", [])
            if contract["groundtruth"] == "reentrant"
        )
        baseline_safe = set(
            contract["contract_id"] for contract in baseline_data.get(model, {}).get("misclassified_contracts", [])
            if contract["groundtruth"] == "safe"
        )

        for data_type in {d["data_type"] for d in comparison_data.get(model, {}).get("misclassified_contracts", [])}:
            print(f"  Processing data type: {data_type}")
            comparison_reentrant = set(
                contract["contract_id"] for contract in
                comparison_data.get(model, {}).get("misclassified_contracts", [])
                if contract["groundtruth"] == "reentrant" and contract["data_type"] == data_type
            )
            comparison_safe = set(
                contract["contract_id"] for contract in
                comparison_data.get(model, {}).get("misclassified_contracts", [])
                if contract["groundtruth"] == "safe" and contract["data_type"] == data_type
            )

            results[model]["union"][data_type]["reentrant"] = list(baseline_reentrant | comparison_reentrant)
            results[model]["union"][data_type]["safe"] = list(baseline_safe | comparison_safe)
            results[model]["intersection"][data_type]["reentrant"] = list(baseline_reentrant & comparison_reentrant)
            results[model]["intersection"][data_type]["safe"] = list(baseline_safe & comparison_safe)

            # Compute improvement
            baseline_reentrant_count = len(baseline_reentrant)
            comparison_reentrant_count = len(comparison_reentrant)
            results[model]["improvement"][data_type][
                "reentrant"] = baseline_reentrant_count - comparison_reentrant_count

            baseline_safe_count = len(baseline_safe)
            comparison_safe_count = len(comparison_safe)
            results[model]["improvement"][data_type]["safe"] = baseline_safe_count - comparison_safe_count

    print("Completed computation of union, intersection, and improvement.")
    return results


def print_stats(results):
    """ Print statistics about the union and intersection of misclassified contracts broken down by data type. """
    print("\nMisclassification Union, Intersection, and Improvement Statistics:")
    for model, stats in results.items():
        print(f"Model: {model}")
        for data_type, data in stats["union"].items():
            print(f"  Data Type: {data_type}")
            print(f"    Union Reentrant: {len(data['reentrant'])}, Union Safe: {len(data['safe'])}")
            print(
                f"    Intersection Reentrant: {len(stats['intersection'][data_type]['reentrant'])}, Intersection Safe: {len(stats['intersection'][data_type]['safe'])}")
            print(
                f"    Improvement Reentrant: {stats['improvement'][data_type]['reentrant']}, Improvement Safe: {stats['improvement'][data_type]['safe']}")


def save_results(results, output_file):
    """ Save the computed union, intersection, and improvement data to a JSON file. """
    print(f"Saving results to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Results successfully saved to {output_file}.")


if __name__ == "__main__":
    BASELINE_FILE = "misclassified_contracts_baseline.json"
    COMPARISON_FILE = "misclassified_contracts_xrag.json"
    OUTPUT_FILE = "misclassified_contracts_union_intersection.json"

    print("Starting misclassification analysis...")
    baseline_data = load_misclassified_data(BASELINE_FILE)
    comparison_data = load_misclassified_data(COMPARISON_FILE)

    union_intersection_results = compute_union_intersection(baseline_data, comparison_data)
    save_results(union_intersection_results, OUTPUT_FILE)
    print_stats(union_intersection_results)
    print("Analysis complete.")
