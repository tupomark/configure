import shlex


VFS_NAME = "demo-vfs"


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