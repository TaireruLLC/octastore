
# OctaStore 🚀

**Your GitHub repos as encrypted, offline-first databases — powered by Python magic.**

---

### Why OctaStore?

You love GitHub, you love Python, but managing data with traditional databases feels heavy and clunky.  
**OctaStore** flips the script: it treats GitHub repositories as your personal, encrypted data vaults — no database language required. Work offline, sync online, and keep your data safe.

---

### What’s under the hood?

- 🔐 Strong encryption with `cryptography`  
- 📦 Multi-repo support with **OctaCluster** fallback  
- 🔄 Offline-first sync — keep working without internet!  
- 🐍 Pythonic API made for developers (no SQL headaches)  
- 💾 Simple data save/load/delete, including complex objects  
- 🔧 Configurable paths & logging to fit your project’s needs

---

### Installation

```bash
pip install octastore
````

---

### Getting Started — Example Code

```python
# OctaStore v0.2.0 Showcase Example

from octastore import OctaCluster, DataStore, OctaFile, NotificationManager, __config__
from cryptography.fernet import Fernet
import sys

# -------------------------
# GitHub Database Setup
# -------------------------
encryption_key = Fernet.generate_key()  # Generate encryption key for secure storage

# OctaCluster setup with fallback repository configurations (if needed)
database = OctaCluster([
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
# from octastore import OctaStore
# database = OctaStore(token=GITHUB_TOKEN, repo_owner=REPO_OWNER, repo_name=REPO_NAME)

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
# the path setup with `__config__.cleanpath` property can be used for other application needs besides OctaStore, it will return a clean path based on your os (ex. Windows -> C:/Users/YourUsername/Documents/Taireru LLC/Cool RPG Game/)

# -------------------------
# System Instantiation
# -------------------------
ds = DataStore(db=database, encryption_key=encryption_key)

# -------------------------
# Player Class Definition
# -------------------------
class Player:
    def __init__(self, username, score, password):
        self.username = username
        self.score = score
        self.password = password

# Create a sample player instance
player = Player(objectname="john_doe", score=100, password="123")

# -------------------------
# Save & Load Player Data with Encryption
# -------------------------
# Save player data to the repository (with encryption)
ds.save_object(
    objectname="john_doe",
    objectinstance=player,
    isencrypted=True,
    attributes=["username", "score", "password"],
    path="players"
)

# Load player data
ds.load_object(objectname="john_doe", objectinstance=player, isencrypted=True)

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
if ds.get_all(path="players"):
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
ds.save_data(key="key_name", value=69, path="data", isencrypted=True)

# Load and display specific key-value pair
loaded_key_value = ds.load_data(key="key_name", path="data", isencrypted=True)
print(f"Key: {loaded_key_value.key}, Value: {loaded_key_value.value}")

# Display all stored data
print("All stored data:", ds.get_all(isencrypted=True, path="data"))

# Delete specific key-value data
ds.delete_data(key="key_name", path="data")

# -------------------------
# Player Account Management
# -------------------------
# Display all player accounts
print("All player accounts:", ds.get_all(path="players"))

# Delete a specific player account
NotificationManager.hide()  # Hide notifications temporarily
ds.delete_object(objectname="john_doe")
NotificationManager.show()  # Show notifications again
```

---

### What’s Next?

* Build your apps without wrangling SQL or external DB servers.
* Enjoy auto-sync between offline work and GitHub once you’re back online.
* Protect sensitive data with industry-grade encryption by default.

---

### OctaStore Web: Your Data, In Your Browser

OctaStore Web extends OctaStore by giving you a sleek web dashboard to browse and manage your data — no Python required.

**Heads up:**

* Use a private GitHub repo
* Host the dashboard on platforms like [Vercel](https://vercel.com)

Discover more at: [OctaStore Web](https://tairerullc.vercel.app/products/extensions/octastore-web)

---

### Useful Links

* PyPI Package: [octastore](https://pypi.org/project/octastore)
* Official Website: [tairerullc.com](https://tairerullc.com)

---

### Need Help? Got Questions?

Reach out at **[tairerullc@gmail.com](mailto:tairerullc@gmail.com)** — We’d love to hear from you!

---

*Built with ❤️ by Taireru LLC — turning GitHub into your personal database playground.*
