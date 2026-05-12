FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY part-1/http_status_client.py /app/http_status_client.py

CMD ["python3", "/app/http_status_client.py"]
