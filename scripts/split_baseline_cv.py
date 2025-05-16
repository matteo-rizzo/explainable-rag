import os
import shutil
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def replicate_filtered_dataset(dataset_path, filter_files_path, output_path):
    """
    Replicates the structure of a dataset folder, copying only the files
    whose base names are present anywhere within a specified filter folder
    (including its subdirectories).

    Args:
        dataset_path (str): Path to the original dataset folder (with subfolders).
        filter_files_path (str): Path to the folder containing files to keep.
                                 This folder will be scanned recursively.
                                 Only the base names of files found matter.
        output_path (str): Path to the folder where the filtered dataset
                           structure will be created.
    """
    # --- Validate Input Paths ---
    if not os.path.isdir(dataset_path):
        logging.error(f"Dataset path '{dataset_path}' not found or is not a directory.")
        return
    if not os.path.isdir(filter_files_path):
        logging.error(f"Filter files path '{filter_files_path}' not found or is not a directory.")
        return

    # --- Ensure output path exists ---
    try:
        # exist_ok=True prevents an error if the directory already exists
        os.makedirs(output_path, exist_ok=True)
        logging.info(f"Output directory set to: '{output_path}'")
    except OSError as e:
        logging.error(f"Could not create or access output directory '{output_path}': {e}")
        return

    # --- Get the set of filenames to keep (scan filter_files_path recursively) ---
    logging.info(f"Scanning filter directory '{filter_files_path}' recursively...")
    filter_filenames = set()
    try:
        for root, dirs, files in os.walk(filter_files_path):
            for filename in files:
                # Add only the base name of the file to the set
                filter_filenames.add(filename) # os.path.basename is redundant here

        if not filter_filenames:
             logging.warning(f"No files found in the filter directory '{filter_files_path}' or its subdirectories. The output directory might remain empty or incomplete.")

    except OSError as e:
        logging.error(f"Error scanning filter files directory '{filter_files_path}': {e}")
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred while scanning filter directory '{filter_files_path}': {e}")
        return


    logging.info(f"Found {len(filter_filenames)} unique filenames to keep from '{filter_files_path}' (recursive scan).")
    # Optional: Log the first few filenames for verification if needed
    # if filter_filenames:
    #     logging.debug(f"First few filter filenames: {list(filter_filenames)[:5]}")


    # --- Walk through the dataset directory ---
    copied_count = 0
    skipped_count = 0
    processed_files = 0
    logging.info(f"Processing dataset directory '{dataset_path}'...")

    for root, dirs, files in os.walk(dataset_path):
        relative_path = os.path.relpath(root, dataset_path)
        # Ensure the corresponding directory structure exists in the output path
        destination_dir_for_current_root = os.path.join(output_path, relative_path)
        try:
            # Check if it's not the root relative path '.' before creating
            if relative_path != '.':
                 os.makedirs(destination_dir_for_current_root, exist_ok=True)
        except OSError as e:
             logging.error(f"Could not create directory structure '{destination_dir_for_current_root}': {e}")
             continue # Skip files in this problematic directory path


        for filename in files:
            processed_files += 1
            # Check if the current file's base name is in the filter set
            if filename in filter_filenames:
                source_file_path = os.path.join(root, filename)
                destination_file_path = os.path.join(destination_dir_for_current_root, filename)

                try:
                    # Copy the file, preserving metadata
                    shutil.copy2(source_file_path, destination_file_path)
                    copied_count += 1
                except OSError as e:
                    logging.error(f"Error copying file '{source_file_path}' to '{destination_file_path}': {e}")
                    skipped_count += 1
                except Exception as e:
                     logging.error(f"An unexpected error occurred while copying '{source_file_path}': {e}")
                     skipped_count += 1
            else:
                skipped_count += 1

            # Optional: Log progress periodically
            if processed_files > 0 and processed_files % 1000 == 0:
                logging.info(f"Processed {processed_files} files...")


    logging.info("\n--- Processing Complete ---")
    logging.info(f"Total files processed in source: {processed_files}")
    logging.info(f"Files copied: {copied_count}")
    logging.info(f"Files skipped (not in filter list or error): {skipped_count}")
    logging.info(f"Filtered dataset created at: '{output_path}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Replicate a dataset directory structure, keeping only files whose names are found within the specified filter directory (recursive scan).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example usage:
python filter_dataset.py /path/to/original_dataset /path/to/filter_files /path/to/output_directory

Where:
  /path/to/original_dataset  : Contains the full dataset with subfolders.
  /path/to/filter_files      : Contains files (and subfolders with files) whose names should be kept.
  /path/to/output_directory  : Where the new filtered dataset structure will be saved. This directory will be created if it doesn't exist.
"""
    )

    parser.add_argument("dataset_path", help="Path to the original dataset directory.")
    parser.add_argument("filter_files_path", help="Path to the directory containing the filter files (scanned recursively).")
    parser.add_argument("output_path", help="Path to the directory where the filtered output will be saved.")

    args = parser.parse_args()

    replicate_filtered_dataset(args.dataset_path, args.filter_files_path, args.output_path)