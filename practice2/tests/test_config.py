"""Проверки настроек первого этапа."""

import contextlib
import io
import unittest

from src.config import parse_arguments

BASE = ["--package", "Example", "--version", "1.0.0"]


class ConfigTests(unittest.TestCase):
    """Проверить нормальный запуск и ошибки каждой настройки."""

    def test_defaults(self):
        """Прочитать пакет и значения по умолчанию."""
        args = parse_arguments(BASE)
        self.assertEqual(args.package, "Example")
        self.assertEqual(args.max_depth, 3)

    def test_invalid_parameters(self):
        """Отвергнуть все классы некорректных аргументов."""
        cases = [
            ["--package", "bad/name"], ["--version", "[1.0]"],
            ["--repository", "ftp://host"], ["--test-repo"],
            ["--output", "graph.svg"], ["--max-depth", "-1"],
            ["--max-depth", "101"], ["--max-depth", "many"],
            ["--exclude", ""], ["--test-repo", "yes"],
        ]
        for case in cases:
            with self.subTest(case=case), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    parse_arguments(BASE + case)
                self.assertEqual(result.exception.code, 2)
