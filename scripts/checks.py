"""Общие средства локальных проверок этапов."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUCCESS = 0
CLI_TIMEOUT = 150


def run_cli(stage, arguments, expected_code=SUCCESS):
    """Запустить настоящий CLI и проверить код завершения."""
    command = [sys.executable, "-m", "src.main", "--stage", str(stage)]
    command.extend(str(item) for item in arguments)
    print("$", " ".join(command), flush=True)
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True,
        timeout=CLI_TIMEOUT,
    )
    print(result.stdout, end="", flush=True)
    print(result.stderr, end="", flush=True)
    if result.returncode != expected_code:
        raise AssertionError(
            f"Код {result.returncode}; ожидался {expected_code}"
        )
    return result.stdout


def expect_lines(output, expected):
    """Проверить точный набор строк, включая отсутствие лишних данных."""
    actual = set(output.splitlines())
    if actual != set(expected):
        raise AssertionError(f"Получено {actual}; ожидалось {set(expected)}")


def run_checks(number, pattern, demonstrate):
    """Выполнить тесты одного этапа и его сценарий демонстрации."""
    print(f"Этап {number}: локальная проверка", flush=True)
    suite = unittest.defaultTestLoader.discover(
        str(ROOT / "tests"), pattern=pattern,
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    demonstrate()
    print(f"PASS: этап {number}", flush=True)


def local_arguments(example="cycle", package="A", *extra):
    """Собрать настройки CLI для тестового JSON-репозитория."""
    return [
        "--package", package, "--version", "1", "--test-repo",
        "--repository", ROOT / "examples" / f"{example}.json", *extra,
    ]


def expect_graph(output, edges=(), leaves=()):
    """Сверить точные рёбра и листья демонстрационного графа версии 1."""
    expected = {
        f"{source}@1.0.0 -> {target}@1.0.0" for source, target in edges
    }
    expected.update(f"{name}@1.0.0" for name in leaves)
    actual = {line for line in output.splitlines() if "@" in line}
    if actual != expected:
        raise AssertionError(f"Граф {actual}; ожидался {expected}")
