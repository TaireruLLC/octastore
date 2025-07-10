# OctaStore v0.3.4 Showcase Example

from octastore import init, __config__, OctaStore, DataBase, All, Object, KeyValue, LogManager; init()
from cryptography.fernet import Fernet
import sys

# -------------------------
# OctaStore Core Setup
# -------------------------
encryption_key = Fernet.generate_key()  # Generate encryption key for secure storage

# OctaStore setup
core = OctaStore([
    {
        "token": "YOUR_GITHUB_TOKEN",
        "repo_owner": "YOUR_GITHUB_USERNAME",
        "repo_name": "YOUR_REPO_NAME",
        "branch": "main"
    },
    # Additional OctaStore configurations can be added here
    # {"token": "SECOND_TOKEN", "repo_owner": "SECOND_USERNAME", "repo_name": "SECOND_REPO", "branch": "main"}
])
# When using Legacy OctaStore do the below instead (will be a single repository)
# from octastore import OctaStoreLegacy
# core = OctaStoreLegacy(token=GITHUB_TOKEN, repo_owner=REPO_OWNER, repo_name=REPO_NAME)

# -------------------------
# Configure OctaStore
# -------------------------

__config__.app_name = "Cool RPG Game"
__config__.publisher = "Taireru LLC"
__config__.version = "0.1.0"
__config__.use_offline = True # defaults to `True`, no need to type out unless you want to set it to `False`
__config__.show_logs = True # defaults to `True`, no need to type out unless you want to set it to `False`
__config__.use_version_path = False # defaults to `True`, this variable will decide if your app path will use a version subdirectory (meaning different versions will have different data)
__config__.setdatpath() # Update `datpath` variable of `__config__` for offline data saving (you can also set it manually via `__config__.datpath = 'path/to/data'`)
# the path setup with `__config.setdatpath()` will add an `__config__.cleanpath` property which can be used for other application needs besides OctaStore, it will return a clean path based on your os (ex. Windows -> C:/Users/YourUsername/AppData/LocalLow/Taireru LLC/Cool RPG Game/)

# -------------------------
# System Initialization
# -------------------------
db = DataBase(core=core, encryption_key=encryption_key)

# -------------------------
# Player Class Definition
# -------------------------
class Player:
    def __init__(self, username, score, password):
        self.username = username
        self.score = score
        self.password = password

# Create a sample player instance
player = Player(username="john_doe", score=100, password="123")

# -------------------------
# Save & Load Player Data with Encryption
# -------------------------
# Save player data to the repository
db.save_object(
    objectname="john_doe",
    objectinstance=player,
    isencrypted=True,
    attributes=["username", "score", "password"],
    path="players"
)

# Load player data
db.load_object(objectname="john_doe", objectinstance=player, isencrypted=True)

# -------------------------
# Game Flow Functions
# -------------------------
def load_game():
    print("Game starting...")

def main_menu():
    sys.exit("Exiting game...")

# -------------------------
# Account Validation & Login
# -------------------------
# Validate player credentials
if db.get_all(isencrypted=False, datatype=Object, path="players"): # datatype can be All, Object or KeyValue, but defaults to All.
    if player.password == input("Enter your password: "):
        print("Login successful!")
        load_game()
    else:
        print("Incorrect password!")
        main_menu()

# -------------------------
# Save & Load General Data with Encryption
# -------------------------
# Save data (key-value) to the repository (with encryption)
db.save_data(key="key_name", value=69, path="data", isencrypted=True)

# Load and display specific key-value pair
loaded_key_value = db.load_data(key="key_name", path="data", isencrypted=True)
print(f"Key: {loaded_key_value.key}, Value: {loaded_key_value.value}")

# Display all stored data
print("All stored data:", db.get_all(isencrypted=True, datatype=KeyValue, path="data"))

# Delete specific key-value data
db.delete_data(key="key_name", path="data")

# -------------------------
# Player Account Management
# -------------------------
# Display all data
print("All data:", db.get_all(isencrypted=True, datatype=All, path="players"))

# Delete a specific player account
LogManager.hide()  # Hide logs temporarily
db.delete_object(objectname="john_doe")
LogManager.show()  # Show logs again