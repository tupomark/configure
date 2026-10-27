"""Генерация языка D2 и сохранение PNG через CLI D2."""

import json
import shutil
import subprocess
from pathlib import Path

RENDER_TIMEOUT = 120
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def to_d2(graph):
    """Использовать безопасные ID и отдельные подписи вершин."""
    nodes = sorted(graph.edges)
    ids = {node: f"n{index}" for index, node in enumerate(nodes)}
    lines = ["direction: right"]
    for node in nodes:
        label = json.dumps(f"{node[0]}@{node[1]}", ensure_ascii=False)
        lines.append(f"{ids[node]}: {label}")
    for source in nodes:
        for target in sorted(graph.edges[source]):
            lines.append(f"{ids[source]} -> {ids[target]}")
    return "\n".join(lines) + "\n"


def render_graph(graph, output):
    """Сохранить D2 даже при отсутствии рендерера, проверить PNG."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    source = output.with_suffix(".d2")
    source.write_text(to_d2(graph), encoding="utf-8")
    executable = shutil.which("d2")
    if executable is None:
        raise ValueError(f"Установите D2; описание графа сохранено в {source}")
    result = subprocess.run(
        [executable, str(source), str(output)], capture_output=True,
        text=True, timeout=RENDER_TIMEOUT, check=False,
    )
    if result.returncode:
        raise ValueError(f"D2 завершился с ошибкой: {result.stderr.strip()}")
    with output.open("rb") as stream:
        if stream.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
            raise ValueError("D2 не создал корректный PNG")
    return source
