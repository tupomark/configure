"""Нормализация NuGet-версий и выбор версии из диапазона."""

import re
from .config import VERSION_PATTERN

VERSION_PARTS = 4


def version_key(value):
    """Построить ключ сортировки с учётом prerelease и revision."""
    if not re.fullmatch(VERSION_PATTERN, value):
        raise ValueError(f"Некорректная версия: {value}")
    clean = value.split("+")[0].lower()
    base, separator, suffix = clean.partition("-")
    numbers = [int(part) for part in base.split(".")]
    numbers += [0] * (VERSION_PARTS - len(numbers))
    labels = tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in suffix.split(".")
    ) if separator else ()
    return tuple(numbers), not separator, labels


def normalize(value):
    """Получить нормализованную версию для URL flat container."""
    numbers, stable, labels = version_key(value)
    parts = list(numbers)
    if not parts[-1]:
        parts.pop()
    result = ".".join(str(part) for part in parts)
    if not stable:
        result += "-" + ".".join(str(part[1]) for part in labels)
    return result


def range_bounds(requirement):
    """Разобрать точную версию, нижний предел или интервал."""
    value = requirement.strip()
    if not value or value == "*":
        return None, None, True, True
    if value.startswith(("[", "(")):
        if not value.endswith(("]", ")")):
            raise ValueError(f"Незакрытый диапазон: {value}")
        inside = value[1:-1]
        if "," not in inside:
            if value.startswith("[") and value.endswith("]") and inside:
                key = version_key(inside)
                return key, key, True, True
            raise ValueError(f"Некорректный диапазон: {value}")
        lower, upper = (part.strip() for part in inside.split(",", 1))
        return (
            version_key(lower) if lower else None,
            version_key(upper) if upper else None,
            value.startswith("["), value.endswith("]"),
        )
    return version_key(value), None, True, False


def satisfies(value, bounds):
    """Проверить обе границы интервала."""
    lower, upper, include_lower, include_upper = bounds
    key = version_key(value)
    low_ok = lower is None or key > lower or (include_lower and key == lower)
    high_ok = upper is None or key < upper or (include_upper and key == upper)
    return low_ok and high_ok


def select_version(versions, requirement):
    """Выбрать минимум в интервале или максимум для floating-версии."""
    value = requirement.strip()
    floating = value.endswith(".*")
    if floating:
        prefix = value[:-1]
        version_key(value[:-2])
        candidates = [item for item in versions if item.startswith(prefix)]
        bounds = range_bounds("*")
    else:
        candidates = list(versions)
        bounds = range_bounds(value)
    matching = [
        item for item in candidates
        if satisfies(item, bounds)
        and (version_key(item)[1] or "-" in value)
    ]
    if not matching:
        raise ValueError(f"Нет версии, подходящей под {requirement!r}")
    chooser = max if floating else min
    return normalize(chooser(matching, key=version_key))
