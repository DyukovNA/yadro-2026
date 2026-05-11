# Раздел 1: Работа со скриптом

## Требования

- Python 3.10+.
- Доступ к `https://httpstat.us` или аналогам.

## Запуск

```bash
python3 part-1/http_status_client.py
```

Скрипт отправляет 5 запросов:

- `https://httpstat.us/102`
- `https://httpstat.us/200`
- `https://httpstat.us/302`
- `https://httpstat.us/404`
- `https://httpstat.us/500`

Стандартный шаблон URL: `https://httpstat.us/{status}`. В силу того, что `https://httpstat.us/` может быть недоступен, была добавлена возможность задать URL самостоятельно параметром `HTTP_STATUS_URL_TEMPLATE`:

```bash
HTTP_STATUS_URL_TEMPLATE='https://example.com/status/{status}' python3 part-1/http_status_client.py
```

## Поведение

- Ответы `1xx`, `2xx` и `3xx` логируются как успешные.
- Ответы 4xx и 5xx приводят к созданию исключения внутри скрипта.
- Ожидаемые ошибки отлавливаются для каждого запроса, логируются и не прерывают другие запросы.
- Скрипт завершается с кодом `0` когда все пять запросов обработаны согласно правилам выше.

Заданные запросы `404` и `500` считаются ожидаемыми, однако ошибки сети или парсинга завершают скрипт с кодом `1`.

## Логи

Логи выводятся в формате JSON Lines.

Поля:

- `timestamp`: временная метка, UTC, ISO-8601.
- `level`: уровень логирования, например `INFO` или `ERROR`.
- `event`: тип события, например `request_started`, `request_completed`,
  `request_failed` или `script_completed`.
- `run_id`: ID запуска.
- `request_id`: ID запроса.
- `url`: URL запроса.
- `status_code`: полученный код статуса.
- `status_class`: группа статуса, например `2xx` или `5xx`.
- `duration_ms`: время выполнения запроса.
- `response_body`: тело ответа (когда доступно).
- `error_type` и `error_message`: детали ошибки.

Пример лога:

```json
{"timestamp":"2026-05-12T10:00:00.000Z","level":"INFO","event":"request_completed","run_id":"...","request_id":"...","url":"https://httpstat.us/200","status_code":200,"status_class":"2xx","duration_ms":150,"response_body":"200 OK"}
```
