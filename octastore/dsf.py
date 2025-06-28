import os
import json
from cryptography.fernet import Fernet
from typing import Optional, Union, Dict, Any, List
from altcolor import cPrint
from .octastore import OctaStore, is_online
import requests
global canUse
from .config import canUse
from .__config__ import config as __config__
from .octacluster import OctaCluster
import jsonpickle
import math
from moviepy.video.io.VideoFileClip import VideoFileClip  # Video handling

class KeyValue:
    """
    Represents a key-value pair for storing data.
    
    Attributes:
        key (str): The key to represent the pair.
        value (Any): The value connected to the key. Can be anything.
    """

    def __init__(self, key: str, value: Any):
        self.key: str = key
        self.value: Any = value

class Object:
    """
    Represents a OctaStore object, but is just an empty class.
    """
    
    def __init__(self):
        pass

BaseKeyValue: KeyValue = KeyValue("N/A", "N/A")
BaseObject: Object = Object()

def is_probably_encrypted(data: str) -> bool:
    try:
        # Fernet-encrypted strings are Base64-encoded, 128+ chars, no curly braces
        return not data.strip().startswith("{")
    except:
        return True

class DataStore:
    """
    Handles data storage and retrieval, supporting online OctaStore and offline backups.
    """

    def __init__(self, db: Union[OctaStore, OctaCluster], encryption_key: bytes):
        """
        Initializes the DataSystem with a OctaStore instance and encryption key.

        Args:
            db (Union[OctaStore, OctaCluster]): The OctaStore or OctaCluster instance for online storage.
            encryption_key (bytes): The key used for encryption.
        """
        self.db: Union[OctaStore, OctaCluster] = db
        self.encryption_key: bytes = encryption_key
        self.fernet: Fernet = Fernet(self.encryption_key)

    def encrypt_data(self, data: str) -> bytes:
        """
        Encrypts the given data.

        Args:
            data (str): The data to encrypt.

        Returns:
            bytes: The encrypted data.
        """
        return self.fernet.encrypt(data.encode('utf-8'))

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """
        Decrypts the given encrypted data.

        Args:
            encrypted_data (bytes): The data to decrypt.

        Returns:
            str: The decrypted data.
        """
        return self.fernet.decrypt(encrypted_data).decode('utf-8')

    def save_data(self, key: str, value: Any, path: Optional[str] = "data", isencrypted: Optional[bool] = False) -> None:
        """
        Saves data to online storage, or offline backup if offline.

        Args:
            key (str): The key associated with the data.
            value (Any): The data to store.
            path (Optional[str]): The storage path. Defaults to "data".
            isencrypted (Optional[bool]): Whether to encrypt the data. Defaults to False.
            
        Returns:
            None: N/A.
        """
        try:
            serialized_data = jsonpickle.encode(value)
            data: str = (
                self.encrypt_data(serialized_data).decode('utf-8') if isencrypted else serialized_data
            )
            full_path = os.path.join(path, f"{key}.json").replace("\\", "/")

            if is_online():
                response_code = self.db.write_data(full_path, data, message=f"Saved {key}")
                if response_code in (200, 201):
                    if __config__.show_logs: cPrint("GREEN", f"Successfully saved online data for {key}.")
                else:
                    if __config__.show_logs: cPrint("RED", f"Error saving online data for {key}. HTTP Status: {response_code}")
            else:
                if __config__.show_logs: cPrint("YELLOW", "Network is offline, saving to offline backup version.")
                if __config__.use_offline:
                    self.load_offline_data(key, value, isencrypted)
        except Exception as e:
            
