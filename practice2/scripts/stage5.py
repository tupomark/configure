"""Этап 5: D2 и настоящие PNG для трёх тестовых пакетов."""

import shutil
import struct
from pathlib import Path

from .checks import ROOT, local_arguments, run_checks, run_cli

STAGE = 5
OUTPUT = ROOT / "output" / "stage5"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
HEADER_SIZE = 24
MIN_DIMENSION = 0
CYCLE_D2 = (
    'direction: right\nn0: "a@1.0.0"\nn1: "b@1.0.0"\n'
    'n2: "c@1.0.0"\nn0 -> n1\nn1 -> n2\nn2 -> n0\n'
)
CASES = [
    ("A", CYCLE_D2), ("B", CYCLE_D2),
    ("E", 'direction: right\nn0: "e@1.0.0"\n'),
]


def check_files(output, expected_d2):
    """Проверить точный D2, сигнатуру PNG и размеры изображения."""
    text = output.with_suffix(".d2").read_text(encoding="utf-8")
    if text != expected_d2:
        raise AssertionError(f"Неожиданный D2 в {output.with_suffix('.d2')}")
    with output.open("rb") as stream:
        header = stream.read(HEADER_SIZE)
    if not header.startswith(PNG_SIGNATURE) or len(header) != HEADER_SIZE:
        raise AssertionError(f"Некорректный PNG: {output}")
    width, height = struct.unpack(">II", header[16:24])
    if min(width, height) <= MIN_DIMENSION:
        raise AssertionError("Изображение имеет нулевой размер")
    print(f"PNG проверен: {output.name}, {width} x {height}")


def demonstrate():
    """Создать три изображения, не выдавая старые результаты за новые."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for package, expected in CASES:
        output = OUTPUT / f"{package}.png"
        output.unlink(missing_ok=True)
        output.with_suffix(".d2").unlink(missing_ok=True)
        arguments = local_arguments(
            "cycle", package, "--max-depth", "10", "--output", output,
        )
        if shutil.which("d2") is None:
            run_cli(STAGE, arguments, expected_code=1)
            raise SystemExit(
                "D2 не установлен. macOS: brew install d2. "
                "PNG-проверка НЕ пройдена; текст D2 сохранён."
            )
        run_cli(STAGE, arguments)
        check_files(output, expected)


if __name__ == "__main__":
    run_checks(STAGE, "test_visualize.py", demonstrate)
