"""Чтение HTTP API NuGet V3 и XML без менеджеров пакетов."""

import json
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .versions import normalize, select_version

TIMEOUT = 20
MAX_RESPONSE = 10 * 1024 * 1024


def fetch_bytes(url):
    """Прочитать ограниченный ответ с тайм-аутом и явной ошибкой."""
    request = Request(url, headers={"User-Agent": "nuget-graph-pr2/1.0"})
    with urlopen(request, timeout=TIMEOUT) as response:
        result = response.read(MAX_RESPONSE + 1)
    if len(result) > MAX_RESPONSE:
        raise ValueError("Ответ репозитория превышает 10 MiB")
    return result


def parse_nuspec(data, framework=None):
    """Извлечь объявленные зависимости всех или одной точной группы."""
    root = ElementTree.fromstring(data)
    for element in root.iter():
        element.tag = element.tag.split("}")[-1]
    metadata = root.find("metadata")
    if metadata is None:
        raise ValueError("В nuspec отсутствует metadata")
    dependencies = metadata.find("dependencies")
    if dependencies is None:
        return []
    groups = list(dependencies.findall("group"))
    selected = groups
    if framework:
        selected = [
            group for group in groups
            if group.get("targetFramework", "").casefold() == framework.casefold()
        ]
        if groups and not selected:
            names = [group.get("targetFramework", "") for group in groups]
            raise ValueError(
                f"Нет группы {framework}; доступны: {names}"
            )
    elements = list(dependencies.findall("dependency"))
    for group in selected:
        elements.extend(group.findall("dependency"))
    result = set()
    for item in elements:
        name = item.get("id")
        if not name:
            raise ValueError("У зависимости отсутствует id")
        result.add((name, item.get("version", "*")))
    return sorted(result, key=lambda pair: (pair[0].casefold(), pair[1]))


class NugetRepository:
    """Кэшировать версии и nuspec внутри одного запуска."""

    def __init__(self, index_url, framework=None, fetcher=fetch_bytes):
        """Найти PackageBaseAddress в пользовательском индексе."""
        self.fetcher = fetcher
        self.framework = framework
        self.version_cache = {}
        self.dependency_cache = {}
        index = json.loads(fetcher(index_url))
        resources = index.get("resources", [])
        addresses = [
            item["@id"] for item in resources
            if str(item.get("@type", "")).startswith("PackageBaseAddress/")
        ]
        if not addresses:
            raise ValueError("Индекс не содержит PackageBaseAddress")
        self.base = addresses[0].rstrip("/")

    def versions(self, name):
        """Получить список версий из flat container."""
        name = name.lower()
        if name not in self.version_cache:
            data = self.fetcher(f"{self.base}/{name}/index.json")
            self.version_cache[name] = json.loads(data)["versions"]
        return self.version_cache[name]

    def resolve(self, name, requirement):
        """Выбрать минимальную подходящую версию зависимости."""
        return select_version(self.versions(name), requirement)

    def dependencies(self, name, version):
        """Загрузить nuspec конкретной версии по документированному URL."""
        name, version = name.lower(), normalize(version)
        key = (name, version)
        if key not in self.dependency_cache:
            url = f"{self.base}/{name}/{version}/{name}.nuspec"
            data = self.fetcher(url)
            self.dependency_cache[key] = parse_nuspec(data, self.framework)
        return self.dependency_cache[key]
