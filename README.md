# neocortex-v2

Минимальный Python-контракт для следующего этапа neocortex. Его утверждение
означает переход координатора на Python: прежний TypeScript-псевдокод — только
материал дизайна и **не** является контрактом Python API. OpenCode остаётся
внешним исполнителем и владельцем истории; это не ослабляет governance-
инварианты исходного дизайна.

## Зафиксированный контракт

| Компонент | Выбор | Назначение |
| --- | --- | --- |
| Python | 3.13.5 (допускаются только 3.13.x) | координатор и проверки |
| pytest | 8.3.5 | тестовый раннер |
| Ruff | 0.9.10 | статическая проверка |
| OpenCode | `anomalyco/opencode` v1.18.30, кандидат | отдельный compatibility smoke |
| Python SDK | `opencode-ai==0.1.0a36` (pre-release), кандидат | отдельный compatibility smoke |

Версии pytest и Ruff закреплены в [requirements-dev.txt](requirements-dev.txt)
и [constraints.txt](constraints.txt); `pyproject.toml` повторяет их как `dev`
extra. Это воспроизводимый манифест прямых инструментов. Транзитивный lock с
hashes должен быть создан владельцем *после* выбора точного Orange Pi image и
Python ABI: иначе lock для другой платформы был бы ложной воспроизводимостью.

Источники выбора: [Python 3.13.5 release](https://www.python.org/downloads/release/python-3135/),
[pytest 8.3.5 на PyPI](https://pypi.org/project/pytest/8.3.5/),
[Ruff 0.9.10 на PyPI](https://pypi.org/project/ruff/0.9.10/),
[официальные releases OpenCode](https://github.com/anomalyco/opencode/releases)
и [opencode-ai на PyPI](https://pypi.org/project/opencode-ai/). Последний
помечен как pre-release, поэтому он не включён в runtime-зависимости и не
является одобренной интеграцией.

## Что наблюдал этот воркер

Offline-среда готова по результатам владельца и проверок воркера: Linux aarch64,
Python 3.13.5, Git 2.47.3, pytest 8.3.5 и Ruff 0.9.10. Воспроизводимое
свидетельство, включая команды, результаты и ссылку на ответ владельца, находится
в [docs/offline-environment-readiness.md](docs/offline-environment-readiness.md).
Никакие пакеты, сервисы, credentials или модель при подготовке не устанавливались
и не вызывались.

## Установка выполняется владельцем

Владелец подготовил один стабильный checkout `/opt/neocortex-v2-runner` и его
venv `/opt/neocortex-v2-runner/.venv`; `.venv-bootstrap` внутри worktree не
используется. Воркеры и арбитр запускают команды из корня своего назначенного
worktree, явно добавляя этот venv в `PATH`. Это не требует и не разрешает
воркеру изменять `/opt/neocortex-v2-runner`.

```console
$ export PATH=/opt/neocortex-v2-runner/.venv/bin:$PATH
$ python3 scripts/check_environment.py
$ pytest -q
$ ruff check .
```

`test_cmd` проекта для арбитра содержит тот же override, поэтому его shell не
обязан наследовать интерактивный `PATH` владельца:

```console
$ export PATH=/opt/neocortex-v2-runner/.venv/bin:$PATH; python -m pytest -q && ruff check .
```

На данном первом этапе stdlib bootstrap-проверки — временный контракт, который
можно принять до установки pytest/Ruff:

```console
$ python3 -m unittest discover -s tests_bootstrap -p "test_*.py"
$ python3 scripts/check_environment.py --help
```

После установки канонические проверки проекта — именно `pytest -q` и `ruff
check .`. В `tests/` есть базовый тест, поэтому pytest не заканчивается с `no
tests ran`.

`scripts/check_environment.py` использует только stdlib и только читает
состояние: проверяет Python 3.13.x, Git >= 2.40, точные pytest/Ruff, а также
импорты закреплённых модулей в том интерпретаторе, которым запущен скрипт. Он
раздельно печатает `MISSING`, `INCOMPATIBLE`, `AVAILABLE` и возвращает ненулевой
код при обязательном пробеле. Он не печатает credentials, не вызывает модель и
не проверяет живой сервис.

## Orange Pi и OpenCode: до следующей задачи

Кандидат OpenCode — immutable release `v1.18.30`; владелец должен сверить его
assets/checksums по официальной странице release. Официальный проект публикует
Linux архивы и container manifests, но это не обещает совместимость с каждой
Orange Pi OS. Кандидат SDK — `opencode-ai==0.1.0a36`: на PyPI это
`py3-none-any` wheel, но его транзитивные зависимости всё равно требуют
platform lock. Ruff 0.9.10 публикует wheels и для aarch64, и для armv7l (glibc
и musl варианты); это лишь доступность артефакта, не успешная установка на
целевом host. Ни OpenCode binary, ни доступность provider, ни native structured
output ещё не подтверждены.

Неизвестны и должны быть проверены владельцем: точная ARM64/ARMv7 архитектура,
дистрибутив/libc, Python ABI, свободное место и RAM, наличие подходящего
OpenCode binary/container, а также совместимость зависимостей SDK с этой
платформой. Возможные npm/Bun требования самого OpenCode относятся к его
отдельной установке; координатору Python npm toolchain не требуется.

Native structured output — отдельная compatibility-проверка. Его отсутствие
не разрешает текстовый или file fallback.

### Checklist владельца перед следующей задачей

- [x] Назвать целевой host, Orange Pi модель, OS, CPU-архитектуру и libc.
- [x] Утвердить абсолютные пути к venv, worktree и Python 3.13.x.
- [x] Подтвердить доступность этого Python, Git, pytest и Ruff воркеру и
  арбитру через явный `PATH` в `test_cmd`.
- [ ] Выбрать и проверить конкретные OpenCode release, binary/container и
  checksum для целевой архитектуры.
- [ ] Создать отдельные OpenCode data/config/history каталоги и отдельный
  loopback namespace/endpoint, не смешивая их с running neocortex.
- [ ] Согласовать provider/model selection и безопасный способ настройки
  credentials (секреты не передаются в ASK, логи или этот репозиторий).
- [ ] Отдельно провести compatibility smoke OpenCode + `opencode-ai`, включая
  native structured output; model access и live health пока не считать
  проверенными.
