# refactor.py

import requests
import os
import sys

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()

def refactor_code(file_path):
    # Read the content of the file
    with open(file_path, 'r') as file:
        code = file.read()
    
    # Query the LLM for refactoring suggestions
    output = query({
        "inputs": f"</s>[INST] Refactor the following code: {code} [/INST]",
    })
    
    # Extract the refactored code from the response
    generated_text = output[0]['generated_text']
    start_index = generated_text.find('[/INST]') + len('[/INST]')
    refactored_code = generated_text[start_index:].strip()
    
    # Write the refactored code back to the file
    with open(file_path, 'w') as file:
        file.write(refactored_code)

def refactor_all_files(repo_path, file_extensions=None):
    if file_extensions is None:
        file_extensions = ['.py']  # Default to Python files
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                print(f"Refactoring file: {file_path}")
                refactor_code(file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python refactor.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    refactor_all_files(repo_path)
