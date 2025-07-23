import argparse
import sys
import os
import json
from cryptography.fernet import Fernet
from . import (
    init, is_online, hasdataloaded, __config__,
    OctaStore, OctaStoreLegacy, DataBase,
    KeyValue, Object, All,
    LogManager, OctaFile
)
from altcolor import colored_text, reset, init; init(show_credits=False)

def log(msg, level="INFO"):
    colors = {
        "INFO": "GREEN",
        "WARN": "YELLOW",
        "ERROR": "RED",
        "DEBUG": "CYAN"
    }
    prefix = {
        "INFO": "[+]",
        "WARN": "[!]",
        "ERROR": "[x]",
        "DEBUG": "[*]"
    }
    color = colors.get(level.upper(), "WHITE")
    print(colored_text(color, f"{prefix.get(level.upper(), '[ ]')} {msg}") + reset())

def confirm_action(prompt):
    response = input(colored_text("YELLOW", f"{prompt} [y/N]: ") + reset()).strip().lower()
    return response in ("y", "yes")

def confirm_action(prompt):
    response = input(f"{prompt} [y/N]: ").strip().lower()
    return response in ("y", "yes")

def load_key(keyfile):
    if not os.path.exists(keyfile):
        raise FileNotFoundError(f"Key file not found: {keyfile}")
    with open(keyfile, "rb") as f:
        return f.read()

def get_octastore(args):
    if args.cluster:
        configs = []
        for token, owner, repo in zip(args.tokens, args.owners, args.repos):
            configs.append({
                "token": token,
                "repo_owner": owner,
                "repo_name": repo,
                "branch": args.branch
            })
        return OctaStore(configs)
    return OctaStoreLegacy(
        token=args.tokens[0],
        repo_owner=args.owners[0],
        repo_name=args.repos[0],
        branch=args.branch
    )

def get_db(args):
    init()
    __config__.use_offline = args.offline
    __config__.show_logs = args.verbose
    __config__.setdatpath()
    encryption_key = load_key(args.keyfile) if args.keyfile else Fernet.generate_key()
    return DataBase(core=get_octastore(args), encryption_key=encryption_key)

def main():
    parser = argparse.ArgumentParser(description="OctaStore CLI - OctaStore is a custom database system built with Python and powered by GitHub, treating GitHub repositories as databases. It features encryption using the cryptography library, ensuring data security.")
    parser.add_argument('--cluster', action='store_true')
    parser.add_argument('--tokens', nargs='+', required=True)
    parser.add_argument('--owners', nargs='+', required=True)
    parser.add_argument('--repos', nargs='+', required=True)
    parser.add_argument('--branch', default="main")
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--encrypted', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--keyfile', help="Path to Fernet key file")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")
    subparsers.add_parser("is-online")

    config_cmd = subparsers.add_parser("config")
    config_cmd.add_argument("action", choices=["get", "set"])
    config_cmd.add_argument("--key", required=True)
    config_cmd.add_argument("--value")

    log_cmd = subparsers.add_parser("log")
    log_cmd.add_argument("action", choices=["show", "hide"])

    of = subparsers.add_parser("octafile")
    of.add_argument("action", choices=["stream", "play-audio", "play-video"])
    of.add_argument("--path", required=True)

    up = subparsers.add_parser("upload-file")
    up.add_argument("--file", required=True)
    up.add_argument("--remote", required=True)

    dl = subparsers.add_parser("download-file")
    dl.add_argument("--remote", required=True)
    dl.add_argument("--file", required=True)

    subparsers.add_parser("generate-example")

    save_kv = subparsers.add_parser("save-kv")
    save_kv.add_argument("--key", required=True)
    save_kv.add_argument("--value", required=True)
    save_kv.add_argument("--path", default="data")

    load_kv = subparsers.add_parser("load-kv")
    load_kv.add_argument("--key", required=True)
    load_kv.add_argument("--path", default="data")

    delete_kv = subparsers.add_parser("delete-kv")
    delete_kv.add_argument("--key", required=True)
    delete_kv.add_argument("--path", default="data")
    delete_kv.add_argument("--local", action='store_true')

    save_obj = subparsers.add_parser("save-object")
    save_obj.add_argument("--name", required=True)
    save_obj.add_argument("--attr", nargs='+', required=True)
    save_obj.add_argument("--path", default="objects")

    load_obj = subparsers.add_parser("load-object")
    load_obj.add_argument("--name", required=True)

    delete_obj = subparsers.add_parser("delete-object")
    delete_obj.add_argument("--name", required=True)
    delete_obj.add_argument("--local", action='store_true')

    list_all = subparsers.add_parser("list-all")
    list_all.add_argument("--datatype", choices=["all", "object", "keyvalue"], default="all")
    list_all.add_argument("--path", default="data")
    list_all.add_argument("--json", action="store_true")
    
    get_all = subparsers.add_parser("get-all")
    get_all.add_argument("--datatype", choices=["all", "object", "keyvalue"], default="all")
    get_all.add_argument("--path", default="data")
    get_all.add_argument("--json", action="store_true")
    get_all.add_argument("--encrypted", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "init":
        init()
        log("Initialized.")

    elif args.command == "is-online":
        log("Online!" if is_online() else "Offline.")

    elif args.command == "config":
        if args.action == "get":
            val = getattr(__config__, args.key, None)
            log(f"{args.key} = {val}")
        else:
            setattr(__config__, args.key, args.value)
            log(f"Set {args.key} = {args.value}")

    elif args.command == "log":
        LogManager.show() if args.action == "show" else LogManager.hide()
        log("Logs shown" if args.action == "show" else "Logs hidden")

    elif args.command == "octafile":
        ofile = OctaFile(
            repo_owner=args.owners[0],
            repo_name=args.repos[0],
            token=args.tokens[0],
            branch=args.branch
        )
        if args.action == "stream":
            stream = ofile.get_file(args.path)
            print(stream.read().decode('utf-8', errors='ignore'))
        elif args.action == "play-audio":
            ofile.play_audio(args.path)
        elif args.action == "play-video":
            ofile.play_video(args.path)

    elif args.command == "upload-file":
        if not os.path.exists(args.file):
            log(f"File not found: {args.file}", "ERROR")
            return
        get_octastore(args).upload_file(args.file, args.remote)
        log(f"Uploaded {args.file} to {args.remote}")

    elif args.command == "download-file":
        if os.path.exists(args.file):
            if not confirm_action(f"Local file '{args.file}' exists. Overwrite?"):
                log("Download cancelled.")
                return
        get_octastore(args).download_file(args.remote, args.file)
        log(f"Downloaded {args.remote} to {args.file}")

    elif args.command == "generate-example":
        OctaStoreLegacy.generate_example()
        log("Example generated to example_code.py")

    else:
        db = get_db(args)
        if args.command == "save-kv":
            db.save_data(args.key, args.value, path=args.path, isencrypted=args.encrypted)
            log(f"Saved key: {args.key}")
        elif args.command == "load-kv":
            kv = db.load_data(args.key, isencrypted=args.encrypted, path=args.path)
            log(f"{kv.key} => {kv.value}" if kv else "Key not found.")
        elif args.command == "delete-kv":
            if confirm_action(f"Are you sure you want to delete key: {args.key}?"):
                db.delete_data(args.key, path=args.path, deleteoffline=args.local)
                log(f"Deleted key: {args.key}", "WARN")
            else:
                log("Delete cancelled.")
        elif args.command == "save-object":
            class Temp: pass
            temp = Temp()
            for attr in args.attr:
                val = input(f"{attr}: ")
                setattr(temp, attr, val)
            db.save_object(args.name, temp, isencrypted=args.encrypted, attributes=args.attr, path=args.path)
            log(f"Object '{args.name}' saved.")
        elif args.command == "load-object":
            class Temp: pass
            temp = Temp()
            db.load_object(args.name, temp, isencrypted=args.encrypted)
            log(f"Loaded object '{args.name}':")
            for k, v in temp.__dict__.items():
                log(f"  {k}: {v}")
        elif args.command == "delete-object":
            if confirm_action(f"Are you sure you want to delete object: {args.name}?"):
                db.delete_object(args.name, deletelocalfile=args.local)
                log(f"Deleted object: {args.name}", "WARN")
            else:
                log("Delete cancelled.")
        elif args.command == "list-all":
            dtype = {"all": All, "object": Object, "keyvalue": KeyValue}[args.datatype]
            res = db.get_all(isencrypted=args.encrypted, datatype=dtype, path=args.path)
            print(json.dumps(res, indent=2) if args.json else res if res else "[empty]")
        elif args.command == "get-all":
            dtype = {"all": All, "object": Object, "keyvalue": KeyValue}[args.datatype]
            res = db.get_all(isencrypted=args.encrypted, datatype=dtype, path=args.path)
            print(json.dumps(res, indent=2) if args.json else res if res else "[empty]")

if __name__ == "__main__":
    main()