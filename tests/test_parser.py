from src.main import parse_command


def test_simple_command():
    result = parse_command("ls")

    assert result == ["ls"]


def test_command_with_arguments():
    result = parse_command("ls -l file.txt")

    assert result == ["ls", "-l", "file.txt"]


def test_quoted_argument():
    result = parse_command('cd "hello world"')

    assert result == ["cd", "hello world"]