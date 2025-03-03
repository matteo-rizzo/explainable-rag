import json


def extract_and_parse_json(text, verbose=False):
    """
    Extracts and parses the first valid JSON object from a string that may contain extra content.

    Args:
        text (str): The input string that contains a JSON object.
        verbose (bool): If True, prints detailed debug information.

    Returns:
        dict: The parsed JSON object.

    Raises:
        ValueError: If no JSON object is found in the input text.
        json.JSONDecodeError: If the extracted JSON string cannot be parsed.
    """
    try:
        if verbose:
            print("Starting JSON extraction...")

        # Find the first occurrence of an opening brace.
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON found in the input text.")

        if verbose:
            print(f"Found first '{{' at index {start}")

        brace_count = 0
        json_str = ""

        # Iterate over the characters starting from the first '{'
        for i in range(start, len(text)):
            char = text[i]
            json_str += char

            if verbose:
                print(f"Index {i}: '{char}' | Current extracted string: {json_str}")

            if char == "{":
                brace_count += 1
                if verbose:
                    print(f"Incremented brace count to {brace_count}")
            elif char == "}":
                brace_count -= 1
                if verbose:
                    print(f"Decremented brace count to {brace_count}")

            # When the braces are balanced, stop the loop.
            if brace_count == 0:
                if verbose:
                    print("Balanced JSON object found.")
                break

        if verbose:
            print(f"Final JSON string extracted: {json_str}")

        # Parse the extracted JSON string.
        parsed_json = json.loads(json_str)

        if verbose:
            print("Successfully parsed JSON object.")
            print(f"Extracted JSON: {parsed_json}")

        return parsed_json

    except json.JSONDecodeError as e:
        if verbose:
            print(f"Error parsing JSON: {e}")
        raise
    except Exception as e:
        if verbose:
            print(f"An error occurred: {e}")
        raise
