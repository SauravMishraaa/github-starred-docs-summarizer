import os
import shutil
import logging
from pathlib import Path
import subprocess
from fetch import get_starred_repo_urls
import stat
logging.basicConfig(level=logging.INFO)

DOCS_DIR = Path('./github_docs')
CLONE_DIR = Path('./tmp_repos')

def handle_remove_readonly(func, path, exc):
    """Error handler for Windows readonly files"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(repo_url, clone_path):
    """Clone a repository"""
    try:
        subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, str(clone_path)],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clone {repo_url}: {e}")
        return False
    
def find_docs(repo_path):
    docs_files = []
    repo_path = Path(repo_path)

    skip_dirs = {'.git', 'node_modules','.txt', 'venv', '__pycache__', '.github', 'tests', 'test', '.venv', 'dist', 'build'}

    doc_extensions = {'.md', '.rst', '.pdf', '.docx'}

    for file_path in repo_path.rglob('*'):
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            continue

        if file_path.is_file() and file_path.suffix.lower() in doc_extensions:
            docs_files.append(file_path)
    return docs_files

def copy_docs(docs_files, repo_name, destination, repo_path):
    dest_dir = Path(destination) / repo_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    repo_path = Path(repo_path)

    for file_path in docs_files:
        try:
            rel_path = file_path.relative_to(repo_path)
            dest_file = dest_dir / rel_path

            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_file)
            logging.info(f"Copied: {file_path.name}")
        except Exception as e:
            logging.error(f"Failed to copy {file_path.name}: {e}")

def process_repo(repo_url):
    """Clone repo, extract docs, and copy them."""
    parts = repo_url.rstrip('/').split('/')
    owner = parts[-2]
    repo_name = parts[-1]
    full_repo_name = f"{owner}_{repo_name}"

    logging.info(f"Processing repository: {owner}/{repo_name}")

    dest_dir = DOCS_DIR / full_repo_name
    if dest_dir.exists() and any(dest_dir.iterdir()):
        logging.info(f"Documentation already exists for {owner}/{repo_name}, skipping.")
        return True

    clone_path = CLONE_DIR / full_repo_name
    if clone_path.exists():
        shutil.rmtree(clone_path, onerror=handle_remove_readonly)

    if not clone_repo(repo_url, clone_path):
        return False
    
    docs_files = find_docs(clone_path)

    if not docs_files:
        logging.warning(f"No documentation found for {repo_name}")
    else:
        logging.info(f"Found {len(docs_files)} documentation files")

        copy_docs(docs_files, full_repo_name, DOCS_DIR, clone_path)
    try:
        shutil.rmtree(clone_path, onerror=handle_remove_readonly)
        logging.info(f"Cleaned up temporary files for {repo_name}")
    except Exception as e:
        logging.error(f"Failed to cleanup {clone_path}: {e}")
    
    return True

def fetch_all_starred_docs():
    """Fetch documentation from all starred repositories."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    CLONE_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Fetching starred repositories...")
    starred_repos = get_starred_repo_urls()
    logging.info(f"Found {len(starred_repos)} starred repositories.\n")


    success_count = 0
    for i, repo_url in enumerate(starred_repos, 1):
        logging.info(f"[{i}/{len(starred_repos)}] {repo_url}")
        if process_repo(repo_url):
            success_count += 1

    if CLONE_DIR.exists():
        shutil.rmtree(CLONE_DIR, onerror=handle_remove_readonly)

    logging.info(f"\n Complete! Processed {success_count}/{len(starred_repos)} repositories.")
    logging.info(f"Documentation saved to: {DOCS_DIR.absolute()}")

if __name__ == "__main__":
    fetch_all_starred_docs()