"""Этап 1: конфигурация и ошибки всех обязательных настроек."""

from .checks import local_arguments, run_checks, run_cli

STAGE = 1
ARGUMENT_ERROR = 2
KEYS = {
    "package", "version", "repository", "test_repo", "output",
    "max_depth", "exclude", "stage", "reverse", "framework",
}
INVALID_OPTIONS = [
    ["--package", "bad/name"], ["--version", "[1]"],
    ["--repository", "missing.json"], ["--test-repo", "yes"],
    ["--output", "graph.svg"], ["--max-depth", "-1"],
    ["--max-depth", "many"], ["--exclude", ""],
]


def demonstrate():
    """Показать все ключи и отдельную ошибку каждой настройки."""
    arguments = local_arguments()
    output = run_cli(STAGE, arguments)
    keys = {line.split("=", 1)[0] for line in output.splitlines()}
    if keys != KEYS:
        raise AssertionError(f"Неверный список параметров: {keys}")
    for options in INVALID_OPTIONS:
        run_cli(STAGE, arguments + options, ARGUMENT_ERROR)
    run_cli(STAGE, ["--package", "A"], ARGUMENT_ERROR)


if __name__ == "__main__":
    run_checks(STAGE, "test_config.py", demonstrate)
