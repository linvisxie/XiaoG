# Local WP-2 release contract only. Do not publish this image from this window.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    XIAOG_RUNTIME_MODE=preview \
    XIAOG_HOST=0.0.0.0 \
    XIAOG_PORT=8000 \
    XIAOG_DATA_DIR=/var/lib/xiaog-preview \
    XIAOG_LOG_DIR=/var/log/xiaog-preview

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 xiaog \
    && mkdir -p /var/lib/xiaog-preview /var/log/xiaog-preview \
    && chown -R xiaog:xiaog /app /var/lib/xiaog-preview /var/log/xiaog-preview

COPY --chown=xiaog:xiaog . .
USER xiaog

EXPOSE 8000
CMD ["python", "main.py"]
