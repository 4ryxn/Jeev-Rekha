FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system jeevrekha && adduser --system --ingroup jeevrekha --home /app jeevrekha

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic ./alembic
COPY alembic.ini ./
COPY app ./app

USER jeevrekha

EXPOSE 8000

# Schema releases and optional synthetic seeding are explicit release operations,
# never container-start side effects.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
