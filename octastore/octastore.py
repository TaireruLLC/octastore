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
        return response.status_code in [200, 201, 204]
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
        if response.status_code in [200, 201, 204]:
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
                response: requests.Response = requests.delete(url, headers=self.headers, json=payload)
                return response.status_code
            else:
                return 404
        except Exception as e:
            raise Exception(f"Error: {e}")

    @staticmethod
    def generate_example() -> None:
        """Generate an example of how to use OctaStore"""
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        # Get the directory of the current file (octastore.py)
        current_dir = os.path.dirname(__file__)
        
        # Construct the full path to example.py
        example_file_path = os.path.join(current_dir, "example.py")
        
        # Read from test.py
        with open(example_file_path, "rb") as file:
            example_code: bytes = file.read()
        
        # Write to example_code.py
        with open("example_code.py", "wb") as file:
            file.write(example_code)

    def upload_file(self, file_path: str, remote_path: str, message: Optional[str] = "Uploaded file") -> int:
        """Upload a file to the online database."""
        
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        try:
            with open(file_path, "rb") as file:
                encoded_data: Union[str, None] = base64.b64encode(file.read()).decode('utf-8')

            payload: Dict[str, Union[str, None]] = {
                "message": message,
                "content": encoded_data,
                "branch": self.branch
            }

            url: str = self._get_file_url(remote_path)
            response: requests.Response = requests.put(url, headers=self.headers, json=payload)
            return response.status_code
        except Exception as e:
            raise Exception(f"Error uploading file: {e}")

    def download_file(self, remote_path: str, local_path: str) -> int:
        """Download a file from the online database."""
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        try:
            content, _ = self._get_file_content(remote_path)
            if content:
                with open(local_path, "wb") as file:
                    file.write(base64.b64decode(content))
                return 200
            return 404
        except Exception as e:
            raise Exception(f"Error downloading file: {e}")

    def get_file_last_modified(self, path: str) -> Optional[float]:
        """Get the last modified timestamp of the file from the GitHub repository."""
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        try:
            url: str = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits?path={path}"
            response: requests.Response = requests.get(url, headers=self.headers)
            if response.status_code in [200, 201, 204]:
                commits: Any = response.json()
                if commits:
                    # Get the date of the most recent commit
                    last_modified: Any = commits[0]['commit']['committer']['date']
                    return datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        except Exception as e:
            raise Exception(f"Error getting last modified time for {path}: {e}")
        return None
    
    def get_all_keys(self, path: str) -> List[str]:
        """
        Retrieves all keys (file names) from the repository.

        Args:
            path (str): The directory path in the repository.

        Returns:
            List[str]: A list of keys (file names) without extensions.
        """
        if not canUse: raise ModuleNotFoundError("No module named 'octastore'")
        url: str = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
        response: requests.Response = requests.get(url, headers=self.headers)
        if response.status_code in [200, 201, 204]:
            files: List[Dict[str, Union[str, int, float, bool]]] = response.json()
            return [file['name'].replace('.json', '') for file in files if file['name'].endswith('.json')]
        return []

def init(show_credits: Optional[bool] = True) -> None:
    """Initialize the OctaStore module."""
    global canUse
    
    if show_credits:
        cPrint("BLUE", "\n\nThanks for using OctaStore! Check out our other products at 'https://tairerullc.vercel.app'\n\n")
        wait(2)
        
    canUse = True