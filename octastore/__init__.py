"""
OctaStore: A module for managing data storage in a GitHub repository, allowing reading, writing, uploading, and deleting files.
"""
import sys
import os
from fancyutil import NotificationManager as nm, init as fancy_init
from .octastore import OctaStore as OctaStoreLegacy, init, hasdataloaded, is_online
from .octacluster import OctaStore
from .dbf import DataBase, Object, KeyValue, All
from .octaFile import OctaFile
from .__config__ import config as __config__

original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

fancy_init(display_credits=False)

sys.stdout.close()
sys.stdout = original_stdout



# Initialize LogManager instance
LogManager: nm = nm()

__all__ = [
    "init", "is_online",
    "hasdataloaded", "__config__",
    "OctaStoreLegacy", "OctaStore",
    "DataBase",
    "KeyValue", "Object", "KeyValue", "All",
    "LogManager", "OctaFile",
]