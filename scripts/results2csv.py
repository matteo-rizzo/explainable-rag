import csv
import json
import os

# Define input/output files
PROCESSED_RESULTS_FOLDER = "results"
CSV_OUTPUT_FILE = "google_form_evaluation.csv"
MODELS = ["o3-mini"]


def gather_evaluation_data():
    """Collect relevant data for evaluation from results."""
    evaluation_rows = []

    for model in os.listdir(PROCESSED_RESULTS_FOLDER):
        if model not in MODELS:
            continue

        model_path = os.path.join(PROCESSED_RESULTS_FOLDER, model)

        if not os.path.isdir(model_path):
            continue  # Skip non-directory files

        for data_type in os.listdir(model_path):
            data_type_path = os.path.join(model_path, data_type)

            for groundtruth_label in os.listdir(data_type_path):
                groundtruth_path = os.path.join(data_type_path, groundtruth_label)

                for contract_file in os.listdir(groundtruth_path):
                    if not contract_file.endswith(".json"):
                        continue

                    contract_path = os.path.join(groundtruth_path, contract_file)
                    with open(contract_path, "r") as f:
                        contract_data = json.load(f)

                    # Prepare evaluation row
                    row = [
                        contract_data["contract_id"],
                        model,
                        data_type,
                        groundtruth_label,
                        contract_data["source_code"],
                        contract_data["baseline_explanation"],
                        contract_data["comparison_explanation"],
                        "Q1: Correctness: Does the BASELINE explanation match expert reasoning?",
                        "Q2: Correctness: Does the XRAG explanation match expert reasoning?"
                        "Q3: Informativeness: Which explanation is more informative?",
                        "Q4: Clarity: Does the explanation help understand the misclassification?",
                        "Q5: Additional comments (optional)"
                    ]
                    evaluation_rows.append(row)

    return evaluation_rows


def save_to_csv(rows, output_file):
    """Save evaluation data to CSV file."""
    print(f"Saving evaluation data to {output_file}...")

    headers = [
        "Contract ID",
        "Model",
        "Data Type",
        "Groundtruth Label",
        "Source Code",
        "Baseline Explanation",
        "XRAG Explanation",
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "Q5"
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Evaluation CSV saved to {output_file}")


if __name__ == "__main__":
    evaluation_data = gather_evaluation_data()
    save_to_csv(evaluation_data, CSV_OUTPUT_FILE)
    print("Google Form evaluation file is ready!")
