import requests

def list_files_in_github_directory():
    repo_owner = 'csfeeser'
    repo_name = 'pollgen'
    directory_path = 'questions'

    # API endpoint for listing directory contents
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{directory_path}"

    # Make GET request to the GitHub API
    response = requests.get(api_url)

    files = []
    data = response.json()

    for item in data:
        if 'type' in item and item['type'] == 'file':
            file_name = item['name']
            if file_name.endswith('.txt'):
                file_name = file_name[:-4]  # Remove the ".txt" extension
            files.append(file_name)

    return files

print(list_files_in_github_directory())
