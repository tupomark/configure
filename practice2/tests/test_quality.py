"""Автоматическая проверка ограничений оформления ПР2."""

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINE_LIMIT = 80
FUNCTION_LIMIT = 40
ARGUMENT_LIMIT = 7
FILE_LIMIT = 1000
COMPLEXITY_LIMIT = 10
BRANCHES = (
    ast.If, ast.For, ast.While, ast.IfExp,
    ast.ExceptHandler, ast.comprehension,
)


def complexity(function):
    """Оценить ветвления, включая булевы операции и генераторы."""
    result = 1
    for node in ast.walk(function):
        if isinstance(node, BRANCHES):
            result += 1
        if isinstance(node, ast.BoolOp):
            result += len(node.values) - 1
    return result


class QualityTests(unittest.TestCase):
    """Проверить исходники, сценарии и тесты одной работы."""

    def test_source_limits(self):
        """Ограничить длины файлов, строк, функций и число аргументов."""
        paths = [p for folder in ("src", "scripts", "tests")
                 for p in (ROOT / folder).glob("*.py")]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertLessEqual(len(text.splitlines()), FILE_LIMIT)
                for line in text.splitlines():
                    self.assertLessEqual(len(line), LINE_LIMIT, path.name)
                self.check_functions(ast.parse(text), path)

    def check_functions(self, tree, path):
        """Проверить docstring и сложность каждого определения функции."""
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            with self.subTest(function=node.name, path=path.name):
                self.assertTrue(ast.get_docstring(node))
                length = node.end_lineno - node.lineno + 1
                self.assertLessEqual(length, FUNCTION_LIMIT)
                self.assertLessEqual(len(node.args.args), ARGUMENT_LIMIT)
                self.assertLessEqual(complexity(node), COMPLEXITY_LIMIT)
