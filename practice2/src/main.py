"""Точка входа CLI."""

import sys
from .config import parse_arguments
from .nuget import NugetRepository


def main(argv=None):
    """Показать конфигурацию минимального прототипа."""
    args = parse_arguments(argv)
    if args.stage == 1:
        for key, value in vars(args).items():
            print(f"{key}={value}")
        return 0
    try:
        repo = NugetRepository(args.repository, args.framework)
        for name, requirement in repo.dependencies(args.package, args.version):
            print(f"{name} {requirement}")
    except (OSError, ValueError, KeyError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
