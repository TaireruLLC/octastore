from typing import Optional, Tuple, List, Dict
from .octastore import OctaStore as OctaStoreLegacy

class OctaStore:
    def __init__(self, octastores: List[Dict[str, str]]) -> None:
        self.octastores: List[OctaStoreLegacy] = [OctaStoreLegacy(**gb) for gb in octastores]
        self.current_index: int = 0

    def _get_active_octastore(self) -> Optional['OctaStoreLegacy']:
        if self.current_index < len(self.octastores):
            return self.octastores[self.current_index]
        return None

    def _switch_to_next_octastore(self) -> bool:
        if self.current_index + 1 < len(self.octastores):
            self.current_index += 1
            return True
        return False
    
    def __getattr__(self, attr):
        octastore = self._get_active_octastore()
        if octastore and hasattr(octastore, attr):
            return getattr(octastore, attr)
        raise AttributeError(f"'OctaStore' object has no attribute '{attr}'")

    # Forward internal method to the current octastore
    def _get_file_url(self, path: str) -> Optional[str]:
        octastore = self._get_active_octastore()
        if octastore:
            return octastore._get_file_url(path)
        return None

    def _get_file_content(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        # Search all octastores for first with content
        for octastore in self.octastores:
            content, sha = octastore._get_file_content(path)
            if content is not None:
                return content, sha
        return None, None

    def read_data(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        for octastore in self.octastores:
            content, sha = octastore.read_data(path)
            if content is not None:
                return content, sha
        return None, None

    def write_data(self, path: str, data: str, message: Optional[str] = "Updated data") -> int:
        while self.current_index < len(self.octastores):
            octastore = self._get_active_octastore()
            if octastore:
                status = octastore.write_data(path, data, message)
                if status in {200, 201}:
                    return status
                if not self._switch_to_next_octastore():
                    return status
        return 507

    def delete_data(self, path: str, message: Optional[str] = "Deleted data") -> int:
        status_codes = [gb.delete_data(path, message) for gb in self.octastores]
        return 200 if any(status == 200 for status in status_codes) else 404

    def upload_file(self, file_path: str, remote_path: str, message: Optional[str] = "Uploaded file") -> int:
        while self.current_index < len(self.octastores):
            octastore = self._get_active_octastore()
            if octastore:
                status = octastore.upload_file(file_path, remote_path, message)
                if status in {200, 201}:
                    return status
                if not self._switch_to_next_octastore():
                    return status
        return 507

    def download_file(self, remote_path: str, local_path: str) -> int:
        for octastore in self.octastores:
            status = octastore.download_file(remote_path, local_path)
            if status == 200:
                return status
        return 404

    def get_file_last_modified(self, path: str) -> Optional[float]:
        timestamps = [gb.get_file_last_modified(path) for gb in self.octastores]
        valid_ts = [ts for ts in timestamps if ts is not None]
        return max(valid_ts, default=None)

    def get_all_keys(self, path: str) -> List[str]:
        for octastore in self.octastores:
            keys = octastore.get_all_keys(path)
            if keys:
                return keys
        return []

    @staticmethod
    def generate_example() -> None:
        # Static method forwarding to OctaStore (pick the OctaStore class itself)
        OctaStore.generate_example()