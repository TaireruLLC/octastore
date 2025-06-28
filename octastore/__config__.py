"""Public config file for OctaStore package"""
import os
import platform

def find_os_data_path():
    """Function to find internal data path based on OS type (e.g., Windows = C:/Users/[USER]/AppData/LocalLow) and return it as a string."""
    system = platform.system()
    home = os.path.expanduser("~")

    if system == "Windows":
        path = os.path.join(home, "AppData", "LocalLow")
    elif system == "Darwin":  # macOS
        path = os.path.join(home, "Library", "Application Support")
    else:  # Assume Linux/Unix
        path = os.path.join(home, ".local", "share")

    return path

class configClass:
    def __init__(self):
        self.app_name = "OctaStore"
        self.publisher = "Taireru LLC"
        self.version = "0.1.0"
        self.show_logs = True
        self.use_offline = True
        self.use_version_path = True
        self.datpath = f"{find_os_data_path()}/{self.publisher}/{self.app_name}/{self.version}/data/octastore/"
        
    def setdatpath(self):
        self.datpath = f"{find_os_data_path()}/{self.publisher}/{self.app_name}/{self.version}/data/octastore/"
    
    @property
    def cleanpath(self) -> str:
        return f"{find_os_data_path()}/{self.publisher}/{self.app_name}/{self.version}" if self.use_version_path else f"{find_os_data_path()}/{self.publisher}/{self.app_name}"

config = configClass()