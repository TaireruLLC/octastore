# OctaStore 🚀

**Your GitHub repos as encrypted, offline-first databases — powered by Python magic.**

---

### Why OctaStore?

You love GitHub, you love Python, but managing data with traditional databases feels heavy and clunky.  
**OctaStore** flips the script: it treats GitHub repositories as your personal, encrypted data vaults — no database language required. Work offline, sync online, and keep your data safe.

---

### What’s under the hood?

- 🔐 Strong encryption with `cryptography`  
- 📦 Multi-repo support with repo fallback  
- 🔄 Offline-first sync — keep working without internet!  
- 🐍 Pythonic API made for developers (no SQL headaches)  
- 💾 Simple data save/load/delete, including complex objects  
- 🔧 Configurable paths & logging to fit your project’s needs

---

### Why does OctaStore look so familiar?

OctaStore is a rebraned version of our package `gitbase` ([gitbase v0.7.6](https://pypi.org/project/gitbase)) with a more unified engine.
GitBase used to share a name with another more popular product, and would, quite honestly, cause headaches, so we rebranded and upgraded the engine.

---

### What does the `-x` suffix mean in some version numbers?

When you see a version number with a suffix like `-x` (e.g., `v0.0.0-1`), it indicates a pre-release. The number after the dash (`-`) reflects the order of the pre-release—higher numbers represent later pre-releases. For example, `v0.0.0-1` is the first pre-release of version `v0.0.0`, while `v0.0.0-2` is the second. The version without a suffix (e.g., `v0.0.0`) is the official release, which comes after all its pre-releases.

Pre-releases are created when we aren't fully confident in calling a version final. Not every release will have pre-releases. Additionally, some pre-releases may reference or depend on software that has not yet been publicly released. In such cases, the required components will be made available as soon as possible, either shortly before or after the official release.

---

### What’s new in v0.3.2-2?
- Renamed `NotificationManager` to `LogManager` to make it eaiser to tell what it's for
- Updated example code to display how to initialize `octastore` (with `init`)
- Renamed `OctaCluster` to `OctaStore` and the old `OctaStore` to `OctaStoreLegacy`
- Fixed bugs in example code
- Added new `datatype` known as `All` which will allow for non-explicit selection of data in `get_all`
- Remade all `datatypes` into classes for type annotation support
- Renamed `DataStore` to `DataBase`
- Renamed `db` param of `DataBase` to `core` to better reflect that the `DataBase` class itself is the database

---

### Installation

```bash
pip install octastore
````

---

### Getting Started — Example Code

```python
# OctaStore v0.3.2-2 Showcase Example

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
# the path setup with `__config.setdatpath()` will add an `__config__.cleanpath` property which can be used for other application needs besides OctaStore, it will return a clean path based on your os (ex. Windows -> C:/Users/YourUsername/Documents/Taireru LLC/Cool RPG Game/)

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
