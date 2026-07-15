# MedicalImageRecognition — Railway / Docker 用ルート Dockerfile
# ビルドコンテキストはリポジトリルート想定

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY ai-imaging-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ai-imaging-service/app ./app

RUN mkdir -p /app/uploads/ai-imaging/previews \
    && python -m app.generate_samples || true

ENV AI_UPLOAD_DIR=/app/uploads/ai-imaging
ENV AI_PREVIEW_DIR=/app/uploads/ai-imaging/previews
ENV AI_ENABLE_MOCK_INFERENCE=true
ENV AI_DEFAULT_PROVIDER=inhouse

# Railway は PORT を注入する（未設定時は 8090）
ENV PORT=8090
EXPOSE 8090

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8090}/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8090}"]
