# Раздел 2: Работа с Docker

## Сборка образа

```bash
docker build -f part-2/Dockerfile -t yadro-2026:part-2 .
```

## Запуск контейнера

```bash
docker run --name yadro-2026-part-2 yadro-2026:part-2
```

Если основной внешний сервис недоступен, можно передать альтернативный шаблон
URL через переменную окружения:

```bash
docker run --name yadro-2026-part-2-alt \
  -e HTTP_STATUS_URL_TEMPLATE='https://httpbingo.org/status/{status}' \
  yadro-2026:part-2
```

Если контейнер с таким именем уже существует, удалите его перед повторным
запуском:

```bash
docker rm yadro-2026-part-2
```

Для альтернативного запуска используйте имя контейнера `yadro-2026-part-2-alt`
в командах проверки ниже.

## Проверка через docker logs

```bash
docker logs yadro-2026-part-2
```

Скрипт пишет логи в формате JSON Lines. В успешном запуске должны быть события
для пяти HTTP-запросов и финальное событие `script_completed`.

## Проверка кода завершения

```bash
docker inspect yadro-2026-part-2 --format '{{.State.ExitCode}}'
```

Ожидаемый код завершения: `0`.
