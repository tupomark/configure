"""Проверки DFS, ромба, циклов, фильтров и версий."""

import unittest
from pathlib import Path

from src.graph import GraphBuilder
from src.test_repository import TestRepository

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def build(example, depth=10, exclude=None):
    """Построить граф примера из корня A."""
    repo = TestRepository(EXAMPLES / f"{example}.json")
    return GraphBuilder(repo, depth, exclude).build("A", "1")


class GraphTests(unittest.TestCase):
    """Проверить ожидаемые множества вершин и рёбер."""

    def test_depth_zero(self):
        """На глубине 0 оставить только корень."""
        self.assertEqual(build("diamond", 0).edges, {("a", "1.0.0"): set()})

    def test_depth_one(self):
        """На глубине 1 не раскрывать непосредственных соседей."""
        graph = build("diamond", 1)
        self.assertEqual(len(graph.edges), 3)
        self.assertFalse(graph.edges[("d", "1.0.0")])

    def test_shorter_path_reopens_node(self):
        """После A-B-C-D раскрыть D снова по короткому пути A-D."""
        graph = build("diamond", 3)
        self.assertIn(("e", "1.0.0"), graph.edges[("d", "1.0.0")])

    def test_cycle(self):
        """Сохранить замыкающее ребро и остановить рекурсию."""
        graph = build("cycle")
        self.assertEqual(len(graph.edges), 3)
        self.assertIn(("a", "1.0.0"), graph.edges[("c", "1.0.0")])
        self.assertTrue(graph.cycles)

    def test_filter(self):
        """Не посещать исключённый пакет и его ветку."""
        graph = build("diamond", exclude="d")
        self.assertEqual({node[0] for node in graph.edges}, {"a", "b", "c"})
        with self.assertRaises(ValueError):
            build("cycle", exclude="A")

    def test_range_chooses_lowest(self):
        """Выбор версии должен влиять на реально посещённые узлы."""
        graph = build("versions")
        self.assertEqual(set(graph.edges), {("a", "1.0.0"), ("b", "1.0.0")})

    def test_unknown_version(self):
        """Сообщить о неизвестной версии корня."""
        repo = TestRepository(EXAMPLES / "cycle.json")
        with self.assertRaises(ValueError):
            GraphBuilder(repo).build("A", "99")
