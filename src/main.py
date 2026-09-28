import shlex
import argparse
import csv


VFS_NAME = "demo-vfs"


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
                if (
                    row.get("path") is None
                    or row.get("type") is None
                    or row.get("content") is None
                ):
                    print("Ошибка: неправильный формат CSV.")
                    return None

                path = row["path"]
                item_type = row["type"]
                content = row["content"]

                if item_type not in ("file", "directory"):
                    print("Ошибка: неправильный тип объекта VFS.")
                    return None

                vfs[path] = {
                    "type": item_type,
                    "content": content
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


def parse_command(line):
    return shlex.split(line)


def normalize_path(current_path, path):
    if path.startswith("/"):
        result = path
    else:
        if current_path == "/":
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


def execute_command(parts, vfs, current_path):
    if not parts:
        return current_path, True

    command = parts[0]
    arguments = parts[1:]

    if command == "exit":
        return current_path, False

    if command == "ls":
        if arguments:
            print("Ошибка: команда ls не принимает аргументы.")
            return current_path, True

        list_directory(vfs, current_path)
        return current_path, True

    if command == "cd":
        if len(arguments) != 1:
            print("Ошибка: команда cd требует один аргумент.")
            return current_path, True

        new_path = change_directory(
            vfs,
            current_path,
            arguments[0]
        )

        return new_path, True

    print("Ошибка: неизвестная команда:", command)
    return current_path, True


def run_script(script_path, vfs):
    current_path = "/"

    try:
        with open(script_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                print(f"{VFS_NAME}> {line}")

                try:
                    parts = parse_command(line)

                    current_path, running = execute_command(
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


def main():
    args = parse_arguments()

    vfs = load_vfs(args.vfs)

    if vfs is None:
        return

    print("VFS загружен:", args.vfs)

    if args.script:
        run_script(args.script, vfs)
        return

    current_path = "/"

    while True:
        try:
            line = input(f"{VFS_NAME}:{current_path}> ")

            parts = parse_command(line)

            current_path, running = execute_command(
                parts,
                vfs,
                current_path
            )

            if not running:
                print("Выход из программы.")
                break

        except ValueError:
            print("Ошибка: неправильные кавычки.")


if __name__ == "__main__":
    main()