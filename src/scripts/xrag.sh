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
#OPENAI_MODELS=("gpt-3.5-turbo-0125" "gpt-4o-mini-2024-07-18" "gpt-4o-2024-08-06" "o3-mini-2025-01-31")
OPENAI_MODELS=("o3-mini-2025-01-31")

# Dataset path template
DATASET_PATH="dataset/manually-verified-{}"

# Loop through each OpenAI model
for MODEL in "${OPENAI_MODELS[@]}"; do
    echo "[INFO] Using OpenAI model: $MODEL"

    # Loop through each mode
    for MODE in "${MODES[@]}"; do
        echo "[INFO] Running contract analysis in mode: $MODE..."

        # Run the Python script with model name argument
        python3 "$PYTHON_SCRIPT" \
            --dataset-path "$DATASET_PATH" \
            --mode "$MODE" \
            --model-name "$MODEL" \
            --use-multiprocessing

        echo "[INFO] Finished processing mode: $MODE with model: $MODEL."
        echo "------------------------------------------------------"
    done
done

echo "[INFO] All modes executed successfully!"
