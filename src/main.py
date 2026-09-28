import shlex
import argparse


VFS_NAME = "demo-vfs"

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--vfs",
        required=True,
        help="Путь к физическому VFS"
    )

    parser.add_argument(
        "--script",
        required=False,
        help="Путь к стартовому скрипту"
    )

    return parser.parse_args()

def run_script(script_path):
    with open(script_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            print(f"{VFS_NAME}> {line}")

            try:
                parts = parse_command(line)
                execute_command(parts)
            except ValueError:
                print("Ошибка: неправильные кавычки.")

def parse_command(line):
    return shlex.split(line)


def execute_command(parts):
    if not parts:
        return

    command = parts[0]
    arguments = parts[1:]

    if command == "exit":
        return False

    if command == "ls":
        print("Команда:", command)
        print("Аргументы:", arguments)
        return True

    if command == "cd":
        print("Команда:", command)
        print("Аргументы:", arguments)
        return True

    print("Ошибка: неизвестная команда:", command)
    return True


def main():
    args = parse_arguments()

    print("Путь к VFS:", args.vfs)
    print("Путь к скрипту:", args.script)

    if args.script:
        run_script(args.script)
        return

    while True:
        try:
            line = input(f"{VFS_NAME}> ")
            parts = parse_command(line)

            result = execute_command(parts)

            if result is False:
                print("Выход из программы.")
                break

        except ValueError:
            print("Ошибка: неправильные кавычки.")


if __name__ == "__main__":
    main()