import os
import json
import requests
from github import Github
from git import Repo

# GitHub & Hugging Face credentials
github_token = "${{ secrets.CLASS_TOKEN }}"
hf_api_key = "${{ secrets.HUGGING_TOKEN }}"

repo_url = "https://github.com/praveenkumar911/SE-reader-web"
repo_path = "./repo"
API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"
headers = {"Authorization": f"Bearer {hf_api_key}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    try:
        output = response.json()
        if isinstance(output, dict) and "generated_text" in output:
            return output["generated_text"]
        else:
            print("Unexpected response format:", json.dumps(output, indent=2))
            return "Error: Unexpected response format"
    except Exception as e:
        print("Error parsing response:", str(e))
        return "Error: Failed to parse API response"

def clone_repo():
    if os.path.exists(repo_path):
        os.system(f"rm -rf {repo_path}")
    Repo.clone_from(repo_url, repo_path)
    print("Repository cloned successfully.")

def detect_design_smells():
    smells = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    code = f.read()
                smells[file_path] = analyze_code_with_llm(code)
    return smells

def analyze_code_with_llm(code):
    prompt = f"Detect code smells and suggest refactoring:\n{code}"
    generated_text = query({"inputs": prompt})
    return generated_text if not generated_text.startswith("Error:") else "LLM analysis failed"

def apply_refactoring(smells):
    refactored_code = {}
    for file, issues in smells.items():
        prompt = f"Refactor the following code while preserving functionality:\n{issues}"
        output = query({"inputs": prompt})
        refactored_code[file] = output if not output.startswith("Error:") else "Refactoring failed"
        with open(file, "w") as f:
            f.write(refactored_code[file])
    return refactored_code

def create_pull_request(smells, refactored_code):
    g = Github(github_token)
    repo = g.get_repo("praveenkumar911/SE-reader-web")
    branch_name = "refactor-design-smells"
    
    try:
        repo.get_branch(branch_name)
        print(f"Branch {branch_name} already exists.")
    except:
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=repo.get_branch("main").commit.sha)
        print(f"Created new branch: {branch_name}")

    for file, new_code in refactored_code.items():
        if new_code != "Refactoring failed":
            with open(file, "r") as f:
                content = f.read()
            repo.get_contents(file, ref=branch_name).update(new_code, f"Refactored {file}", branch=branch_name)

    pr_description = f"""
    ## Automated Design Smell Refactoring
    ### Detected Issues:
    {json.dumps(smells, indent=2)}
    ### Applied Refactorings:
    {json.dumps(refactored_code, indent=2)}
    """
    
    repo.create_pull(title="Automated Refactoring", body=pr_description, head=branch_name, base="main")
    print("Pull request created successfully.")

def main():
    clone_repo()
    smells = detect_design_smells()
    refactored_code = apply_refactoring(smells)
    create_pull_request(smells, refactored_code)

if __name__ == "__main__":
    main()
