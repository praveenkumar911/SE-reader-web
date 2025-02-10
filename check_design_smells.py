import os
import requests

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer ${{ secrets.HUGGING_TOKEN }}"}  # Use GitHub Actions variable directly

def query(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()

def check_and_fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    prompt = f"Analyze the following code for design smells and suggest improvements:\n{content}"
    response = query({"inputs": f"</s>[INST] {prompt} [/INST]"})
    
    if response and isinstance(response, list) and 'generated_text' in response[0]:
        generated_text = response[0]['generated_text']
        start_index = generated_text.find('[/INST]') + len('[/INST]')
        fixed_code = generated_text[start_index:].strip()
        
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(fixed_code)
        print(f"Updated: {file_path}")
    else:
        print(f"Failed to analyze {file_path}")

def main():
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                check_and_fix_file(file_path)

if __name__ == "__main__":
    main()
