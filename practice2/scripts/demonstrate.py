"""Три реальные визуализации и сравнение с dotnet list package."""

import json
import subprocess
from pathlib import Path
from src.graph import GraphBuilder, graph_lines
from src.nuget import NugetRepository
from src.visualize import render_graph

PACKAGES = [
    ("Serilog.Sinks.Console", "6.0.0"),
    ("Serilog.Sinks.File", "6.0.0"),
    ("Serilog.Formatting.Compact", "3.0.0"),
]
OUTPUT = Path("output")


def command(arguments, cwd=None):
    """Выполнить штатный инструмент и сохранить ошибки в журнале."""
    return subprocess.check_output(
        arguments, cwd=cwd, text=True, stderr=subprocess.STDOUT,
    )


def compare(name, version, graph):
    """Сравнить набор package/version со штатным выводом .NET SDK 8."""
    project = OUTPUT / name
    project.mkdir(parents=True, exist_ok=True)
    command(["dotnet", "new", "classlib", "-f", "net8.0", "--force"], project)
    command(["dotnet", "add", "package", name, "--version", version], project)
    raw = command([
        "dotnet", "list", "package", "--include-transitive", "--format", "json",
    ], project)
    (OUTPUT / f"{name}.native.json").write_text(raw, encoding="utf-8")
    data = json.loads(raw)
    native = set()
    for item in data["projects"]:
        for framework in item["frameworks"]:
            for kind in ("topLevelPackages", "transitivePackages"):
                for package in framework.get(kind, []):
                    node = (
                        package["id"].lower(), package["resolvedVersion"],
                    )
                    native.add(node)
    ours = set(graph.edges)
    return {"package": name, "version": version, "equal": ours == native,
            "only_graph": sorted(ours - native),
            "only_dotnet": sorted(native - ours)}


def main():
    """Сохранить PNG, D2, фактические графы и результаты сравнения."""
    OUTPUT.mkdir(exist_ok=True)
    repository = NugetRepository(
        "https://api.nuget.org/v3/index.json", framework="net8.0",
    )
    results = []
    for name, version in PACKAGES:
        graph = GraphBuilder(repository, 10).build(name, version)
        render_graph(graph, OUTPUT / f"{name}.png")
        (OUTPUT / f"{name}.graph.txt").write_text(
            "\n".join(graph_lines(graph)) + "\n", encoding="utf-8",
        )
        results.append(compare(name, version, graph))
    (OUTPUT / "comparison.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8",
    )
    print(json.dumps(results, indent=2))
    if not all(item["equal"] for item in results):
        raise SystemExit("Граф и dotnet расходятся; см. comparison.json")


if __name__ == "__main__":
    main()
