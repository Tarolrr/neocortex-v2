# Offline readiness среды

> Статус: **ready for review**. Offline readiness gate пройден после ответа
> владельца и проверок ниже. Это не является проверкой модели, OpenCode или
> structured output.

Дата: 2026-09-14.

## ASK и ответ владельца

Воркер использовал штатный ASK текущего Neocortex: запросил установку точных
`pytest==8.3.5` и `ruff==0.9.10` из `requirements-dev.txt` с
`constraints.txt`, доступность канонического Python/Git, путь venv и
подтверждение `test_cmd`; секреты, токены и значения credentials не
запрашивались. Ответ владельца, который устранил blocker и разъяснил механику
арбитра, сохранён в разделе `New messages for you` scheduler brief:
`/root/.neocortex/runs/worker-neocortex-v2-T006_20260914T215250Z/brief.md`.
Исход штатного ASK (включая точные запрошенные команды и единый перечень
подтверждений) сохранён отдельно:
`/root/.neocortex/runs/worker-neocortex-v2-T006_20260914T165550Z/outcome.json`.

Подтверждённые несекретные факты:

- canonical venv — `/opt/neocortex-v2-runner/.venv`, его Python —
  `/opt/neocortex-v2-runner/.venv/bin/python`, Python 3.13.5; venv read-only
  для воркера;
- host — `orangepizero2w`, Armbian 26.11.0 trixie, aarch64, glibc 2.41;
- в canonical venv имеются pytest 8.3.5 и Ruff 0.9.10;
- service `PATH` арбитра неизменно начинает venv раннера v1
  `/opt/neocortex-runner/.venv/bin` (pytest 9.1.1 и без Ruff), который нельзя
  менять. Его `$`-критерии не наследуют project `test_cmd`;
- project `test_cmd` явно добавляет canonical venv в `PATH` и проходит. Это
  единственная привязка pytest/Ruff к среде проекта для арбитра.

Поэтому `scripts/check_environment.py` выбирает canonical interpreter сам,
независимо от ambient `PATH`; для иной машины есть явный `--python PATH` и
диагностируемый fallback на вызвавший Python, если canonical path отсутствует.

## Воспроизводимый прогон воркера

Из корня `/root/.neocortex/work/neocortex-v2-T006` выполнено после ответа
владельца:

```console
$ python3 scripts/check_environment.py
# exit 0
AVAILABLE:
  - python: 3.13.5 (/opt/neocortex-v2-runner/.venv/bin/python)
  - git: 2.47.3 (/bin/git)
  - interpreter selection: /opt/neocortex-v2-runner/.venv/bin/python
  - pytest: 8.3.5 (/opt/neocortex-v2-runner/.venv/bin/python -m pytest)
  - ruff: 0.9.10 (/opt/neocortex-v2-runner/.venv/bin/python -m ruff)
  - import pytest: available
  - import ruff: available

$ export PATH=/opt/neocortex-v2-runner/.venv/bin:$PATH
$ pytest -q
1 passed in 0.03s
# exit 0
$ ruff check .
All checks passed!
# exit 0
$ python3 -m unittest discover -s tests_bootstrap -p 'test_*.py'
Ran 6 tests ... OK
# exit 0
```

Владелец отдельно подтвердил, что canonical project `test_cmd` арбитра
выполнен из назначенного worktree с тем же PATH override и завершился с кодом
0. Таким образом, service PATH арбитра не ошибочно принимается за project
venv; `check_environment.py` закрывает различие для первой `$`-проверки, а
`test_cmd` — для pytest/Ruff.

Ни пакеты, ни сервисы, ни credentials воркер не изменял.

## Prerequisites следующего планирования

Live-доступ к модели и native structured output не проверялись и не входят в
этот gate. Неизвестны параметры целевого OpenCode: окончательный release,
asset/checksum для архитектуры, binary/container, data/config/history каталоги,
loopback endpoint, provider/model, безопасная настройка credentials и
совместимость `opencode-ai==0.1.0a36` с платформой. Отдельно понадобятся
platform/transitive hash lock после выбора целевого image и ABI. Следующая
задача обязана планировать эти проверки отдельно; readiness этого offline Python
окружения их не предполагает.
