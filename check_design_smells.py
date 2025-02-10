import os
import json
import requests
from github import Github
from git import Repo

github_token = os.getenv("GITHUB_TOKEN", "${{ secrets.CLASS_TOKEN }}")
repo_url = "https://github.com/praveenkumar911/SE-reader-web.git"
repo_path = "./repo"
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
headers = {"Authorization": f"Bearer ${{ secrets.HUGGING_TOKEN }}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def clone_repo():
    if os.path.exists(repo_path):
        os.system(f"rm -rf {repo_path}")
    Repo.clone_from(repo_url, repo_path)

def detect_design_smells():
    smells = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):  # Target Python files
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    code = f.read()
                smells[file_path] = analyze_code_with_llm(code)
    return smells

def analyze_code_with_llm(code):
    output = query({"inputs": f"</s>[INST]Detect code smells and suggest refactoring:\n{code}[/INST]"})
    generated_text = output[0]['generated_text']
    start_index = generated_text.find('[/INST]') + len('[/INST]')
    return generated_text[start_index:].strip()

def apply_refactoring(smells):
    refactored_code = {}
    for file, issues in smells.items():
        output = query({"inputs": f"</s>[INST]Refactor the following code while preserving functionality:\n{issues}[/INST]"})
        generated_text = output[0]['generated_text']
        start_index = generated_text.find('[/INST]') + len('[/INST]')
        refactored_code[file] = generated_text[start_index:].strip()
        with open(file, "w") as f:
            f.write(refactored_code[file])
    return refactored_code

def create_pull_request(smells, refactored_code):
    g = Github(github_token)
    repo = g.get_repo("your-username/your-repo")
    branch_name = "refactor-design-smells"
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=repo.get_branch("main").commit.sha)
    
    for file, new_code in refactored_code.items():
        with open(file, "r") as f:
            content = f.read()
        repo.get_contents(file).update(content, f"Refactored {file}", branch=branch_name)
    
    pr_description = """
    ## Automated Design Smell Refactoring
    ### Detected Issues:
    {}
    ### Applied Refactorings:
    {}
    """.format(json.dumps(smells, indent=2), json.dumps(refactored_code, indent=2))
    
    repo.create_pull(title="Automated Refactoring", body=pr_description, head=branch_name, base="main")

def main():
    clone_repo()
    smells = detect_design_smells()
    refactored_code = apply_refactoring(smells)
    create_pull_request(smells, refactored_code)

if __name__ == "__main__":
    main()
