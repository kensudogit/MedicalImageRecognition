# Medical Image Recognition

医療画像AI認識サービス（FastAPI）。  
`medicalcare-electronic-application` から分離したスタンドアロンパッケージです。

## 構成

```
MedicalImageRecognition/
└── ai-imaging-service/     # FastAPI (port 8090)
    ├── app/
    ├── Dockerfile
    ├── requirements.txt
    └── .env.example
```

## 起動（ローカル）

Python **3.11 または 3.12** を使用（3.14 不可）。

```powershell
cd C:\devlop\MedicalImageRecognition\ai-imaging-service
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8090
```

- トップ: http://127.0.0.1:8090/
- **サービス画面**: http://127.0.0.1:8090/service （サンプル画像ギャラリー付き）
- サンプル一覧 API: http://127.0.0.1:8090/api/samples
- Health: http://127.0.0.1:8090/health
- 性能: http://127.0.0.1:8090/metrics/performance
- Docs: http://127.0.0.1:8090/docs

サンプル再生成:

```powershell
.\.venv\Scripts\python -m app.generate_samples
```

実用性能ベンチマーク:

```powershell
.\.venv\Scripts\python -m app.benchmark_performance
```

詳細は [PERFORMANCE.md](./PERFORMANCE.md) を参照。

## 実用エンジン（v1.1）

- **ローカルCV**（デフォルト）: 画素コントラストから病変候補枠を生成（固定モックではない）
- **結果キャッシュ**: 同一画像の再解析を高速化
- **同時実行制御**: `AI_MAX_CONCURRENT_ANALYSES`
- クラウド未接続時もローカルCVにフォールバック

本結果は診断支援候補であり、確定診断ではありません。

## medicalcare との連携

Spring Boot は `ai.imaging.base-url: http://localhost:8090` で本サービスを呼び出します。

Docker Compose（medicalcare 側）では build context を次のように参照しています。

```yaml
context: ../MedicalImageRecognition/ai-imaging-service
```

## Railway デプロイ

ルートに `Dockerfile` と `railway.json` があります。再デプロイは git push 後に自動、または Railway ダッシュボードから Redeploy。

## 単体 Docker 起動

```powershell
cd C:\devlop\MedicalImageRecognition
docker compose up -d --build
```
