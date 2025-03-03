import json
import os
from concurrent.futures import ThreadPoolExecutor


def clean_json_content(lines):
    """
    Clean the JSON content by removing lines outside the JSON dictionary.

    Parameters:
    lines (list): List of lines read from the file.

    Returns:
    str: Cleaned JSON content as a string.
    """
    json_content = ''.join(lines)
    try:
        # Attempt to parse the full content directly
        json.loads(json_content)
        return json_content
    except json.JSONDecodeError:
        pass

    # Attempt to extract JSON dictionary from lines
    json_start = -1
    json_end = -1

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('{') and json_start == -1:
            json_start = i
        if line.endswith('}') and json_start != -1:
            json_end = i + 1

    if json_start != -1 and json_end != -1:
        json_content = ''.join(lines[json_start:json_end])
        return json_content
    else:
        return None


def preprocess_file(input_file_path, output_file_path):
    """
    Processes a single JSON file, extracts the JSON dictionary content, and saves it to the output path.

    Parameters:
    input_file_path (str): The path to the input JSON file.
    output_file_path (str): The path to the output JSON file.
    """
    try:
        # Read the content of the input file
        with open(input_file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {input_file_path}: {e}")
        return

    # Clean the JSON content
    json_content = clean_json_content(lines)
    if json_content is None:
        print(f"Skipping invalid JSON file: {input_file_path}")
        return

    try:
        # Parse the cleaned JSON content
        json_data = json.loads(json_content)
    except json.JSONDecodeError:
        print(f"Skipping invalid JSON file: {input_file_path}")
        return

    # Check if the parsed JSON data is a dictionary
    if isinstance(json_data, dict):
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        try:
            # Write the JSON dictionary to the output file
            with open(output_file_path, 'w') as f:
                json.dump(json_data, f, indent=4)
            print(f"Processed and saved: {output_file_path}")
        except Exception as e:
            print(f"Error writing file {output_file_path}: {e}")
    else:
        print(f"Skipping non-dict JSON file: {input_file_path}")


def preprocess_files(input_dir, output_dir):
    """
    Processes all JSON files in the input directory, extracting only the JSON dictionary content and saving it to the output directory.

    Parameters:
    input_dir (str): The path to the directory containing the input JSON files.
    output_dir (str): The path to the directory to save the preprocessed JSON files.
    """
    files_to_process = []

    # Traverse the input directory to find all JSON files
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json'):
                input_file_path = os.path.join(root, file)
                output_file_path = os.path.join(output_dir, os.path.relpath(input_file_path, input_dir))
                files_to_process.append((input_file_path, output_file_path))

    # Process files in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        executor.map(lambda p: preprocess_file(*p), files_to_process)


if __name__ == "__main__":
    # Define the input and output directories
    input_directory = "dataset/manually-verified-train/ast-raw"  # Path to the directory containing the saved JSON files
    output_directory = "dataset/manually-verified-train/ast-preprocessed"  # Path to the directory to save the preprocessed JSON files

    # Check if the input directory exists
    if not os.path.exists(input_directory):
        print(f"Input directory does not exist: {input_directory}")
    else:
        # Preprocess the JSON files
        preprocess_files(input_directory, output_directory)
