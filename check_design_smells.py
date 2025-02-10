import os
import json
import requests
from github import Github
from git import Repo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

REPO_URL = "https://github.com/praveenkumar911/SE-reader-web"
REPO_PATH = "./repo"
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def query_llm(prompt):
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": f"</s>[INST]{prompt}[/INST]"})
    try:
        output = response.json()
        generated_text = output[0]['generated_text']
        start_index = generated_text.find('[/INST]') + len('[/INST]')
        return generated_text[start_index:].strip()
    except Exception as e:
        print("Error in LLM response:", str(e))
        return "LLM analysis failed"

def clone_repo():
    if os.path.exists(REPO_PATH):
        os.system(f"rm -rf {REPO_PATH}")
    Repo.clone_from(REPO_URL, REPO_PATH)
    print("Repository cloned successfully.")

def detect_design_smells():
    smells = {}
    for root, _, files in os.walk(REPO_PATH):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    code = f.read()
                prompt = f"Analyze the following code and detect design smells:\n{code}"
                smells[file_path] = query_llm(prompt)
    return smells

def apply_refactoring(smells):
    refactored_code = {}
    for file, issues in smells.items():
        prompt = f"Refactor the following code while preserving functionality:\n{issues}"
        output = query_llm(prompt)
        refactored_code[file] = output if output != "LLM analysis failed" else "Refactoring failed"

        if refactored_code[file] != "Refactoring failed":
            with open(file, "w") as f:
                f.write(refactored_code[file])
    return refactored_code

def create_pull_request(smells, refactored_code):
    g = Github(GITHUB_TOKEN)
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
