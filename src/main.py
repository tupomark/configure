import argparse
import base64
import binascii
import csv
import os
import shlex


VFS_NAME = "demo-vfs"
CURRENT_USER = "marksuvorov"

NO_ARGUMENTS = 0
ONE_ARGUMENT = 1
TWO_ARGUMENTS = 2
BASE64_PREFIX = "base64:"

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--vfs",
        required=True,
        help="Путь к CSV-файлу VFS"
    )

    parser.add_argument(
        "--script",
        required=False,
        help="Путь к стартовому скрипту"
    )

    return parser.parse_args()


def load_vfs(vfs_path):
    vfs = {}
    try:
        with open(vfs_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not valid_csv_row(row):
                    print("Ошибка: неправильный формат CSV.")
                    return None

                path = row["path"]
                item_type = row["type"]
                content = decode_content(row["content"])
                if content is None:
                    return None

                if item_type not in ("file", "directory"):
                    print("Ошибка: неправильный тип объекта VFS.")
                    return None

                vfs[path] = {
                    "type": item_type,
                    "content": content,
                    "owner": CURRENT_USER
                }

        if "/" not in vfs:
            print("Ошибка: VFS не содержит корневую директорию.")
            return None

        return vfs
    except FileNotFoundError:
        print("Ошибка: файл VFS не найден.")
        return None
    except (csv.Error, KeyError):
        print("Ошибка: неправильный формат CSV.")
        return None


def valid_csv_row(row):
    return (
        row.get("path") is not None
        and row.get("type") is not None
        and row.get("content") is not None
    )


def parse_command(line):
    return shlex.split(line)

def decode_content(content):
    if not content.startswith(BASE64_PREFIX):
        return content

    encoded_content = content[len(BASE64_PREFIX):]

    try:
        return base64.b64decode(encoded_content, validate=True)
    except (binascii.Error, ValueError):
        print("Ошибка: неправильные данные base64.")
        return None

def normalize_path(current_path, path):
    if path.startswith("/"):
        result = path
    elif current_path == "/":
        result = "/" + path
    else:
        result = current_path + "/" + path

    parts = []

    for part in result.split("/"):
        if part == "" or part == ".":
            continue

        if part == "..":
            if parts:
                parts.pop()
        else:
            parts.append(part)

    if not parts:
        return "/"

    return "/" + "/".join(parts)


def list_directory(vfs, current_path):
    prefix = current_path

    if prefix != "/":
        prefix += "/"

    found = []

    for path in vfs:
        if path == current_path:
            continue

        if not path.startswith(prefix):
            continue

        relative = path[len(prefix):]

        if "/" not in relative:
            found.append(relative)

    for name in found:
        print(name)


def change_directory(vfs, current_path, path):
    new_path = normalize_path(current_path, path)

    if new_path not in vfs:
        print("Ошибка: директория не найдена.")
        return current_path

    if vfs[new_path]["type"] != "directory":
        print("Ошибка: это не директория.")
        return current_path

    return new_path


def change_owner(vfs, current_path, owner, path):
    target_path = normalize_path(current_path, path)

    if target_path not in vfs:
        print("Ошибка: объект не найден.")
        return

    vfs[target_path]["owner"] = owner
    print(f"Владелец {target_path}: {owner}")


def copy_file(vfs, current_path, source, destination):
    source_path = normalize_path(current_path, source)
    destination_path = normalize_path(current_path, destination)

    if source_path not in vfs:
        print("Ошибка: исходный файл не найден.")
        return

    if vfs[source_path]["type"] != "file":
        print("Ошибка: копировать можно только файл.")
        return

    if destination_path in vfs:
        print("Ошибка: объект назначения уже существует.")
        return

    parent_path = os.path.dirname(destination_path)

    if parent_path == "":
        parent_path = "/"

    if parent_path not in vfs:
        print("Ошибка: директория назначения не найдена.")
        return

    if vfs[parent_path]["type"] != "directory":
        print("Ошибка: путь назначения содержит не директорию.")
        return

    vfs[destination_path] = {
        "type": "file",
        "content": vfs[source_path]["content"],
        "owner": vfs[source_path].get("owner", CURRENT_USER)
    }

    print(f"Файл скопирован: {destination_path}")


def execute_ls(arguments, vfs, current_path):
    if arguments:
        print("Ошибка: команда ls не принимает аргументы.")
        return current_path, True

    list_directory(vfs, current_path)
    return current_path, True


def execute_cd(arguments, vfs, current_path):
    if len(arguments) != ONE_ARGUMENT:
        print("Ошибка: команда cd требует один аргумент.")
        return current_path, True

    new_path = change_directory(
        vfs,
        current_path,
        arguments[0]
    )

    return new_path, True


def execute_whoami(arguments, current_path):
    if arguments:
        print("Ошибка: команда whoami не принимает аргументы.")
        return current_path, True

    print(CURRENT_USER)
    return current_path, True


def execute_echo(arguments, current_path):
    print(" ".join(arguments))
    return current_path, True


def execute_who(arguments, current_path):
    if arguments:
        print("Ошибка: команда who не принимает аргументы.")
        return current_path, True

    print(CURRENT_USER)
    return current_path, True


def execute_chown(arguments, vfs, current_path):
    if len(arguments) != TWO_ARGUMENTS:
        print("Ошибка: команда chown требует два аргумента.")
        return current_path, True

    change_owner(
        vfs,
        current_path,
        arguments[0],
        arguments[1]
    )

    return current_path, True


def execute_cp(arguments, vfs, current_path):
    if len(arguments) != TWO_ARGUMENTS:
        print("Ошибка: команда cp требует два аргумента.")
        return current_path, True

    copy_file(
        vfs,
        current_path,
        arguments[0],
        arguments[1]
    )

    return current_path, True


def execute_vfs_load(arguments, vfs, current_path):
    if len(arguments) != ONE_ARGUMENT:
        print("Ошибка: команда vfs-load требует один аргумент.")
        return current_path, True, vfs

    new_vfs = load_vfs(arguments[0])

    if new_vfs is None:
        return current_path, True, vfs

    print("VFS загружен:", arguments[0])
    return "/", True, new_vfs


def execute_command(parts, vfs, current_path):
    if not parts:
        return current_path, True, vfs

    command = parts[0]
    arguments = parts[1:]

    handlers = {
        "ls": lambda: execute_ls(arguments, vfs, current_path),
        "cd": lambda: execute_cd(arguments, vfs, current_path),
        "whoami": lambda: execute_whoami(arguments, current_path),
        "echo": lambda: execute_echo(arguments, current_path),
        "who": lambda: execute_who(arguments, current_path),
        "chown": lambda: execute_chown(arguments, vfs, current_path),
        "cp": lambda: execute_cp(arguments, vfs, current_path)
    }

    if command == "exit":
        return current_path, False, vfs
    if command == "vfs-load":
        return execute_vfs_load(arguments, vfs, current_path)

    if command not in handlers:
        print("Ошибка: неизвестная команда:", command)
        return current_path, True, vfs

    new_path, running = handlers[command]()
    return new_path, running, vfs


def run_script(script_path, vfs):
    current_path = "/"

    try:
        with open(script_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                print(
                    f"{VFS_NAME}:{current_path}> "
                    f"{line}"
                )

                try:
                    parts = parse_command(line)

                    current_path, running, vfs = execute_command(
                        parts,
                        vfs,
                        current_path
                    )

                    if not running:
                        break

                except ValueError:
                    print("Ошибка: неправильные кавычки.")

    except FileNotFoundError:
        print("Ошибка: стартовый скрипт не найден.")


def run_interactive(vfs):
    current_path = "/"

    while True:
        try:
            line = input(f"{VFS_NAME}:{current_path}> ")

            parts = parse_command(line)

            current_path, running, vfs = execute_command(
                parts,
                vfs,
                current_path
            )

            if not running:
                print("Выход из программы.")
                break

        except ValueError:
            print("Ошибка: неправильные кавычки.")


def main():
    args = parse_arguments()

    print("Путь к VFS:", args.vfs)
    print("Путь к скрипту:", args.script)

    vfs = load_vfs(args.vfs)

    if vfs is None:
        return

    print("VFS загружен:", args.vfs)

    if args.script:
        run_script(args.script, vfs)
        return

    run_interactive(vfs)


if __name__ == "__main__":
    main()