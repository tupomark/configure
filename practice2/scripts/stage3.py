"""Этап 3: DFS, глубина, фильтр, цикл и выбор версии."""

from .checks import expect_graph, local_arguments, run_checks, run_cli

STAGE = 3
CASES = [
    ("diamond", ["--max-depth", "0"], [], ["a"]),
    ("diamond", ["--max-depth", "1"], [("a", "b"), ("a", "d")],
     ["b", "d"]),
    ("diamond", ["--max-depth", "3"],
     [("a", "b"), ("a", "d"), ("b", "c"), ("c", "d"), ("d", "e")],
     ["e"]),
    ("diamond", ["--exclude", "d"], [("a", "b"), ("b", "c")], ["c"]),
    ("cycle", ["--max-depth", "10"],
     [("a", "b"), ("b", "c"), ("c", "a")], []),
    ("versions", [], [("a", "b")], ["b"]),
]


def demonstrate():
    """Проверить реальные запуски CLI на разных локальных графах."""
    for example, options, edges, leaves in CASES:
        output = run_cli(STAGE, local_arguments(example, "A", *options))
        expect_graph(output, edges, leaves)
    run_cli(STAGE, local_arguments("cycle", "A", "--exclude", "A"), 1)


if __name__ == "__main__":
    run_checks(STAGE, "test_graph.py", demonstrate)
