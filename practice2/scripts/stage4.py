"""Этап 4: прямые и транзитивные потребители выбранного пакета."""

from .checks import expect_graph, local_arguments, run_checks, run_cli

STAGE = 4
CASES = [
    ("B", ["--max-depth", "1"], [("b", "a"), ("b", "d")], ["a", "d"]),
    ("B", ["--max-depth", "10"],
     [("a", "c"), ("b", "a"), ("b", "d"), ("c", "b")], ["d"]),
    ("E", [], [], ["e"]),
    ("B", ["--max-depth", "10", "--exclude", "D"],
     [("a", "c"), ("b", "a"), ("c", "b")], []),
]


def demonstrate():
    """Найти отдельного потребителя D, пустой результат и цикл."""
    for package, options, edges, leaves in CASES:
        output = run_cli(STAGE, local_arguments("cycle", package, *options))
        expect_graph(output, edges, leaves)
    run_cli(STAGE, local_arguments("cycle", "Z"), 1)


if __name__ == "__main__":
    run_checks(STAGE, "test_reverse.py", demonstrate)
