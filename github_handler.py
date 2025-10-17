from github import Github
import os
import time
import requests

def create_or_update_repo(task: str, round_num: int, files: dict, token: str) -> dict:
    if not token:
        raise ValueError("GITHUB_TOKEN required")
    
    g = Github(token)
    username = g.get_user().login
    repo_name = f"{task.replace(' ', '-').replace('/', '-')}-app".lower()[:100]
    
    try:
        repo = g.get_user().get_repo(repo_name)
        if round_num == 1:
            raise Exception("Repo already exists")
    except:
        repo = g.get_user().create_repo(repo_name, private=False, auto_init=True)
        branch = repo.get_branch('main')
    else:
        branch = repo.get_branch('main')
    
    for path in files.keys():
        if path in ['.git', '.gitignore']:
            continue
        content = files[path]
        try:
            repo.delete_file(path, f"Delete {path}", branch=branch.name, sha=repo.get_contents(path).sha)
        except:
            pass
        repo.create_file(path, f"Update {path} for Round {round_num}", content, branch=branch.name)
    
    commits = list(repo.get_commits(sha=branch.name))
    commit_sha = commits[0].sha if commits else 'unknown'
    
    try:
        repo.edit(
            has_pages=True,
            pages_branch='main',
            pages_source_path='/ (root)'
        )
    except Exception as e:
        print(f"Pages enable failed: {e}")
    
    pages_url = f"https://{username}.github.io/{repo_name}/"
    for _ in range(12):
        try:
            resp = requests.get(pages_url, timeout=5)
            if resp.status_code == 200:
                break
        except:
            pass
        time.sleep(10)
    
    return {
        'repo_url': repo.html_url,
        'commit_sha': commit_sha,
        'pages_url': pages_url
    }
