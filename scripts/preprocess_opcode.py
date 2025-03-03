import os


def clean_opcode_file(input_path, output_path):
    with open(input_path, 'r') as file:
        lines = file.readlines()

    opcodes = []
    is_opcode_section = False

    for line in lines:
        line = line.strip()

        # Start capturing opcodes after "Opcodes:" line
        if line.startswith("Opcodes:"):
            is_opcode_section = True
            continue

        # Stop capturing when a separator line is encountered
        if line.startswith("======="):
            is_opcode_section = False
            continue

        # If we're in the opcode section, process the line
        if is_opcode_section:
            # Remove any blank lines or lines with noise
            if line and not line.startswith("======="):
                opcodes.append(line)

    # Combine all opcode lines into a single string
    cleaned_opcodes = ' '.join(opcodes)

    # Write the cleaned opcodes to the output file
    with open(output_path, 'w') as output_file:
        output_file.write(cleaned_opcodes)


def process_directory(input_directory, output_directory):
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)

            # Clean the opcode file
            clean_opcode_file(input_path, output_path)
            print(f"Processed and cleaned {filename}")


if __name__ == "__main__":
    # Specify the input and output directories
    input_directory = 'dataset/cgt/opcode'
    output_directory = 'dataset/cgt/opcode_preprocessed'

    # Process the directory
    process_directory(input_directory, output_directory)
