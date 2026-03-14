"""
GitHub Integration Tools for ABC AI Agent
Provides GitHub API operations: read repos, create issues/PRs, read code
Requires: GitHub Personal Access Token
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import requests, fallback to urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error


class GitHubTools:
    """GitHub API integration tools"""
    
    def __init__(self, token: str):
        """
        Initialize GitHub tools
        
        Args:
            token: GitHub Personal Access Token
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ABC-AI-Agent"
        }
        
        # Verify token on init
        self._verify_token()
        logger.info("🔗 GitHub tools initialized")
    
    def _verify_token(self) -> bool:
        """Verify the GitHub token is valid"""
        try:
            response = self._make_request("/user")
            if response.get('login'):
                logger.info(f"✅ GitHub authenticated as: {response['login']}")
                return True
            return False
        except Exception as e:
            logger.error(f"GitHub token verification failed: {e}")
            return False
    
    def _make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Make authenticated request to GitHub API"""
        url = f"{self.base_url}{endpoint}"
        
        if HAS_REQUESTS:
            try:
                if method == "GET":
                    response = requests.get(url, headers=self.headers, timeout=30)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, json=data, timeout=30)
                elif method == "PATCH":
                    response = requests.patch(url, headers=self.headers, json=data, timeout=30)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                return response.json() if response.text else {}
                
            except requests.exceptions.RequestException as e:
                logger.error(f"GitHub API request failed: {e}")
                raise
        else:
            # Fallback to urllib
            import urllib.request
            import json
            
            req = urllib.request.Request(url, headers=self.headers, method=method)
            if data and method in ["POST", "PATCH"]:
                req.add_header('Content-Type', 'application/json')
                req.data = json.dumps(data).encode('utf-8')
            
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    return json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                logger.error(f"GitHub API error: {e.code} - {e.reason}")
                raise
    
    def _parse_repo(self, repo_str: str) -> Tuple[str, str]:
        """Parse owner/repo from string"""
        # Handle various formats:
        # - "owner/repo"
        # - "https://github.com/owner/repo"
        # - "github.com/owner/repo"
        
        repo_str = repo_str.strip()
        
        # Remove URL prefixes
        if 'github.com/' in repo_str:
            repo_str = repo_str.split('github.com/')[-1]
        
        # Remove trailing slash or .git
        repo_str = repo_str.rstrip('/').replace('.git', '')
        
        parts = repo_str.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
        
        raise ValueError(f"Invalid repository format: {repo_str}")
    
    def get_repo_info(self, repo: str) -> Dict:
        """
        Get repository information
        
        Args:
            repo: Repository (owner/repo or full URL)
            
        Returns:
            Dict with repo info
        """
        try:
            owner, repo_name = self._parse_repo(repo)
            data = self._make_request(f"/repos/{owner}/{repo_name}")
            
            return {
                "success": True,
                "name": data.get('name'),
                "full_name": data.get('full_name'),
                "description": data.get('description'),
                "url": data.get('html_url'),
                "stars": data.get('stargazers_count'),
                "forks": data.get('forks_count'),
                "open_issues": data.get('open_issues_count'),
                "language": data.get('language'),
                "created_at": data.get('created_at'),
                "updated_at": data.get('updated_at'),
                "default_branch": data.get('default_branch')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_issues(self, repo: str, state: str = "open") -> Dict:
        """
        List issues in a repository
        
        Args:
            repo: Repository (owner/repo)
            state: open, closed, or all
            
        Returns:
            Dict with issues list
        """
        try:
            owner, repo_name = self._parse_repo(repo)
            data = self._make_request(f"/repos/{owner}/{repo_name}/issues?state={state}&per_page=10")
            
            issues = []
            for issue in data:
                issues.append({
                    "number": issue.get('number'),
                    "title": issue.get('title'),
                    "state": issue.get('state'),
                    "url": issue.get('html_url'),
                    "created_at": issue.get('created_at'),
                    "user": issue.get('user', {}).get('login')
                })
            
            return {
                "success": True,
                "repo": f"{owner}/{repo_name}",
                "count": len(issues),
                "issues": issues
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_issue(self, repo: str, title: str, body: str = "") -> Dict:
        """
        Create a new issue
        
        Args:
            repo: Repository (owner/repo)
            title: Issue title
            body: Issue body/description
            
        Returns:
            Dict with created issue info
        """
        try:
            owner, repo_name = self._parse_repo(repo)
            data = self._make_request(
                f"/repos/{owner}/{repo_name}/issues",
                method="POST",
                data={"title": title, "body": body}
            )
            
            return {
                "success": True,
                "number": data.get('number'),
                "title": data.get('title'),
                "url": data.get('html_url'),
                "state": data.get('state'),
                "created_at": data.get('created_at')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, repo: str, path: str, ref: str = None) -> Dict:
        """
        Read a file from a repository
        
        Args:
            repo: Repository (owner/repo)
            path: File path in repo
            ref: Branch/tag/commit (default: default branch)
            
        Returns:
            Dict with file content
        """
        try:
            owner, repo_name = self._parse_repo(repo)
            
            # Get file content
            url = f"/repos/{owner}/{repo_name}/contents/{path}"
            if ref:
                url += f"?ref={ref}"
            
            data = self._make_request(url)
            
            import base64
            content = base64.b64decode(data.get('content', '')).decode('utf-8')
            
            return {
                "success": True,
                "path": data.get('path'),
                "size": data.get('size'),
                "url": data.get('html_url'),
                "content": content,
                "sha": data.get('sha')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_directory(self, repo: str, path: str = "", ref: str = None) -> Dict:
        """
        List contents of a directory in a repository
        
        Args:
            repo: Repository (owner/repo)
            path: Directory path (empty for root)
            ref: Branch/tag/commit
            
        Returns:
            Dict with directory listing
        """
        try:
            owner, repo_name = self._parse_repo(repo)
            
            url = f"/repos/{owner}/{repo_name}/contents/{path}"
            if ref:
                url += f"?ref={ref}"
            
            data = self._make_request(url)
            
            items = []
            for item in data:
                items.append({
                    "name": item.get('name'),
                    "type": item.get('type'),  # file or dir
                    "path": item.get('path'),
                    "size": item.get('size', 0) if item.get('type') == 'file' else None,
                    "url": item.get('html_url')
                })
            
            return {
                "success": True,
                "repo": f"{owner}/{repo_name}",
                "path": path or "/",
                "count": len(items),
                "items": items
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_pull_request(self, repo: str, title: str, head: str, base: str, body: str = "") -> Dict:
        """
        Create a pull request
        
        Args:
            repo: Repository (owner/repo)
            title: PR title
            head: Branch with changes
            base: Branch to merge into
            body: PR description
            
        Returns:
            Dict with PR info
        """
        try:
            owner, repo_name = self._parse_repo(repo)
            data = self._make_request(
                f"/repos/{owner}/{repo_name}/pulls",
                method="POST",
                data={
                    "title": title,
                    "head": head,
                    "base": base,
                    "body": body
                }
            )
            
            return {
                "success": True,
                "number": data.get('number'),
                "title": data.get('title'),
                "url": data.get('html_url'),
                "state": data.get('state'),
                "head": data.get('head', {}).get('ref'),
                "base": data.get('base', {}).get('ref')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def detect_and_execute(self, message: str) -> Optional[Dict]:
        """
        Detect GitHub-related commands and execute them
        
        Args:
            message: User message
            
        Returns:
            Result dict if a GitHub command was executed
        """
        import re
        msg_lower = message.lower().strip()
        
        # Get repo info: "info for repo X" or "tell me about github.com/owner/repo"
        info_patterns = [
            r'(?:info|information|about|details)\s+(?:for|on|about)\s+(?:repo\s+)?["\']?([^"\']+)["\']?',
            r'what\s+is\s+["\']?([^"\']+)["\']?\s+on\s+github',
        ]
        for pattern in info_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                repo = match.group(1).strip()
                return self.get_repo_info(repo)
        
        # List issues: "list issues for repo X" or "show open issues in X"
        issues_match = re.search(r'(?:list|show)\s+(?:(\w+)\s+)?issues\s+(?:for|in)\s+["\']?([^"\']+)["\']?', msg_lower)
        if issues_match:
            state = issues_match.group(1) or "open"
            repo = issues_match.group(2).strip()
            return self.list_issues(repo, state)
        
        # Create issue: "create issue 'title' in repo X" or "new issue in X: title"
        issue_create_match = re.search(r'(?:create|new)\s+issue\s+[\'"](.+?)[\'"]\s+(?:in|for)\s+["\']?([^"\']+)["\']?', msg_lower)
        if issue_create_match:
            title = issue_create_match.group(1)
            repo = issue_create_match.group(2).strip()
            return self.create_issue(repo, title)
        
        # Read file: "read file X from repo Y" or "show me X in repo Y"
        file_patterns = [
            r'(?:read|show)\s+(?:file\s+)?["\']?([^"\']+)["\']?\s+(?:from|in)\s+["\']?([^"\']+)["\']?',
            r'what\s+is\s+in\s+["\']?([^"\']+)["\']?\s+(?:in|from)\s+["\']?([^"\']+)["\']?',
        ]
        for pattern in file_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                path = match.group(1).strip()
                repo = match.group(2).strip()
                return self.read_file(repo, path)
        
        # List directory: "list files in repo X" or "show directory Y in repo X"
        dir_match = re.search(r'(?:list|show)\s+(?:files?|directory|contents?)\s+(?:in|of|from)\s+["\']?([^"\']+)["\']?(?:\s+(?:in|from)\s+["\']?([^"\']+)["\']?)?', msg_lower)
        if dir_match:
            if dir_match.group(2):  # Has both path and repo
                path = dir_match.group(1).strip()
                repo = dir_match.group(2).strip()
            else:  # Just repo, root directory
                path = ""
                repo = dir_match.group(1).strip()
            return self.list_directory(repo, path)
        
        # Create PR: "create PR from X to Y in repo Z" or "pull request from X to Y in Z"
        pr_match = re.search(r'(?:create\s+)?(?:pull\s+request|pr)\s+["\']?([^"\']+)["\']?\s+from\s+["\']?([^"\']+)["\']?\s+to\s+["\']?([^"\']+)["\']?(?:\s+in\s+["\']?([^"\']+)["\']?)?', msg_lower)
        if pr_match:
            title = pr_match.group(1).strip()
            head = pr_match.group(2).strip()
            base = pr_match.group(3).strip()
            repo = pr_match.group(4).strip() if pr_match.group(4) else head.split(':')[0] if ':' in head else None
            if repo:
                return self.create_pull_request(repo, title, head, base)
        
        return None


# For testing
if __name__ == "__main__":
    import os
    
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Set GITHUB_TOKEN environment variable to test")
        exit(1)
    
    tools = GitHubTools(token)
    
    print("Testing get_repo_info...")
    result = tools.get_repo_info("octocat/Hello-World")
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Repo: {result.get('full_name')}, Stars: {result.get('stars')}")
    
    print("\n✅ GitHub tools test completed!")
