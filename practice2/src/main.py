"""Точка входа CLI."""

from .config import parse_arguments


def main(argv=None):
    """Показать конфигурацию минимального прототипа."""
    args = parse_arguments(argv)
    for key, value in vars(args).items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
