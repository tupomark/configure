"""Проверки обратного обхода."""

import unittest
from pathlib import Path
from src.reverse import reverse_graph, test_universe
from src.test_repository import TestRepository

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class ReverseTests(unittest.TestCase):
    """Проверить потребителей в разных компонентах графа."""

    def setUp(self):
        """Загрузить цикл с отдельным потребителем D."""
        self.graph = test_universe(
            TestRepository(EXAMPLES / "cycle.json"), 10, None,
        )

    def test_disconnected_consumer(self):
        """Найти A, C и D, зависящие от B."""
        result = reverse_graph(self.graph, "B", 10)
        self.assertEqual({n[0] for n in result.edges}, {"a", "b", "c", "d"})

    def test_no_consumers(self):
        """Не приписывать E чужие зависимости."""
        self.assertEqual(len(reverse_graph(self.graph, "E", 10).edges), 1)

    def test_depth_one(self):
        """Оставить только прямых потребителей B."""
        result = reverse_graph(self.graph, "B", 1)
        self.assertEqual({n[0] for n in result.edges}, {"a", "b", "d"})

    def test_unknown_target(self):
        """Сообщить об отсутствии пакета."""
        with self.assertRaises(ValueError):
            reverse_graph(self.graph, "Z", 10)
