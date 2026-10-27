"""Рекурсивный DFS с глубиной, фильтрацией и сохранением циклов."""

from dataclasses import dataclass, field
from .versions import normalize

ROOT_DEPTH = 0


@dataclass
class Graph:
    """Хранить узлы (имя, версия) и ориентированные рёбра."""

    edges: dict = field(default_factory=dict)
    cycles: set = field(default_factory=set)


class GraphBuilder:
    """Строить граф с повторным раскрытием более короткого пути."""

    def __init__(self, repository, max_depth=3, exclude=None):
        """Запомнить источник, глубину и нечувствительный к регистру фильтр."""
        self.repository = repository
        self.max_depth = max_depth
        self.exclude = exclude.casefold() if exclude else None
        self.graph = Graph()
        self.best_depth = {}
        self.active = set()

    def build(self, name, version):
        """Начать DFS; корень находится на глубине 0."""
        if self._excluded(name):
            raise ValueError("Корневой пакет исключён фильтром --exclude")
        version = self.repository.resolve(name, f"[{version}]")
        root = (name.casefold(), normalize(version))
        self._visit(root, ROOT_DEPTH, name)
        return self.graph

    def _excluded(self, name):
        """Проверить вхождение подстроки в имя пакета."""
        return self.exclude is not None and self.exclude in name.casefold()

    def _visit(self, node, depth, source_name):
        """Раскрыть вершину, если найден меньший уровень глубины."""
        self.graph.edges.setdefault(node, set())
        if node in self.active:
            return
        previous = self.best_depth.get(node)
        if previous is not None and previous <= depth:
            return
        self.best_depth[node] = depth
        if depth >= self.max_depth:
            return
        self.active.add(node)
        dependencies = self.repository.dependencies(source_name, node[1])
        for name, requirement in dependencies:
            if self._excluded(name):
                continue
            version = self.repository.resolve(name, requirement)
            child = (name.casefold(), version)
            self.graph.edges[node].add(child)
            if child in self.active:
                self.graph.cycles.add((node, child))
            self._visit(child, depth + 1, name)
        self.active.remove(node)


def graph_lines(graph):
    """Показать рёбра и изолированные вершины в устойчивом порядке."""
    result = []
    for node, children in sorted(graph.edges.items()):
        source = f"{node[0]}@{node[1]}"
        if not children:
            result.append(source)
        for child in sorted(children):
            result.append(f"{source} -> {child[0]}@{child[1]}")
    return result
