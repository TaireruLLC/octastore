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
GitBase used to sshare a name with another more popular product, and would, quite honestly, cause headaches, so we rebranded and upgraded the engine.

---

### What does the `-x` suffix mean in some version numbers?

When you see a version number with a suffix like `-x` (e.g., `v0.0.0-1` or `v0.0.0`), it indicates a pre-release. The number after the dash (`-`) reflects the order of the pre-release—higher numbers represent later pre-releases. For example, `v0.0.0-1` is the first pre-release of version `v0.0.0`, while `v0.0.0-2` is the second. The version without a suffix (e.g., `v0.0.0`) is the official release, which comes after all its pre-releases.

Pre-releases are created when we aren't fully confident in calling a version final and are never released on PyPi. Not every release will have pre-releases. Additionally, some pre-releases may reference or depend on software that has not yet been publicly released. In such cases, the required components will be made available as soon as possible, either shortly before or after the official release.

---

### What’s new in v0.3.6?

- CLI support

---

### Installation

```bash
pip install octastore
````

---

### Getting Started — Example Code

```python
# OctaStore v0.3.6 Showcase Example

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
db.save_object(
    objectname="john_doe",
    objectinstance=player,
    isencrypted=True,
    attributes=["username", "score", "password"],
    path="players"
)

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
if db.get_all(isencrypted=False, datatype=Object, path="players"):
    if player.password == input("Enter your password: "):
        print("Login successful!")
        load_game()
    else:
        print("Incorrect password!")
        main_menu()

# -------------------------
# Save & Load General Data with Encryption
# -------------------------
db.save_data(key="key_name", value=69, path="data", isencrypted=True)

loaded_key_value = db.load_data(key="key_name", path="data", isencrypted=True)
print(f"Key: {loaded_key_value.key}, Value: {loaded_key_value.value}")

print("All stored data:", db.get_all(isencrypted=True, datatype=KeyValue, path="data"))

db.delete_data(key="key_name", path="data")

# -------------------------
# Player Account Management
# -------------------------
print("All data:", db.get_all(isencrypted=True, datatype=All, path="players"))

LogManager.hide()
db.delete_object(objectname="john_doe")
LogManager.show()
```

---

### 🔧 OctaStore CLI (Command-Line Interface)

OctaStore comes with a powerful CLI tool to help you interact with your data directly from the terminal — no Python scripting required.

#### ✅ Setup

If you've installed OctaStore as a module in a project, you can expose the CLI like so:

```bash
octastore --help
```

> Or alias it inside a shell script for convenience.

---

#### 🚀 Basic Usage

Every CLI command requires authentication info:

```bash
--tokens YOUR_TOKEN --owners YOUR_USERNAME --repos YOUR_REPO
```

For cluster mode (multi-repo):

```bash
--cluster --tokens TOKEN1 TOKEN2 --owners OWNER1 OWNER2 --repos REPO1 REPO2
```

---

#### 📦 Commands Overview

| Command            | Description                                    |
| ------------------ | ---------------------------------------------- |
| `init`             | Initialize the OctaStore system                |
| `is-online`        | Check GitHub connectivity                      |
| `config get/set`   | Read/write internal config flags               |
| `log show/hide`    | Toggle verbose logs                            |
| `octafile`         | Stream, play audio, or play video from repo    |
| `upload-file`      | Upload a file to the GitHub repo               |
| `download-file`    | Download a file from the repo to your machine  |
| `save-kv`          | Save a key-value pair                          |
| `load-kv`          | Load a key-value pair                          |
| `delete-kv`        | Delete a key-value pair                        |
| `save-object`      | Save a class/object by attributes              |
| `load-object`      | Load a saved object into memory                |
| `delete-object`    | Delete a stored object                         |
| `list-all`         | List stored keys/objects                       |
| `get-all`          | Retrieve and print all stored data             |
| `generate-example` | Save an example code file to `example_code.py` |

---

#### 🔐 Encryption & Keys

You can enable encryption and pass a Fernet key:

```bash
--encrypted --keyfile path/to/key.key
```

If `--keyfile` is omitted, a new encryption key is generated.

---

#### 📁 Example

```bash
octastore save-kv \
  --tokens ghp_XXXX --owners user --repos repo \
  --key "level" --value "5" --encrypted
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
