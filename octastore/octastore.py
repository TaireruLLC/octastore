import requests
import base64
import os
from typing import Optional, Tuple, Union, Dict, List, Any
from altcolor import cPrint, init; init(show_credits=False)
from datetime import datetime
from time import sleep as wait
from .config import canUse

# Define a variable to check if data is loaded/has been found before continuing to try to update any class instances
hasdataloaded: bool = False

# Define a function to check if the user is online
def is_online(url: Optional[str] = 'http://www.google.com', timeout: Optional[int] = 5) -> bool:
    """Check if the user is online before continuing code"""
    
    if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
    try:
        response: requests.Response = requests.get(url, timeout=timeout)
        # If the response status code is 200, we have an internet connection
        return response.status_code == 200
    except requests.ConnectionError:
        return False
    except requests.Timeout:
        return False

class OctaStore:
    def __init__(self, token: str, repo_owner: str, repo_name: str, branch: Optional[str] = 'main'):
        self.token: str = token
        self.repo_owner: str = repo_owner
        self.repo_name: str = repo_name
        self.branch: Optional[str] = branch
        self.headers: Dict[str, str] = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _get_file_url(self, path: str) -> str:
        """Reterive GitHub url for file"""
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        return f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"

    def _get_file_content(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get the content of a file"""
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        url: str = self._get_file_url(path)
        response: requests.Response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            file_data: Dict[str, Union[str, bytes]] = response.json()
            sha: str = file_data['sha']
            content: str = base64.b64decode(file_data['content']).decode('utf-8')
            return content, sha
        return None, None

    def read_data(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Read a file and return it's data as content and sha"""
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        content, sha = self._get_file_content(path)
        return content, sha

    def write_data(self, path: str, data: str, message: Optional[str] = "Updated data") -> int:
        """Write to/update a file's content"""
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        try:
            url: str = self._get_file_url(path)
            content, sha = self._get_file_content(path)
            encoded_data: str = base64.b64encode(data.encode('utf-8')).decode('utf-8')

            payload: Dict[str, Union[str, None]] = {
                "message": message,
                "content": encoded_data,
                "branch": self.branch
            }

            if sha:
                payload["sha"] = sha

            response: requests.Response = requests.put(url, headers=self.headers, json=payload)
            return response.status_code
        except Exception as e:
            raise Exception(f"Error: {e}")

    def delete_data(self, path: str, message: str = "Deleted data") -> int:
        """Delete data for a file"""
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        try:
            url: str = self._get_file_url(path)
            _, sha = self._get_file_content(path)

            if sha:
                payload: Dict[str, str] = {
                    "message": message,
                    "sha": sha,
                    "branch": self.branch
                }
  
