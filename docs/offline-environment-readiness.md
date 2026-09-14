# Offline readiness среды

> Статус: **waiting for owner**. Последняя проверка показала, что ранее
> подтверждённое `/opt/neocortex-v2-runner/.venv` не является окружением,
> которое сейчас выбирает арбитр (`/opt/neocortex-runner/.venv`). Поэтому
> успешный результат ниже не является пройденным readiness gate.

Дата проверки: 2026-09-14.

## Подтверждение владельца

Ответ владельца получен через штатный ASK текущего Neocortex. Его неизменяемая
локальная ссылка в scheduler transcript: `/root/.neocortex/runs/worker-neocortex-v2-T006_20260914T213122Z/session.log`.
В ответе подтверждены подготовка окружения и доступность для арбитра; секреты,
токены и credentials не запрашивались и не записывались.

Владелец сообщил следующие несекретные параметры:

- checkout окружения: `/opt/neocortex-v2-runner` (origin
  `/root/neocortex-v2`);
- venv и интерпретатор:
  `/opt/neocortex-v2-runner/.venv/bin/python`, Python 3.13.5;
- host: `orangepizero2w`, Armbian community 26.11.0-trunk.36 (Debian 13),
  aarch64, glibc 2.41;
- установлены из `requirements-dev.txt` с `constraints.txt`: pytest 8.3.5,
  Ruff 0.9.10;
- арбитр использует project `test_cmd`:
  `export PATH=/opt/neocortex-v2-runner/.venv/bin:$PATH; python -m pytest -q && ruff check .`.

Владелец также подтвердил `nc doctor --project neocortex-v2` как `doctor:
ready` и успешный readiness-прогон арбитра из одноразового worktree базовой
ветки. Это подтверждение относится к указанному владельцем пути
`/opt/neocortex-v2-runner`; после повторной проверки оно требует уточнения для
фактического пути арбитра.

## Повторная проверка воркера

Команды выполнены 2026-09-14 из корня назначенного worktree
`/root/.neocortex/work/neocortex-v2-T006`:

```console
$ export PATH=/opt/neocortex-v2-runner/.venv/bin:$PATH
$ python --version
Python 3.13.5
$ python3 --version
Python 3.13.5
$ git --version
git version 2.47.3
$ python3 scripts/check_environment.py
MISSING:
INCOMPATIBLE:
AVAILABLE:
  - python: 3.13.5 (/opt/neocortex-v2-runner/.venv/bin/python3)
  - git: 2.47.3 (/bin/git)
  - pytest: 8.3.5 (/opt/neocortex-v2-runner/.venv/bin/python3 -m pytest)
  - ruff: 0.9.10 (/opt/neocortex-v2-runner/.venv/bin/python3 -m ruff)
  - import pytest: available
  - import ruff: available
$ pytest -q
1 passed in 0.03s
$ ruff check .
All checks passed!
```

Этот запуск с `/opt/neocortex-v2-runner/.venv` завершился с кодом 0. Он
свидетельствует только о состоянии этого отдельного venv, но не подтверждает
offline readiness арбитра.

## Повторная проверка фактического окружения арбитра

В ходе повторного арбитражного прогона 2026-09-14 его shell выбрал
`/opt/neocortex-runner/.venv/bin/python3`, а не путь из подтверждения
владельца. В назначенном worktree выполнены ровно канонические команды:

```console
$ export PATH=/opt/neocortex-runner/.venv/bin:$PATH
$ python3 scripts/check_environment.py
MISSING:
  - ruff: not runnable in /opt/neocortex-runner/.venv/bin/python3: '/opt/neocortex-runner/.venv/bin/python3: No module named ruff'
  - import ruff: not installed in /opt/neocortex-runner/.venv/bin/python3
INCOMPATIBLE:
  - pytest: 9.1.1, need 8.3.5
AVAILABLE:
  - python: 3.13.5 (/opt/neocortex-runner/.venv/bin/python3)
  - git: 2.47.3 (/bin/git)
  - import pytest: available
# exit 1
$ pytest -q
1 passed in 0.05s
# exit 0
$ ruff check .
/usr/bin/bash: ruff: command not found
# exit 127
```

Следующий шаг требует нового ответа владельца через ASK: установить в
`/opt/neocortex-runner/.venv` строго `pytest==8.3.5` и `ruff==0.9.10` из
`requirements-dev.txt` с `constraints.txt`, затем подтвердить, что арбитр
использует именно этот venv в `project test_cmd` (без секретов). До этого
ответа и успешного повтора трёх команд задача не готова, а
`python-offline-baseline` начинать нельзя. Воркер не менял host, venv или
сервисы.

## Известные prerequisites следующего этапа

Live-доступ к модели и native structured output не проверялись и не входят в
этот gate. Остаются непроверенными кандидаты OpenCode `anomalyco/opencode`
v1.18.30 и `opencode-ai==0.1.0a36`: владелец ещё не зафиксировал asset/checksum.
Также не подготовлены отдельные data/config/history каталоги и loopback-only
доступ OpenCode. Platform SDK lock и транзитивный hash lock отложены до выбора
образа/ABI. Provider/model и остальные параметры целевого OpenCode пока
неизвестны; их нельзя предполагать при следующем планировании.
