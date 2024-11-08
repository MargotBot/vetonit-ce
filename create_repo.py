import os
import requests
import json

def create_github_repo():
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not github_token:
        print("Error: GitHub token not found in environment variables")
        return None, None

    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # First, check if the repository exists
    try:
        response = requests.get('https://api.github.com/user/repos', headers=headers)
        existing_repos = response.json()
        for repo in existing_repos:
            if repo['name'] == 'vetonit-ce':
                print("Repository already exists, using existing repository")
                return repo['clone_url'], repo['html_url']
    except Exception as e:
        print(f"Error checking existing repositories: {str(e)}")
        return None, None
    
    # If repository doesn't exist, create it
    data = {
        'name': 'vetonit-ce',
        'description': 'VetOnIt CE landing page for Master Controlled Substance Regulations course',
        'private': False,
        'has_issues': True,
        'has_projects': True,
        'has_wiki': True,
        'auto_init': False  # Changed to False to avoid conflicts with our initial push
    }
    
    try:
        response = requests.post('https://api.github.com/user/repos', 
                               headers=headers,
                               data=json.dumps(data))
        
        if response.status_code == 201:
            print("Repository created successfully!")
            repo_data = response.json()
            return repo_data['clone_url'], repo_data['html_url']
        else:
            print(f"Error creating repository: {response.status_code}")
            print(f"Response: {response.json().get('message', 'Unknown error')}")
            return None, None
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None, None

def setup_git_and_push():
    clone_url, html_url = create_github_repo()
    if not clone_url:
        return False
        
    try:
        # Configure git
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        os.system('git config --global user.name "GitHub Actions Bot"')
        
        # Initialize git repository if not already initialized
        os.system('git init')
        
        # Add all files
        os.system('git add .')
        os.system('git commit -m "Initial commit: Add landing page content"')
        
        # Set up remote
        os.system('git remote remove origin 2>/dev/null')  # Remove if exists
        
        # Set up Git credentials using token
        git_url = clone_url.replace('https://', f'https://oauth2:{os.environ["GITHUB_TOKEN"]}@')
        os.system(f'git remote add origin {git_url}')
        
        # Push to GitHub
        os.system('git branch -M main')
        os.system('git push -u origin main --force')  # Using force push to handle existing repository
        
        print("Successfully pushed code to GitHub!")
        
        # Enable GitHub Pages
        headers = {
            'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        pages_data = {
            'source': {
                'branch': 'main',
                'path': '/'
            }
        }
        
        repo_name = clone_url.split('/')[-1].replace('.git', '')
        username = clone_url.split('/')[-2]
        
        pages_response = requests.post(
            f'https://api.github.com/repos/{username}/{repo_name}/pages',
            headers=headers,
            data=json.dumps(pages_data)
        )
        
        if pages_response.status_code in [201, 204]:
            print("GitHub Pages enabled successfully!")
        else:
            print(f"Warning: Could not enable GitHub Pages: {pages_response.status_code}")
            print(pages_response.json().get('message', 'Unknown error'))
        
        return True
    except Exception as e:
        print(f"Error during git operations: {str(e)}")
        return False

if __name__ == "__main__":
    setup_git_and_push()
