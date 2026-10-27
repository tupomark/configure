"""Проверки D2 и ошибок рендерера."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.graph import Graph
from src.visualize import render_graph, to_d2


class VisualizeTests(unittest.TestCase):
    """Проверить текст диаграммы и сохранение при ошибке."""

    def test_deterministic_d2(self):
        """Подписи и рёбра не зависят от порядка словаря."""
        a, b = ("a", "1.0.0"), ("b", "2.0.0")
        graph = Graph({b: set(), a: {b}})
        self.assertEqual(to_d2(graph),
                         'direction: right\nn0: "a@1.0.0"\n'
                         'n1: "b@2.0.0"\nn0 -> n1\n')

    def test_renderer_missing(self):
        """Не терять D2, если внешняя программа недоступна."""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "graph.png"
            with patch("src.visualize.shutil.which", return_value=None):
                with self.assertRaises(ValueError):
                    render_graph(Graph({("a", "1"): set()}), output)
            self.assertTrue(output.with_suffix(".d2").is_file())
