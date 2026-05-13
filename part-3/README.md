# Раздел 3: Автоматизация с помощью Ansible

## Что делает playbook

`playbook.yml` автоматизирует проверку решения на целевом Ubuntu/Debian-хосте:

- устанавливает Docker и необходимые зависимости;
- добавляет текущего пользователя в группу `docker`;
- запускает и включает службу `docker`;
- проверяет `docker --version`;
- копирует артефакты из `part-1` и `part-2` на целевой хост;
- собирает Docker-образ;
- запускает контейнер со скриптом;
- читает результат через `docker logs`;
- автоматически проверяет exit code контейнера и наличие `script_completed`.

## Запуск на localhost

Из корня репозитория:

```bash
cd part-3
ansible-playbook playbook.yml --ask-become-pass
```

Если пользователь может выполнять `sudo` без пароля:

```bash
cd part-3
ansible-playbook playbook.yml
```

## Запуск на удалённом хосте

Замените `localhost` в `inventory.ini` на адрес целевого хоста:

```ini
[targets]
server ansible_host=192.0.2.10 ansible_user=ubuntu
```

Запуск:

```bash
cd part-3
ansible-playbook playbook.yml --ask-become-pass
```

## Переменные

По умолчанию используются:

- образ: `yadro-2026:part-3`;
- контейнер: `yadro-2026-part-3`;
- директория сборки на целевом хосте: `/tmp/yadro-2026-docker-build`;
- шаблон URL: `https://httpbingo.org/status/{status}`.

Шаблон URL можно переопределить:

```bash
ansible-playbook playbook.yml \
  -e "http_status_url_template=https://httpstat.us/{status}" \
  --ask-become-pass
```

## Ручная проверка логов

После выполнения playbook на целевом хосте:

```bash
docker logs yadro-2026-part-3
docker inspect yadro-2026-part-3 --format '{{.State.ExitCode}}'
```

Ожидаемый код завершения: `0`.
