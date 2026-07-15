FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /app/uploads/ai-imaging/previews

ENV AI_UPLOAD_DIR=/app/uploads/ai-imaging
ENV AI_PREVIEW_DIR=/app/uploads/ai-imaging/previews
ENV AI_ENABLE_MOCK_INFERENCE=true
ENV AI_DEFAULT_PROVIDER=inhouse

EXPOSE 8090

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8090/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
