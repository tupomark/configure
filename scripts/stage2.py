"""Этап 2: получение прямых зависимостей по HTTP из настоящего nuspec."""

from .checks import expect_lines, run_checks, run_cli
from .local_feed import local_feed

STAGE = 2
DATA_ERROR = 1


def demonstrate():
    """Различить версии корня, прямые связи, лист и сетевую ошибку."""
    with local_feed() as url:
        base = ["--repository", url, "--framework", "net8.0"]
        cases = [
            ("A", "1", ["B [1.0.0]"]),
            ("A", "2", ["C [1.0.0]"]),
            ("C", "1", []),
        ]
        for package, version, expected in cases:
            arguments = base + ["--package", package, "--version", version]
            expect_lines(run_cli(STAGE, arguments), expected)
        run_cli(
            STAGE, base + ["--package", "A", "--version", "99"], DATA_ERROR,
        )


if __name__ == "__main__":
    run_checks(STAGE, "test_nuget.py", demonstrate)
