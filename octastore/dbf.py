import os
import json
from cryptography.fernet import Fernet
from typing import Optional, Union, Dict, Any, List
from altcolor import cPrint
from .octastore import OctaStore as OctaStoreLegacy, is_online
import requests
global canUse
from .config import canUse
from .__config__ import config as __config__
from .octacluster import OctaStore
import jsonpickle
import math
from moviepy.video.io.VideoFileClip import VideoFileClip  # Video handling

class KeyValue:
    """
    Represents a key-value pair for storing data.
    
    Args:
        key (str): The key to represent the pair.
        value (Any): The value connected to the key. Can be anything.
    """

    def __init__(self, key: Union[str, None] = None, value: Any = None):
        self.key: Union[str, None] = key
        self.value: Any = value

class Object:
    """
    Represents a OctaStore object.
    
    Args:
        objectname (str): The name of the object.
        objectinstance (Any): The instance of the object.
        attributes (Optional[Union[None, List[str]])]: The list of attributes to save (only use if you don't want to save the entire instance).
    """
    
    def __init__(self, objectname: Union[str, None] = None, objectinstance: Any = None, attributes: Optional[Union[None, List[str]]] = None):
        self.objectname: Union[str, None] = objectname
        self.objectinstance: Any = objectinstance
        self.attributes: Union[None, List[str]] = attributes
    
class All:
    """
    Represents all OctaStore data types, hence it has every argument of the others.
    
    Args:
        key (str): The key to represent the pair.
        value (Any): The value connected to the key. Can be anything.
        objectname (str): The name of the object.
        objectinstance (Any): The instance of the object.
        attributes (Optional[Union[None, List[str]])]: The list of attributes to save (only use if you don't want to save the entire instance).
    """
    
    def __init__(self, key: Union[str, None] = None, value: Any = None, objectname: Union[str, None] = None, objectinstance: Any = None, attributes: Optional[Union[None, List[str]]] = None):
        self.key: Union[str, None] = key
        self.value: Any = value
        self.objectname: Union[str, None] = objectname
        self.objectinstance: Any = objectinstance
        self.attributes: Union[None, List[str]] = attributes

_FERNET_TOKEN_MINLEN = 128  # Fernet token minimum length

def is_probably_encrypted(data: str) -> bool:
    """
    Determines if the data appears to be Fernet-encrypted.

    Returns True only if the data looks encrypted (Base64, no JSON markers).
    """
    data = data.strip()
    if len(data) < _FERNET_TOKEN_MINLEN:
        return False
    return all(c.isalnum() or c in "-_" for c in data.rstrip("="))

class DataBase:
    """
    Handles data storage and retrieval, supporting online OctaStore and offline backups.
    """

    def __init__(self, core: Union[OctaStore, OctaStoreLegacy], encryption_key: bytes):
        """
        Initializes the DataSystem with a OctaStore instance and encryption key.

        Attributes:
            core (Union[OctaStore, OctaStore]): The OctaStore or OctaStore instance for online storage.
            encryption_key (bytes): The key used for encryption.
            fernet (Fernet): The Fernet instance for the db.
        """
        self.core: Union[OctaStore, OctaStoreLegacy] = core
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

    def decrypt_data(self, encrypted_data: Union[bytes, str]) -> str:
        """
        Decrypts the given encrypted data.

        Args:
            encrypted_data (bytes | str): The data to decrypt.

        Returns:
            str: The decrypted data.
        """
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode("utf-8")
        return self.fernet.decrypt(encrypted_data).decode("utf-8")

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
                response_code = self.core.write_data(full_path, data, message=f"Saved {key}")
                if response_code in [200, 201, 204]:
                    if __config__.show_logs: cPrint("GREEN", f"Successfully saved online data for {key}.")
                else:
                    if __config__.show_logs: cPrint("RED", f"Error saving online data for {key}. HTTP Status: {response_code}")
            else:
                if __config__.show_logs: cPrint("YELLOW", "Network is offline, saving to offline backup version.")
                if __config__.use_offline:
                    self.load_offline_data(key, value, isencrypted)
        except Exception as e:
            if __config__.show_logs: cPrint("RED", f"Error: {e}")
            if __config__.show_logs: cPrint("GREEN", "Attempting to save to offline backup version anyway.")
            try:
                if __config__.use_offline:
                    self.load_offline_data(key, value, isencrypted)
            except Exception as e:
                raise Exception(f"Error saving to offline backup: {e}")


    def load_data(self, key: str, isencrypted: bool, path: Optional[str] = "data") -> Union[KeyValue, None]:
        """
        Loads data from online storage or offline backup.

        Args:
            key (str): The key associated with the data.
            isencrypted (bool): Whether the data is encrypted.
            path (Optional[str]): The storage path. Defaults to "data".

        Returns:
            Union[KeyValue, None]: The retrieved data or None if not found.
        """
        path = os.path.join(path, f"{key}.json").replace("\\", "/")
        try:
            if is_online():
                online_data, _ = self.core.read_data(path)

                if online_data:
                    try:
                        if isencrypted and is_probably_encrypted(online_data):
                            decrypted_data = self.decrypt_data(online_data.encode("utf-8"))
                        else:
                            decrypted_data = online_data

                        try:
                            parsed = jsonpickle.decode(decrypted_data)
                            return KeyValue(key, parsed)
                        except Exception as json_err:
                            raise Exception(f"Deserialization error for key '{key}': {json_err}")
                    except Exception as decrypt_err:
                        raise Exception(f"Decryption or decoding error for key '{key}': {decrypt_err}")
                else:
                    if __config__.show_logs: cPrint("RED", f"No online data found for {key}.")
            else:
                if __config__.show_logs: cPrint("YELLOW", "Network is offline, loading from offline backup.")
                if __config__.use_offline:
                    return self.load_offline_data(key, isencrypted)
        except Exception as e:
            raise Exception(f"Error loading data for key '{key}': {e}")
        
    def load_offline_data(self, key: str, value: Any, enc: Optional[bool] = False) -> Union[KeyValue, None]:
        """
        Loads offline data from the local backup.

        Args:
            key (str): The key associated with the data.
            value (Any): The value associated with the key.
            enc (Optional[bool]): Whether the data is encrypted.

        Returns:
            Union[KeyValue, None]: The loaded key-value object, or None if not found.
        """
        if __config__.use_offline:
            path: str = os.path.join(f"{__config__.datpath}/data", f"{key}.octafile")
            if not os.path.exists(path):
                if __config__.show_logs: cPrint("RED", f"No offline data found for key: {key}")
                return None

            try:
                with open(path, "rb") as file:
                    raw_data = file.read()
                    decoded_data = self.decrypt_data(raw_data) if enc else raw_data.decode("utf-8")
                    v = jsonpickle.decode(decoded_data) or value
                    return KeyValue(key, v)
            except Exception as e:
                raise Exception(f"Failed to load offline data for '{key}': {e}")

    def delete_data(self, key: str, path: Optional[str] = "data", deleteoffline: Optional[bool] = False) -> None:
        """
        Deletes data from online storage and optionally offline storage.

        Args:
            key (str): The key associated with the data.
            path (Optional[str]): The storage path. Defaults to "data".
            deleteoffline (Optional[bool]): Whether to delete offline storage as well. Defaults to False.
            
        Returns:
            None: N/A.
        """
        full_path = os.path.join(path, f"{key}.json").replace("\\", "/")
        try:
            response_code: int = self.core.delete_data(full_path, message=f"Deleted {key}")
            if response_code in (200, 204):
                if __config__.show_logs: cPrint("GREEN", f"Successfully deleted online data for {key}.")
            elif response_code == 404:
                if __config__.show_logs: cPrint("RED", f"No online data found for {key}.")
            else:
                if __config__.show_logs: cPrint("RED", f"Error deleting online data for {key}. HTTP Status: {response_code}")
        except Exception as e:
            if __config__.show_logs: cPrint("RED", f"Error deleting online data: {e}")

        if deleteoffline:
            offline_path: str = os.path.join(f"{__config__.datpath}/data", f"{key}.octafile")
            if os.path.exists(offline_path):
                os.remove(offline_path)
                if __config__.show_logs: cPrint("GREEN", f"Successfully deleted offline backup for {key}.")
            else:
                if __config__.show_logs: cPrint("RED", f"No offline backup found for {key}.")
                
    def save_object(self, objectname: str, objectinstance: Any, isencrypted: bool, attributes: Optional[Union[None, List[str]]] = None, path: Optional[str] = "objects") -> None:
        """
        Save a object's attribute data to the database, with optional encryption and local backup.

        Args:
            objectname (str): The object's name.
            objectinstance (Any): The object instance containing data to save.
            isencrypted (bool): Whether to encrypt the data.
            attributes (Optional[Union[None, List[str]]]): List of attributes to save; defaults to all.
            path (Optional[str]): The path for saving data; defaults to "objects".
            
        Returns:
            None: N/A.
        """
        
        try:
            # Extract object data
            if attributes:
                object_dict = {var: getattr(objectinstance, var) for var in attributes if hasattr(objectinstance, var)}
                object_data = json.dumps(object_dict)  # <-- Convert dict to JSON string
            else:
                object_data = jsonpickle.encode(objectinstance)

            # Encrypt data if required
            if isencrypted:
                encrypted_data: str = self.encrypt_data(object_data).decode('utf-8')
            else:
                encrypted_data: str = object_data

            # Format the path
            full_path: str = f"{path}/{objectname}.json" if not path.endswith("/") else f"{path}{objectname}.json"

            # Save data online
            if is_online():
                response_code = self.core.write_data(full_path, encrypted_data, message=f"Saved data for {objectname}")
                if response_code in [200, 201, 204]:
                    if __config__.show_logs: cPrint("GREEN", f"Successfully saved online data for {objectname}.")
                    self.save_offline_object(objectname, objectinstance, attributes)
                else:
                    if __config__.show_logs: cPrint("RED", f"Error saving online data for {objectname}. HTTP Status: {response_code}")
            else:
                if __config__.show_logs: cPrint("YELLOW", "Network is offline, saving to offline backup version.")
                if __config__.use_offline:
                    self.save_offline_object(objectname, objectinstance, attributes)
        except Exception as e:
            if __config__.show_logs: cPrint("RED", f"Error: {e}")
            if __config__.use_offline:
                if __config__.show_logs: cPrint("GREEN", "Attempting to save to offline backup version anyway.")
                try:
                    self.save_offline_object(objectname, objectinstance, attributes)
                except Exception as e:
                    raise Exception(f"Error: {e}")

    def save_offline_object(self, objectname: str, objectinstance: Any, attributes: Optional[Union[None, List[str]]] = None) -> None:
        """
        Save full object instance to a local backup using jsonpickle.

        Args:
            objectname (str): The object's name.
            objectinstance (Any): The object instance to save.
            attributes (Optional[Union[None, List[str]]]): List of attributes to save; defaults to all.
            
        Returns:
            None: N/A.
        """
        if __config__.use_offline:
            if not os.path.exists(f"{__config__.datpath}/objects"):
                os.makedirs(f"{__config__.datpath}/objects")

            # Serialize full object using jsonpickle
            serialized_data: str = jsonpickle.encode(objectinstance)

            # Encrypt if needed
            encrypted_data: bytes = self.encrypt_data(serialized_data)
            offline_path: str = os.path.join(f"{__config__.datpath}/objects", f"{objectname}.octafile")

            try:
                with open(offline_path, "wb") as file:
                    file.write(encrypted_data)
                if __config__.show_logs: cPrint("GREEN", f"Successfully saved full offline backup for {objectname}.")
            except Exception as e:
                raise Exception(f"Error saving full offline data: {e}")

    def load_object(self, objectname: str, objectinstance: Any, isencrypted: bool) -> None:
        """
        Load a object's attribute data from the database or local backup.

        Args:
            objectname (str): The object's name.
            objectinstance (Any): The object instance to populate with data.
            isencrypted (bool): Whether to decrypt the data.
        
        Returns:
            None: N/A.
        """
        
        try:
            path: str = f"objects/{objectname}.json"
            offline_path: str = f"{__config__.datpath}/objects/{objectname}.octafile"

            if is_online():
                online_data, _ = self.core.read_data(path)
                offline_data_exists = os.path.exists(offline_path)

                if online_data:
                    # Compare timestamps to determine which data to use
                    online_timestamp = self.core.get_file_last_modified(path)
                    offline_timestamp = os.path.getmtime(offline_path) if offline_data_exists else 0

                    if offline_data_exists and offline_timestamp > online_timestamp and __config__.use_offline:
                        if __config__.show_logs: cPrint("GREEN", f"Loading offline backup for {objectname} (newer version found).")
                        self.load_offline_object(objectname, objectinstance)
                        self.core.write_data(path, json.dumps(objectinstance.__dict__), "Syncing offline with online")
                    else:
                        if __config__.show_logs: cPrint("GREEN", f"Loading online data for {objectname} (newer version).")
                        if isencrypted:
                            decrypted_data: str = self.decrypt_data(online_data.encode('utf-8'))
                        else:
                            decrypted_data: str = online_data
                        object_data = jsonpickle.decode(decrypted_data)
                        # Ensure we're working with an actual object or dict
                        if hasattr(object_data, '__dict__'):
                            objectinstance.__dict__.update(object_data.__dict__)
                        elif isinstance(object_data, dict):
                            objectinstance.__dict__.update(object_data)
                        else:
                            raise TypeError(f"Unexpected type for decoded data: {type(object_data)}")
                elif offline_data_exists and __config__.use_offline:
                    if __config__.show_logs: cPrint("GREEN", f"Loading offline backup for {objectname} (no online data available).")
                    self.load_offline_object(objectname, objectinstance)
                else:
                    if __config__.show_logs: cPrint("RED", f"No data found for {objectname}.")
            else:
                if __config__.use_offline:
                    if __config__.show_logs: cPrint("YELLOW", "Network is offline, loading from offline backup.")
                    self.load_offline_object(objectname, objectinstance)
        except Exception as e:
            raise Exception(f"Error loading object data: {e}")

    def load_offline_object(self, objectname: str, objectinstance: Any) -> None:
        """
        Load a object's attribute data from a local backup.

        Args:
            objectname (str): The object's name.
            objectinstance (Any): The object instance to populate with data.
        
        Returns:
            None: N/A.
        """
        if __config__.use_offline:
            
            offline_path: str = os.path.join(f"{__config__.datpath}/objects", f"{objectname}.octafile")

            try:
                if os.path.exists(offline_path):
                    with open(offline_path, "rb") as file:
                        encrypted_data = file.read()
                    decrypted_data: str = self.decrypt_data(encrypted_data)
                    object_data: Dict[str, Union[str, int, float]] = json.loads(decrypted_data)
                    for var, value in object_data.items():
                        setattr(objectinstance, var, value)
                    if __config__.show_logs: cPrint("GREEN", f"Successfully loaded offline backup for {objectname}.")
                else:
                    if __config__.show_logs: cPrint("RED", f"No offline backup found for {objectname}.")
            except Exception as e:
                raise Exception(f"Error loading offline backup: {e}")

    def delete_object(self, objectname: str, deletelocalfile: Optional[bool] = False) -> None:
        """
        Delete a object data from the database and optionally from local storage.

        Args:
            objectname (str): The object's name.
            deletelocalfile (Optional[bool]): Whether to delete the local backup; defaults to False.
        
        Returns:
            None: N/A.
        """
        
        online_path: str = f"objects/{objectname}.json"
        offline_path: str = os.path.join(f"{__config__.datpath}/objects", f"{objectname}.octafile")

        try:
            response_code = self.core.delete_data(online_path, message=f"Deleted object '{objectname}'")
            if response_code in [200, 201, 204]:
                if __config__.show_logs: cPrint("GREEN", f"Successfully deleted online object '{objectname}'.")
            elif response_code == 404:
                if __config__.show_logs: cPrint("RED", f"No online object found for '{objectname}'.")
            else:
                if __config__.show_logs: cPrint("RED", f"Error deleting online object. HTTP Status: {response_code}")
        except Exception as e:
            raise Exception(f"Error deleting online account: {e}")

        if deletelocalfile and os.path.exists(offline_path) and __config__.use_offline:
            try:
                os.remove(offline_path)
                if __config__.show_logs: cPrint("GREEN", f"Successfully deleted offline backup for '{objectname}'.")
            except Exception as e:
                raise Exception(f"Error deleting offline backup: {e}")

    def get_all(self, isencrypted: bool, datatype: Optional[Union[All, Object, KeyValue]] = All, path: Optional[str] = f"{__config__.datpath}/data") -> Dict[str, Any]:
        """
        Retrieves all key-value pairs or object data, either from online or offline storage depending on connectivity and configuration.
        
        Args:
            isencrypted (bool): Whether or not the items for retrieval are encrypted.
            datatype (Optional[Union[All, Object, KeyValue]]): The data type of the objects for retrieval. Can be All, Object, or KeyValue. Defaults to All.
            path (Optional[str]): The path of the items for retrieval. Defaults to "/data"
        
        Returns:
            Dict[str, Any]: A dictionary of all retrieved data, with their name as the key and their data as the item.
        """

        def load_offline_file(filepath: str, key: str) -> Optional[Any]:
            try:
                with open(filepath, "rb") as f:
                    raw_data = f.read()
                    decrypted = self.decrypt_data(raw_data) if isencrypted else raw_data.decode("utf-8")
                    return jsonpickle.decode(decrypted)
            except Exception as e:
                if __config__.show_logs:
                    cPrint("RED", f"Error loading offline data for {key}: {e}")
                return None

        def load_online_json(file_path: str, objectname: str) -> Optional[Any]:
            try:
                online_data, _ = self.core.read_data(file_path)
                if not online_data:
                    return None

                decrypted: str
                if isencrypted and is_probably_encrypted(online_data):
                    try:
                        decrypted = self.decrypt_data(online_data)
                    except Exception as e:
                        if __config__.show_logs:
                            cPrint("YELLOW", f"Decryption failed for {objectname}, falling back to plain text: {e}")
                        decrypted = online_data
                else:
                    decrypted = online_data

                return jsonpickle.decode(decrypted)
            except Exception as e:
                if __config__.show_logs:
                    cPrint("RED", f"Failed to load online JSON for {objectname}: {e}")
                return None

        def get_objects() -> Dict[str, Any]:
            all_objects = {}
            if is_online():
                try:
                    url = self.core._get_file_url(path)
                    response = requests.get(url, headers=self.core.headers)
                    if response.status_code not in [200, 201, 204]:
                        if __config__.show_logs:
                            cPrint("RED", f"Error retrieving object files from online database. HTTP Status: {response.status_code}")
                        return all_objects

                    files = response.json() or []
                    if not files and __config__.show_logs:
                        cPrint("YELLOW", "No object files found in the online repository.")

                    for file in files:
                        if file.get('name', '').endswith('.json'):
                            name = file['name'].rsplit('.', 1)[0]
                            obj = load_online_json(f"{path}/{file['name']}", name)
                            if obj is not None:
                                all_objects[name] = obj
                except Exception as e:
                    if __config__.show_logs:
                        cPrint("RED", f"Error retrieving online object data: {e}")
            elif __config__.use_offline:
                if __config__.show_logs:
                    cPrint("YELLOW", "Network is offline, loading object data from local storage.")
                offline_dir = os.path.join(__config__.datpath, path)
                if os.path.exists(offline_dir):
                    for filename in os.listdir(offline_dir):
                        if filename.endswith('.octastore'):
                            name = filename.rsplit('.', 1)[0]
                            obj = load_offline_file(os.path.join(offline_dir, filename), name)
                            if obj is not None:
                                all_objects[name] = obj
                else:
                    if __config__.show_logs:
                        cPrint("YELLOW", f"Offline directory {offline_dir} does not exist.")
            return all_objects

        def get_keyvalues() -> Dict[str, Any]:
            all_data = {}
            if is_online():
                try:
                    for key in self.core.get_all_keys(path):
                        kv = self.load_data(key, isencrypted, path)
                        if kv is not None:
                            all_data[kv.key] = kv.value
                except Exception as e:
                    if __config__.show_logs:
                        cPrint("RED", f"Error loading online data: {e}")
            elif __config__.use_offline:
                if __config__.show_logs:
                    cPrint("YELLOW", "Network is offline, loading from offline backup.")
                for file in os.listdir(path):
                    if file.endswith(".octafile"):
                        key = file[:-len(".octafile")]
                        value = load_offline_file(os.path.join(path, file), key)
                        if value is not None:
                            all_data[key] = value
            return all_data

        if datatype == Object:
            return get_objects()
        elif datatype == KeyValue:
            return get_keyvalues()
        elif datatype == All:
            return {
                "objects": get_objects(),
                "keyvalues": get_keyvalues()
            }
        else:
            if __config__.show_logs:
                cPrint("RED", f"Invalid datatype specified: {datatype}")
            return {}