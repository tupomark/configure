"""Параметры командной строки и проверка их значений."""

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

MAX_DEPTH = 100
ID_PATTERN = r"[A-Za-z0-9_][A-Za-z0-9_.-]*"
VERSION_PATTERN = (
    r"\d+(?:\.\d+){0,3}(?:-[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*)?"
    r"(?:\+[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*)?"
)


def package_id(value):
    """Проверить идентификатор пакета NuGet."""
    if not re.fullmatch(ID_PATTERN, value):
        raise argparse.ArgumentTypeError("некорректное имя пакета")
    return value


def version(value):
    """Проверить конкретную версию, а не диапазон."""
    if not re.fullmatch(VERSION_PATTERN, value):
        raise argparse.ArgumentTypeError("нужна конкретная версия, например 1.0.0")
    return value


def depth(value):
    """Ограничить глубину безопасным для рекурсии диапазоном."""
    try:
        result = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("глубина должна быть целой") from error
    if not 0 <= result <= MAX_DEPTH:
        raise argparse.ArgumentTypeError(f"глубина должна быть 0..{MAX_DEPTH}")
    return result


def nonempty(value):
    """Не разрешать пустую подстроку, совпадающую со всеми пакетами."""
    if not value.strip():
        raise argparse.ArgumentTypeError("значение не может быть пустым")
    return value


def output_path(value):
    """Проверить расширение и тип пути будущего изображения."""
    path = Path(value)
    if path.suffix.lower() != ".png" or path.is_dir():
        raise argparse.ArgumentTypeError("нужен путь к файлу .png")
    if path.with_suffix(".d2").is_dir():
        raise argparse.ArgumentTypeError("путь .d2 занят каталогом")
    return path


def validate_source(parser, args):
    """Разделить локальный JSON и сетевой индекс NuGet V3."""
    if args.test_repo:
        if not Path(args.repository).is_file():
            parser.error("--repository: тестовый файл не найден")
        if not re.fullmatch(r"[A-Z]+", args.package):
            parser.error("--package: в тестовом режиме нужны буквы A-Z")
        return
    url = urlparse(args.repository)
    if url.scheme not in ("https", "http") or not url.hostname:
        parser.error("--repository: нужен HTTP(S) URL индекса NuGet V3")
    if url.username or url.password or url.fragment:
        parser.error("--repository: логин, пароль и фрагмент не поддерживаются")


def parse_arguments(argv=None):
    """Прочитать семь обязательных настроек варианта и режим этапа."""
    parser = argparse.ArgumentParser(description="NuGet: ПР2, вариант 31")
    parser.add_argument("--package", required=True, type=package_id)
    parser.add_argument("--version", required=True, type=version)
    parser.add_argument("--repository", default="https://api.nuget.org/v3/index.json")
    parser.add_argument("--test-repo", action="store_true")
    parser.add_argument("--output", type=output_path, default=Path("output/graph.png"))
    parser.add_argument("--max-depth", type=depth, default=3)
    parser.add_argument("--exclude", type=nonempty, default=None)
    parser.add_argument("--stage", type=int, choices=range(1, 6), default=1)
    parser.add_argument("--reverse", type=package_id)
    parser.add_argument("--framework", type=nonempty)
    args = parser.parse_args(argv)
    validate_source(parser, args)
    return args
