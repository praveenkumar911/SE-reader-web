import os

def detect_and_fix_magic_numbers(file_path):
    """
    Detects and replaces magic numbers (hardcoded numeric values) with named constants.
    """
    with open(file_path, 'r') as file:
        content = file.readlines()

    modified = False
    new_content = []
    for line in content:
        # Example: Replace hardcoded number 42 with a named constant
        if '42' in line and not line.strip().startswith('#'):  # Ignore comments
            print(f"Detected magic number '42' in {file_path}. Fixing...")
            line = line.replace('42', 'MAGIC_NUMBER')
            modified = True
        new_content.append(line)

    if modified:
        with open(file_path, 'w') as file:
            file.writelines(new_content)


def detect_and_fix_long_functions(file_path):
    """
    Detects long functions (e.g., > 20 lines) and suggests refactoring.
    """
    with open(file_path, 'r') as file:
        content = file.readlines()

    function_start = None
    function_name = None
    inside_function = False
    function_lines = []

    for i, line in enumerate(content):
        stripped_line = line.strip()

        # Detect the start of a function definition
        if stripped_line.startswith("def ") and ":" in stripped_line:
            function_start = i
            function_name = stripped_line.split("def ")[1].split("(")[0]
            inside_function = True
            function_lines = [line]
        elif inside_function:
            function_lines.append(line)
            # Detect the end of a function (dedent or EOF)
            if stripped_line == "" or i == len(content) - 1:
                if len(function_lines) > 20:  # Threshold for "long function"
                    print(f"Detected long function '{function_name}' in {file_path}.")
                    print("Suggestion: Refactor this function into smaller sub-functions.")
                inside_function = False


def detect_and_fix_duplicate_code(file_path):
    """
    Detects duplicate code blocks and suggests deduplication.
    """
    with open(file_path, 'r') as file:
        content = file.readlines()

    # Simple heuristic: Look for repeated blocks of 3+ consecutive lines
    seen_blocks = {}
    for i in range(len(content) - 2):
        block = tuple(content[i:i + 3])  # Consider 3-line blocks
        if block in seen_blocks:
            print(f"Duplicate code block detected in {file_path} at lines {seen_blocks[block]} and {i + 1}.")
            print("Suggestion: Extract this block into a reusable function.")
        else:
            seen_blocks[block] = i + 1


def process_file(file_path):
    """
    Processes a single file to detect and fix design smells.
    """
    print(f"Processing file: {file_path}")
    detect_and_fix_magic_numbers(file_path)
    detect_and_fix_long_functions(file_path)
    detect_and_fix_duplicate_code(file_path)


def main():
    """
    Main function to iterate over all files in the repository and process them.
    """
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):  # Only process Python files
                file_path = os.path.join(root, file)
                process_file(file_path)


if __name__ == "__main__":
    main()
