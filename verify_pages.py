import os
import requests

def verify_github_pages():
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not github_token:
        print("Error: GitHub token not found")
        return False
        
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Get user's username
        user_response = requests.get('https://api.github.com/user', headers=headers)
        if user_response.status_code != 200:
            print("Error getting user information")
            return False
            
        username = user_response.json()['login']
        
        # Check Pages status
        pages_response = requests.get(
            f'https://api.github.com/repos/{username}/vetonit-ce/pages',
            headers=headers
        )
        
        if pages_response.status_code == 200:
            pages_data = pages_response.json()
            print("\nGitHub Pages Status:")
            print(f"URL: {pages_data.get('html_url', 'Not available')}")
            print(f"Status: {pages_data.get('status', 'Unknown')}")
            print(f"Custom Domain: {pages_data.get('custom_domain', 'None')}")
            print(f"HTTPS: {pages_data.get('https_enforced', False)}")
            return True
        else:
            print(f"Error getting Pages status: {pages_response.status_code}")
            print(pages_response.json().get('message', 'Unknown error'))
            return False
            
    except Exception as e:
        print(f"Error verifying GitHub Pages: {str(e)}")
        return False

if __name__ == "__main__":
    verify_github_pages()
