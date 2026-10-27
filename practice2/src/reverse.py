"""Обратные зависимости через рекурсивный DFS предыдущего этапа."""

from .graph import Graph, GraphBuilder


class ReversedRepository:
    """Адаптер обращённого графа к интерфейсу репозитория."""

    def __init__(self, graph):
        """Заменить каждое ребро A → B на B → A."""
        self.edges = {node: set() for node in graph.edges}
        for source, children in graph.edges.items():
            for child in children:
                self.edges.setdefault(child, set()).add(source)

    def dependencies(self, name, version):
        """Вернуть потребителей с точными версиями."""
        return [(item[0], f"[{item[1]}]") for item in
                sorted(self.edges[(name.casefold(), version)])]

    def resolve(self, name, requirement):
        """Прочитать уже известную версию."""
        return requirement[1:-1]


def merge_graphs(graphs):
    """Объединить результаты без потери общих рёбер."""
    result = Graph()
    for graph in graphs:
        for node, children in graph.edges.items():
            result.edges.setdefault(node, set()).update(children)
        result.cycles.update(graph.cycles)
    return result


def test_universe(repository, max_depth, exclude):
    """Проверить все компоненты и версии локального репозитория."""
    graphs = []
    for name, versions in repository.packages.items():
        if exclude and exclude.casefold() in name.casefold():
            continue
        for version in versions:
            builder = GraphBuilder(repository, max_depth, exclude)
            graphs.append(builder.build(name, version))
    return merge_graphs(graphs)


def reverse_graph(graph, name, max_depth, version=None):
    """Выполнить DFS по обращённому графу из заданного пакета."""
    targets = [node for node in graph.edges if node[0] == name.casefold()
               and (version is None or node[1] == version)]
    if not targets:
        raise ValueError(f"Пакет {name} не найден в области анализа")
    repository = ReversedRepository(graph)
    return merge_graphs([
        GraphBuilder(repository, max_depth).build(*node) for node in targets
    ])
