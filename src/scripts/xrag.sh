#!/bin/bash

# Define paths
VENV_PATH=".venv"
PYTHON_SCRIPT="src/scripts/xrag.py"

# Ensure the virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "[ERROR] Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Ensure the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "[ERROR] Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Add the 'src' directory to PYTHONPATH
export PYTHONPATH=$(pwd)/src:$PYTHONPATH

# Modes to run
MODES=("aggregated" "ast" "cfg")

# Dataset path (modify if needed)
DATASET_PATH="dataset/manually-verified-{}"

# Loop through modes and execute the Python script
for MODE in "${MODES[@]}"; do
    echo "[INFO] Running contract analysis in mode: $MODE..."

    python3 "$PYTHON_SCRIPT" \
        --dataset-path "$DATASET_PATH" \
        --mode "$MODE" \
        --use-multiprocessing

    echo "[INFO] Finished processing mode: $MODE."
    echo "-------------------------------------------"
done

echo "[INFO] All modes executed successfully!"
