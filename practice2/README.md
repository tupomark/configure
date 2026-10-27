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

## Этап 3. Граф

```sh
sh run.sh --package A --version 1 --test-repo \
  --repository examples/cycle.json --stage 3
sh run.sh --package A --version 1 --test-repo \
  --repository examples/diamond.json --max-depth 3 --stage 3
sh run.sh --package A --version 1 --test-repo \
  --repository examples/diamond.json --exclude D --stage 3
```

`GraphBuilder.build` использует рекурсивный DFS. Корень имеет глубину 0.
На границе глубины вершина сохраняется, но не раскрывается.
Фильтр исключает пакет и обход через него; регистр не важен.
Замыкающее ребро цикла сохраняется. Повторно найденный более короткий путь
позволяет раскрыть общую вершину глубже (пример diamond).
`TestRepository` читает JSON: пакет → версия → зависимости с диапазонами.
`graph_lines` выводит граф в устойчивом порядке.

## Этап 4. Обратные зависимости

```sh
sh run.sh --package B --version 1 --test-repo \
  --repository examples/cycle.json --stage 4
sh run.sh --package E --version 1 --test-repo \
  --repository examples/cycle.json --stage 4
```

`test_universe` обходит все версии тестового репозитория.
`ReversedRepository` обращает рёбра; `reverse_graph` использует DFS этапа 3.
Для B находятся A, C и D; для E потребителей нет.
Для реального NuGet поиск ограничен графом от `--package`.
`--reverse NAME` выбирает пакет внутри этой области (все найденные версии).
Полный поиск потребителей во всём NuGet V3 не предоставляется API.

## Этап 5. Визуализация

Нужен установленный CLI [D2](https://d2lang.com/tour/install/).
На macOS: `brew install d2`. Проверка: `d2 --version`.

```sh
sh run.sh --package A --version 1 --test-repo \
  --repository examples/cycle.json --stage 5 --output output/cycle.png
```

`to_d2` создаёт текст D2. `render_graph` сохраняет `.d2` и вызывает D2
для создания `.png`. Без D2 текст сохраняется, программа возвращает ошибку.
Готовые средства получения зависимостей не используются: D2 только рисует.

Три реальные демонстрации и сравнение с .NET SDK 8:

```sh
python3 -m scripts.demonstrate
```

Пакеты: Serilog.Sinks.Console 6.0.0, Serilog.Sinks.File 6.0.0,
Serilog.Formatting.Compact 3.0.0. Для каждого сохраняются D2, PNG,
текст графа и штатный JSON `dotnet list package --include-transitive`.
Сравнение множеств пакет/версия записывается в `output/comparison.json`.
Менеджер dotnet используется только для независимого сравнения.

Граф объявленных зависимостей не является полной копией NuGet restore.
По умолчанию объединяются framework-группы; dotnet выбирает совместимую
с целевым framework. Возможны отличия из-за выбора групп, разрешения
конфликтов версий и ограничения глубины. В графе сохраняются разные версии
одного пакета, а правила direct-dependency-wins не применяются.
PNG и PDF не коммитятся: это бинарные результаты работы.

## Установка и структура

```sh
git clone https://github.com/tupomark/configure.git
cd configure/practice2
python3 --version
python3 -m unittest discover -s tests -v
```

Исходный код: `src/`; тесты: `tests/`; локальные репозитории: `examples/`;
сценарий сравнения: `scripts/demonstrate.py`; запуск: `run.sh`.
Python-зависимости для работы приложения и тестов устанавливать не нужно.
Для реальной сети нужен доступ к URL индекса и PackageBaseAddress.
Сборка не нужна: Python исполняет исходные файлы.

| Параметр | Значение и проверка |
| --- | --- |
| `--package` | Обязательное имя NuGet; в тестовом режиме только A-Z |
| `--version` | Обязательная конкретная версия корня, не диапазон |
| `--repository` | HTTP(S) индекс NuGet V3 либо JSON с `--test-repo` |
| `--test-repo` | Флаг, переключающий источник на локальный JSON |
| `--output` | PNG-путь; по умолчанию `output/graph.png` |
| `--max-depth` | Целое 0-100; по умолчанию 3; корень на глубине 0 |
| `--exclude` | Непустая исключаемая подстрока без учёта регистра |
| `--stage` | Этап 1-5; по умолчанию 1 для показа конфигурации |
| `--framework` | Точное имя группы nuspec; без параметра объединение |
| `--reverse` | Имя пакета для обратного обхода внутри области анализа |

Ошибки аргументов возвращают код 2. Сетевые, XML/JSON и файловые ошибки,
отсутствие версии и сбой D2 возвращают код 1. Успех возвращает код 0.
Родительские каталоги результата создаются автоматически.

## Функции и классы

| Модуль | Назначение функций |
| --- | --- |
| `config` | `package_id`, `version`, `depth`, `nonempty`, `output_path`: проверка значений |
| `config` | `validate_source`: проверка источника; `parse_arguments`: разбор CLI |
| `versions` | `version_key`: сортировка; `normalize`: нормализация URL-версий |
| `versions` | `range_bounds`, `exact_bounds`, `satisfies`: интервалы; `select_version`: выбор |
| `nuget` | `fetch_bytes`: HTTP; `parse_nuspec`, `select_groups`: XML и framework |
| `nuget` | `NugetRepository`: индекс, кэш, `versions`, `resolve`, `dependencies` |
| `test_repository` | `TestRepository`: проверка JSON, `resolve`, `dependencies` |
| `graph` | `Graph`: данные; `GraphBuilder.build`, `_visit`: DFS; `_excluded`: фильтр |
| `graph` | `graph_lines`: стабильный текстовый вывод графа |
| `reverse` | `merge_graphs`: объединение; `test_universe`: все локальные версии |
| `reverse` | `ReversedRepository`: адаптер; `reverse_graph`: обратный DFS |
| `visualize` | `to_d2`: текст диаграммы; `render_graph`: файлы D2 и PNG |
| `main` | `execute`: этапы; `apply_reverse`: обратный обход; `main`: ошибки и код выхода |
| `scripts.demonstrate` | `command`, `compare`, `main`: независимая проверка через dotnet |
| `scripts.export_readme` | `main`: печать README в Chromium, аналог Ctrl+P |

Числовые версии нормализуются до трёх или четырёх частей; build-метаданные
не участвуют в сравнении. Поддерживаются bare minimum, `[exact]`, интервалы
с открытыми границами, `*` и числовой floating-суффикс `1.*`.
Для обычного диапазона выбирается минимальная подходящая версия;
для floating выбирается максимальная стабильная. Prerelease допускается,
когда он явно присутствует в требовании. Экзотические floating-выражения
вроде `1.0.0-rc.*` не поддерживаются и возвращают ошибку.

## Локальные проверки по этапам

В ветке `main` сначала выполните `cd practice2`.
В отдельной ветке `practice2-variant31` команды выполняются из корня.

| Этап | Команда | Что проверяется |
| --- | --- | --- |
| 1 | `./scripts/check_stage1.sh` | Все параметры и ошибки каждого вида настроек |
| 2 | `./scripts/check_stage2.sh` | Получение прямых зависимостей из nuspec по HTTP |
| 3 | `./scripts/check_stage3.sh` | DFS, глубина 0/1/3, фильтр, цикл и выбор версии |
| 4 | `./scripts/check_stage4.sh` | Прямые и транзитивные потребители, цикл и отсутствие потребителей |
| 5 | `./scripts/check_stage5.sh` | Точный текст D2 и настоящие PNG для пакетов A, B и E |

Каждый сценарий сначала запускает модульные тесты своего этапа,
затем вызывает настоящий CLI с `--stage N` и проверяет его результат.
Ошибка завершает сценарий ненулевым кодом; успешный этап заканчивается
строкой `PASS: этап N`. Сообщения об ошибках в отрицательных примерах
ожидаемы: сценарий проверяет, что CLI вернул именно код ошибки.

Для этапов 1-4 нужен только Python 3.11+. Интернет не требуется.
На этапе 2 временно запускается HTTP-сервер на `127.0.0.1` со свободным
портом. Он обслуживает `examples/nuget/flat/`: версии A, B и C в формате
NuGet. После проверки сервер закрывается. Проверяется, что A версии 1
зависит прямо от B, A версии 2 - от C, а транзитивный C для A версии 1
не попадает в вывод прямых зависимостей.

Для этапа 5 дополнительно нужен CLI D2. На macOS:

```sh
brew install d2
./scripts/check_stage5.sh
```

Изображения и описания сохраняются в `output/stage5/`.
Без D2 текст диаграммы сохраняется, но сценарий честно возвращает ошибку:
создание PNG в таком случае не считается проверенным.

Все пять этапов, а затем полный набор модульных тестов:

```sh
./scripts/check_all.sh
```

Только все модульные тесты, без интернета, D2 и .NET:

```sh
./scripts/check_tests.sh
```

Три реальных пакета NuGet и сравнение с dotnet:

```sh
./scripts/check_real.sh
```

Для последней команды нужны интернет, D2 и .NET SDK 8.
Она сохраняет D2, PNG, штатные списки зависимостей и `comparison.json`
в `output/`. Это отдельная проверка реального репозитория;
`check_all.sh` не требует внешней сети и .NET.

Сценарии запуска определяют папку работы автоматически и могут вызываться
по полному пути из другого каталога. На сервер GitHub ничего отправлять
для проверки не нужно. Каталог `.github/workflows` удалён: проверки
выполняются локально по командам выше.

Вспомогательные файлы:

- `scripts/checks.py`: запуск CLI, проверка кодов и ожидаемых результатов;
- `scripts/stage1.py` - `scripts/stage5.py`: сценарии конкретных этапов;
- `scripts/local_feed.py`: временный локальный HTTP-репозиторий NuGet;
- `examples/nuget/flat/`: текстовые nuspec и списки версий пакетов;
- `scripts/check_*.sh`: короткие команды запуска проверок.

История первоначальных пяти этапов сохранена. Для добавления проверок
откат и переписывание старых коммитов не требуются: режим `--stage`
выбирает операции соответствующего этапа в текущей версии программы.
