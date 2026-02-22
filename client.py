from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
from docs import DOCS_DIR, CLONE_DIR, clone_repo, find_docs, copy_docs, handle_remove_readonly
from pathlib import Path
import shutil
import time
from fetch import get_starred_repo_urls

logging.basicConfig(level=logging.INFO)
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def read_docs_content(docs_files, max_chars=200000):  # Increased further
    """
    Read documentation files and combine their content.
    Limits total content to avoid token limits.
    """
    combined_content = ""
    for file_path in docs_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                combined_content += f"\n\n{'='*80}\n FILE: {file_path.name}\n{'='*80}\n\n{content}"
                
                if len(combined_content) > max_chars:
                    logging.warning(f"Content limit reached, stopping at {len(combined_content)} chars")
                    break
        except Exception as e:
            logging.error(f"Failed to read {file_path.name}: {e}")
    
    return combined_content

def summarize_docs(docs_content, repo_name, max_retries=5):
    """
    Use OpenAI to summarize documentation content with retry logic.
    """
    if not docs_content.strip():
        logging.warning(f"No content to summarize for {repo_name}")
        return None
    
    for attempt in range(max_retries):
        try:
            message = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=4096,  # Increased from 2048 to 4096
                temperature=0.3,  # Lower temperature for more focused, detailed output
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical documentation expert who creates comprehensive, detailed summaries. Your summaries should be thorough, well-structured, and include all important technical details, code examples, and specific implementation guidance."
                    },
                    {
                        "role": "user",
                        "content": f"""Create an exhaustive and highly detailed summary of the documentation for the repository '{repo_name}'.

**Instructions:**
- Be extremely thorough and comprehensive
- Include specific technical details, not just high-level overviews
- Quote important configuration values, command examples, and code snippets
- Explain how different components work together
- Include version requirements and compatibility notes
- Mention important caveats, gotchas, and best practices
- If there are multiple ways to do something, explain all of them
- Use markdown formatting with headers, lists, code blocks, and emphasis

**Required Sections (provide extensive detail for each):**

### 1. Project Overview & Purpose
- What is this project and what problem does it solve?
- Target audience and use cases
- Project history, maturity, and current status
- Key differentiators from similar projects

### 2. Key Features & Capabilities
- List ALL major features with detailed explanations
- For each feature, explain:
  * What it does
  * Why it's useful
  * When to use it
  * Any limitations or trade-offs

### 3. Architecture & Technical Design
- Overall system architecture with component descriptions
- Design patterns and principles used
- Data flow and component interactions
- Technology stack and why each piece was chosen
- Scalability and performance considerations

### 4. Installation & Setup
- Detailed step-by-step installation for different platforms
- All prerequisites with specific version requirements
- Configuration file locations and structures
- Initial setup and bootstrapping process
- Verification steps to confirm successful installation
- Common installation issues and troubleshooting

### 5. Core Components & Modules
- Detailed description of each major component
- Purpose and responsibilities of each module
- How components interact and depend on each other
- Extension points and customization options
- Internal APIs and interfaces

### 6. Usage Guide & Examples
- Basic usage with simple examples
- Advanced usage patterns with detailed examples
- Common workflows and how to accomplish them
- Best practices and recommended approaches
- Real-world use case examples
- Code snippets demonstrating key features

### 7. API / CLI Reference
- Complete list of available APIs, endpoints, or commands
- For each API/command:
  * Purpose and description
  * Parameters and their meanings
  * Return values and response formats
  * Usage examples
  * Error codes and handling

### 8. Configuration & Customization
- All configuration options with descriptions
- Default values and recommended settings
- Environment variables and their effects
- Configuration file formats and examples
- Advanced configuration scenarios
- Performance tuning options

### 9. Dependencies & Requirements
- Complete list of dependencies with versions
- System requirements (OS, hardware, etc.)
- Optional dependencies and what they enable
- Dependency installation and management
- Compatibility matrix

### 10. Development & Contributing
- How to set up development environment
- Build process and tooling
- Testing approach and running tests
- Code structure and organization
- Contributing guidelines
- Release process

### 11. Deployment & Production
- Production deployment strategies
- Scaling considerations
- Monitoring and observability
- Backup and disaster recovery
- Security best practices
- Performance optimization

### 12. Troubleshooting & Common Issues
- Known issues and limitations
- Common error messages and solutions
- Debugging techniques and tools
- Where to get help
- FAQ items

### 13. Additional Resources
- Links to tutorials and guides
- Community resources
- Related projects and integrations
- Changelog highlights

**Documentation Content:**
{docs_content}

**Remember:** Be as detailed and comprehensive as possible. Include concrete examples, specific values, and actionable information throughout."""
                    }
                ]
            )
            
            summary = message.choices[0].message.content
            logging.info(f"Generated detailed summary for {repo_name} ({len(summary)} chars)")
            return summary

        except Exception as e:
            error_str = str(e)
            if '429' in error_str:
                wait_time = (2 ** attempt) * 10
                logging.warning(f"Rate limit hit for {repo_name}. Attempt {attempt + 1}/{max_retries}. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"Failed to generate summary for {repo_name}: {e}")
                return None

    logging.error(f"Max retries reached for {repo_name}")
    return None

def save_summary(summary, repo_name, destination):
    """
    Save the summary to a file.
    """
    dest_dir = Path(destination) / repo_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    summary_file = dest_dir / "SUMMARY.md"
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Detailed Summary: {repo_name}\n\n")
            f.write(f"*Auto-generated comprehensive documentation summary*\n\n")
            f.write("---\n\n")
            f.write(summary)
        logging.info(f"Saved detailed summary to {summary_file} ({len(summary)} chars)")
        return True
    except Exception as e:
        logging.error(f"Failed to save summary for {repo_name}: {e}")
        return False

def process_repo_with_summary(repo_url):
    parts = repo_url.rstrip('/').split('/')
    owner = parts[-2]
    repo_name = parts[-1]
    full_repo_name = f"{owner}_{repo_name}"

    logging.info(f"Processing repository: {owner}/{repo_name}")

    dest_dir = DOCS_DIR / full_repo_name
    summary_file = dest_dir / "SUMMARY.md"

    # If summary already exists, skip entirely
    if summary_file.exists():
        logging.info(f"Summary already exists for {owner}/{repo_name}, skipping.")
        return True

    # If docs exist, just generate summary from existing docs
    if dest_dir.exists() and any(dest_dir.iterdir()):
        logging.info(f"Docs exist for {owner}/{repo_name}, generating summary only...")
        docs_files = list(dest_dir.rglob('*'))
        docs_files = [f for f in docs_files if f.is_file() and f.name != 'SUMMARY.md']
        docs_content = read_docs_content(docs_files)
        summary = summarize_docs(docs_content, full_repo_name)
        if summary:
            save_summary(summary, full_repo_name, DOCS_DIR)
        return True

    # Otherwise clone, copy docs, and generate summary
    clone_path = CLONE_DIR / full_repo_name
    if clone_path.exists():
        shutil.rmtree(clone_path, onerror=handle_remove_readonly)

    if not clone_repo(repo_url, clone_path):
        return False
    
    docs_files = find_docs(clone_path)

    if not docs_files:
        logging.warning(f"No documentation found for {repo_name}")
        return True
        
    logging.info(f"Found {len(docs_files)} documentation files")
    copy_docs(docs_files, full_repo_name, DOCS_DIR, clone_path)
        
    docs_content = read_docs_content(docs_files)
    summary = summarize_docs(docs_content, full_repo_name)
    if summary:
        save_summary(summary, full_repo_name, DOCS_DIR)
    
    try:
        shutil.rmtree(clone_path, onerror=handle_remove_readonly)
        logging.info(f"Cleaned up temporary files for {repo_name}")
    except Exception as e:
        logging.error(f"Failed to cleanup {clone_path}: {e}")
    
    return True

def fetch_all_starred_docs_with_summary():
    """Fetch documentation and generate summaries for all starred repositories."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    CLONE_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Fetching starred repositories...")
    starred_repos = get_starred_repo_urls()
    logging.info(f"Found {len(starred_repos)} starred repositories.\n")

    success_count = 0
    for i, repo_url in enumerate(starred_repos, 1):
        logging.info(f"[{i}/{len(starred_repos)}] {repo_url}")
        if process_repo_with_summary(repo_url):
            success_count += 1
        
        if i < len(starred_repos):
            parts = repo_url.rstrip('/').split('/')
            full_repo_name = f"{parts[-2]}_{parts[-1]}"
            summary_file = DOCS_DIR / full_repo_name / "SUMMARY.md"
            
            if not summary_file.exists():
                wait_time = 60
                logging.info(f"Waiting {wait_time}s before next repo to avoid rate limits...")
                time.sleep(wait_time)

    if CLONE_DIR.exists():
        shutil.rmtree(CLONE_DIR, onerror=handle_remove_readonly)

    logging.info(f"\nComplete! Processed {success_count}/{len(starred_repos)} repositories.")
    logging.info(f"Documentation saved to: {DOCS_DIR.absolute()}")

if __name__ == "__main__":
    fetch_all_starred_docs_with_summary()