FROM python:3.12 AS builder

RUN pip install --upgrade pip uv

WORKDIR /app

COPY README.md /app/
COPY pyproject.toml /app/
COPY uv.lock /app/
COPY src /app/src

RUN uv build


FROM python:3.12 AS runtime

WORKDIR  /app

COPY --from=builder /app/dist/*.whl /app/

RUN pip install --no-cache-dir ./*.whl

CMD ["annomemo"]