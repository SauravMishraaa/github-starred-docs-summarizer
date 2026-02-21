import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

GITHUB_TOKEN = os.getenv('GIT_TOKEN')


headers = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'Authorization': f'Bearer {GITHUB_TOKEN}'
}

logging.basicConfig(level=logging.INFO)
def get_starred_repo_urls():
    page = 1
    repo_urls = []

    while True:
        response = requests.get(
            f'https://api.github.com/user/starred?page={page}&per_page=100',
            headers=headers
        )

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code} - {response.text}")
            break

        repos = response.json()

        if not repos:
            break

        for repo in repos:
            repo_urls.append(repo['html_url'])

        page += 1
        logging.info(f"Fetched page {page - 1}, total repos: {len(repo_urls)}")
    return repo_urls

if __name__ == "__main__":
    starred_repos = get_starred_repo_urls()
    for url in starred_repos:
        print(url)