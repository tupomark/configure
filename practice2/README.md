# Практическая работа №2. Вариант 31

Инструмент визуализации зависимостей NuGet на Python 3.11+.
Получение данных реализуется стандартной библиотекой Python.

## Этап 1. Конфигурация

`sh run.sh --package Example --version 1.0.0 --stage 1`

Прототип печатает настройки в формате ключ=значение.
Доступные параметры: `--package`, `--version`, `--repository`,
`--test-repo`, `--output`, `--max-depth`, `--exclude`.
Режим этапа задаётся параметром `--stage` (1-5).
Некорректные аргументы завершают программу с кодом 2.

Сборка не требуется. Запуск тестов:
`python3 -m unittest discover -s tests -v`.

## Этап 2. Получение данных

`sh run.sh --package Serilog --version 4.0.0 --stage 2`

Индекс NuGet V3 указывает адрес PackageBaseAddress.
Программа читает XML `.nuspec` указанной версии и выводит прямые зависимости.
По умолчанию объединяются все объявленные framework-группы.
`--framework` выбирает точное имя группы из nuspec.
Функции `parse_nuspec`, `select_version`, `normalize` обрабатывают XML и версии.
Класс `NugetRepository` получает и кэширует данные.

Основание: [NuGet API](https://learn.microsoft.com/en-us/nuget/api/package-base-address-resource),
[версии NuGet](https://learn.microsoft.com/en-us/nuget/concepts/package-versioning).
