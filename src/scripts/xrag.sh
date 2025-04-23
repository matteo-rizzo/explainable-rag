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
MODES=("ast_cfg" "ast" "cfg")

# OpenAI Model Names (modify these as needed)
MODELS=("gemini-1.5-flash" "gemini-2.0-flash")

# Dataset path template
DATASET_PATH="cv_splits/cv_split_2/{}"

# Loop through each OpenAI model
for MODEL in "${MODELS[@]}"; do
    echo "[INFO] Using OpenAI model: $MODEL"

    # Loop through each mode
    for MODE in "${MODES[@]}"; do
        echo "[INFO] Running contract analysis in mode: $MODE..."

        # Run the Python script with model name argument
        python3 "$PYTHON_SCRIPT" \
            --dataset-path "$DATASET_PATH" \
            --mode "$MODE" \
            --model-name "$MODEL"

        echo "[INFO] Finished processing mode: $MODE with model: $MODEL."
        echo "------------------------------------------------------"
    done
done

echo "[INFO] All modes executed successfully!"
