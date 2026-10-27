"""Точка входа CLI с режимами демонстрации этапов."""

import sys
import subprocess
from xml.etree.ElementTree import ParseError

from .config import parse_arguments
from .graph import GraphBuilder, graph_lines
from .nuget import NugetRepository
from .test_repository import TestRepository
from .reverse import reverse_graph, test_universe
from .versions import normalize
from .visualize import render_graph


def execute(args):
    """Выполнить выбранный этап после проверки конфигурации."""
    if args.stage == 1:
        for key, value in vars(args).items():
            print(f"{key}={value}")
        return
    if args.test_repo:
        repo = TestRepository(args.repository)
    else:
        repo = NugetRepository(args.repository, args.framework)
    if args.stage == 2:
        for name, requirement in repo.dependencies(args.package, args.version):
            print(f"{name} {requirement}")
        return
    graph = GraphBuilder(repo, args.max_depth, args.exclude).build(
        args.package, args.version,
    )
    if args.stage == 4 or args.reverse:
        if args.test_repo:
            graph = test_universe(repo, args.max_depth, args.exclude)
        version = None if args.reverse else normalize(args.version)
        graph = reverse_graph(
            graph, args.reverse or args.package, args.max_depth, version,
        )
        print("Обратные зависимости в области анализа:")
    for line in graph_lines(graph):
        print(line)
    if args.stage == 5:
        source = render_graph(graph, args.output)
        print(f"D2: {source}; PNG: {args.output}")
    print(f"Узлов: {len(graph.edges)}; циклических рёбер: {len(graph.cycles)}")


def main(argv=None):
    """Показать понятную ошибку и ненулевой код при сбое."""
    args = parse_arguments(argv)
    try:
        execute(args)
    except (OSError, ValueError, KeyError, TypeError, ParseError,
            subprocess.TimeoutExpired) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
