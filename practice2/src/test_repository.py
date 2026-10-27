"""Локальный репозиторий пакетов с именами из букв A-Z."""

import json
import re
from pathlib import Path

from .versions import normalize, select_version


class TestRepository:
    """Использовать JSON вместо HTTP, сохраняя интерфейс репозитория."""

    def __init__(self, path):
        """Прочитать файл и проверить все записи, включая недостижимые."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not data:
            raise ValueError(
                "Тестовый репозиторий должен быть непустым объектом"
            )
        self.packages = {}
        for name, versions in data.items():
            self._validate_name(name)
            if not isinstance(versions, dict) or not versions:
                raise ValueError(f"У {name} должен быть объект версий")
            self.packages[name] = self._read_versions(versions)
        for versions in self.packages.values():
            for dependencies in versions.values():
                for name, requirement in dependencies:
                    self.resolve(name, requirement)

    @staticmethod
    def _validate_name(name):
        """Потребовать заглавные латинские буквы."""
        if not re.fullmatch(r"[A-Z]+", name):
            raise ValueError(
                f"Имя тестового пакета должно состоять из A-Z: {name}"
            )

    def _read_versions(self, versions):
        """Нормализовать версии и проверить списки зависимостей."""
        result = {}
        for version, dependencies in versions.items():
            key = normalize(version)
            if key in result or not isinstance(dependencies, dict):
                raise ValueError(
                    "Повторная версия или неверный объект зависимостей"
                )
            for name, requirement in dependencies.items():
                self._validate_name(name)
                if not isinstance(requirement, str):
                    raise ValueError("Диапазон версии должен быть строкой")
            result[key] = sorted(dependencies.items())
        return result

    def resolve(self, name, requirement):
        """Найти версию зависимости в локальном наборе."""
        if name not in self.packages:
            raise ValueError(f"Пакет {name} не найден в тестовом репозитории")
        return select_version(self.packages[name], requirement)

    def dependencies(self, name, version):
        """Вернуть прямые зависимости конкретной версии."""
        try:
            return self.packages[name][normalize(version)]
        except KeyError as error:
            raise ValueError(f"Нет пакета {name} версии {version}") from error
