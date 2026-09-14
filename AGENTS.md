# Контракт работы в этом worktree

Запускайте команды из корня данного worktree. Не устанавливайте пакеты на host и
не изменяйте `/root/neocortex` либо `/opt/neocortex-runner`.

Владелец предоставляет изолированное окружение в
`/opt/neocortex-v2-runner/.venv`; не создавайте и не изменяйте его. Перед
каноническими проверками в любом назначенном worktree выберите его явно:

```console
$ export PATH=/opt/neocortex-v2-runner/.venv/bin:$PATH
$ pytest -q
$ ruff check .
```

Арбитр применяет этот же `PATH` override в project `test_cmd`; не полагайтесь
на совпадение с интерактивным shell владельца. До появления обычных тестов
bootstrap-контракт первой задачи остаётся независимым от внешних пакетов:

```console
$ python3 -m unittest discover -s tests_bootstrap -p "test_*.py"
```

`pytest -q` не является заменой bootstrap-проверок и после подготовки проекта
не должен завершаться сообщением `no tests ran`.

OpenCode — внешний исполнитель и владелец истории. Переход координатора на
Python не меняет governance-инварианты исходного дизайна.
