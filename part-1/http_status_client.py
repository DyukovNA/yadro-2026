#!/usr/bin/env python3
"""HTTP status checker with structured console logging."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib import error, request


DEFAULT_URL_TEMPLATE = "https://httpstat.us/{status}"
URL_TEMPLATE = os.getenv("HTTP_STATUS_URL_TEMPLATE", DEFAULT_URL_TEMPLATE)
STATUSES_TO_CHECK = (102, 200, 302, 404, 500)
TIMEOUT_SECONDS = 10
USER_AGENT = "yadro-2026-http-status-client/1.0"


class HttpStatusError(Exception):
    """Raised for HTTP responses that must be treated as failed requests."""

    def __init__(self, status_code: int, body: str, duration_ms: int) -> None:
        self.status_code = status_code
        self.body = body
        self.duration_ms = duration_ms
        super().__init__(f"HTTP status {status_code} is an error response")


class NoRedirectHandler(request.HTTPRedirectHandler):
    """Keep 3xx responses visible instead of following redirects."""

    def redirect_request(
        self,
        req: request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


@dataclass(frozen=True)
class HttpResult:
    url: str
    status_code: int
    body: str
    duration_ms: int

    @property
    def status_class(self) -> str:
        return f"{self.status_code // 100}xx"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def log_event(level: str, event: str, **fields: Any) -> None:
    record = {
        "timestamp": utc_now(),
        "level": level,
        "event": event,
        **fields,
    }
    print(json.dumps(record, ensure_ascii=False), flush=True)


def decode_body(body: bytes) -> str:
    return body.decode("utf-8", errors="replace")


def build_opener() -> request.OpenerDirector:
    opener = request.build_opener(NoRedirectHandler)
    opener.addheaders = [
        ("User-Agent", USER_AGENT),
        ("Accept", "text/plain, */*"),
    ]
    return opener


def build_url(status_code: int) -> str:
    return URL_TEMPLATE.format(status=status_code)


def fetch_status(opener: request.OpenerDirector, status_code: int) -> HttpResult:
    url = build_url(status_code)
    started = time.monotonic()

    try:
        with opener.open(url, timeout=TIMEOUT_SECONDS) as response:
            body = decode_body(response.read())
            result_status = response.getcode()
    except error.HTTPError as exc:
        body = decode_body(exc.read())
        result_status = exc.code

    duration_ms = round((time.monotonic() - started) * 1000)
    return HttpResult(
        url=url,
        status_code=result_status,
        body=body,
        duration_ms=duration_ms,
    )


def handle_response(result: HttpResult) -> None:
    if 100 <= result.status_code < 400:
        return

    if 400 <= result.status_code < 600:
        raise HttpStatusError(result.status_code, result.body, result.duration_ms)

    raise ValueError(f"Unexpected HTTP status code: {result.status_code}")


def process_status(opener: request.OpenerDirector, run_id: str, status_code: int) -> bool:
    request_id = str(uuid.uuid4())
    url = build_url(status_code)

    log_event(
        "INFO",
        "request_started",
        run_id=run_id,
        request_id=request_id,
        url=url,
        expected_status_code=status_code,
    )

    try:
        result = fetch_status(opener, status_code)
        handle_response(result)
    except HttpStatusError as exc:
        log_event(
            "ERROR",
            "request_failed",
            run_id=run_id,
            request_id=request_id,
            url=url,
            status_code=exc.status_code,
            status_class=f"{exc.status_code // 100}xx",
            duration_ms=exc.duration_ms,
            error_type=exc.__class__.__name__,
            error_message=str(exc),
            response_body=exc.body,
        )
        return True
    except Exception as exc:
        log_event(
            "ERROR",
            "request_unexpected_error",
            run_id=run_id,
            request_id=request_id,
            url=url,
            error_type=exc.__class__.__name__,
            error_message=str(exc),
        )
        return False

    log_event(
        "INFO",
        "request_completed",
        run_id=run_id,
        request_id=request_id,
        url=result.url,
        status_code=result.status_code,
        status_class=result.status_class,
        duration_ms=result.duration_ms,
        response_body=result.body,
    )
    return True


def main() -> int:
    run_id = str(uuid.uuid4())
    opener = build_opener()

    log_event(
        "INFO",
        "script_started",
        run_id=run_id,
        url_template=URL_TEMPLATE,
        request_count=len(STATUSES_TO_CHECK),
    )

    results = []
    for status_code in STATUSES_TO_CHECK:
        results.append(process_status(opener, run_id, status_code))
    exit_code = 0 if all(results) else 1

    log_event(
        "INFO" if exit_code == 0 else "ERROR",
        "script_completed",
        run_id=run_id,
        request_count=len(STATUSES_TO_CHECK),
        handled_count=sum(1 for item in results if item),
        exit_code=exit_code,
    )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
