# Medical Image Recognition

医療画像AI認識サービス（FastAPI）。  
`medicalcare-electronic-application` から分離したスタンドアロンパッケージです。

> **Healthcare AI / Medical Imaging Service** — 医療画像を独立したAIサービスとして解析し、ローカルCVとVision AIを切り替えながら、キャッシュ・同時実行制御・性能計測・フォールバックまで扱う推論基盤です。
>
> **Stack:** Python · FastAPI · Computer Vision · OpenAI Vision · Docker · Railway

## Portfolio Overview

| Item | Description |
|---|---|
| **Problem** | 医療画像AIを業務アプリへ直接埋め込むと、推論負荷・AIプロバイダー障害・モデル変更・性能監視が業務処理と密結合する |
| **Solution** | 画像解析を独立FastAPIサービスへ分離し、ローカルCVと外部Vision AIを共通APIの背後で切り替える |
| **Architecture** | Healthcare Application → Medical Imaging API → Provider Router → Local CV / Vision AI → Cache / Metrics |
| **Reliability** | AI未設定・クラウド未接続時のローカルフォールバック、同時実行制御、結果キャッシュ、性能ベンチマーク |
| **Role** | Healthcare AIポートフォリオの **Medical Imaging AI Service Layer** |

## Architecture

```text
Healthcare / Medical Application
             │
             ▼
     Medical Imaging API
          FastAPI
             │
      ┌──────┴──────┐
      ▼             ▼
 Provider Router   Cache
      │
 ┌────┴─────────┐
 ▼              ▼
Local CV     Vision AI
                 │
                 ▼
        Findings / Candidate Regions
                 │
                 ▼
          Metrics / Monitoring
```

## Engineering Differentiators

- **Service isolation** — imaging inference is separated from the healthcare business application so model/runtime changes do not redefine the core application boundary.
- **Provider abstraction** — local computer vision and external Vision AI are selected behind one service interface.
- **Graceful fallback** — the service remains usable through local CV when cloud AI is unavailable or unconfigured.
- **Performance controls** — caching and explicit concurrency limits protect the service from repeated analysis and uncontrolled parallel inference.
- **Benchmarkable runtime** — performance measurement is part of the repository rather than an undocumented assumption.
- **Integration-ready design** — Spring Boot healthcare applications consume the service through a configurable base URL.
- **Clinical boundary** — outputs are positioned as diagnostic-support candidates, not definitive diagnoses.

## Healthcare AI Portfolio Map

| Repository | Primary role |
|---|---|
| [NextGen_AI_Healthcare_Platform](../NextGen_AI_Healthcare_Platform) | Flagship healthcare platform: EMR/PACS, HL7/FHIR, DICOM and AI integration |
| **MedicalImageRecognition** | **Medical Imaging AI Service Layer** |
| [MediCall_AI](../MediCall_AI) | Healthcare Voice AI and appointment/call automation |
| [DisabilityClaim](../DisabilityClaim) | Welfare-service billing and claims workflow |
| [medicalcare-electronic-application](../medicalcare-electronic-application) | Healthcare electronic application/workflow system and imaging integration |

```text
                NextGen Healthcare Platform
                    /        |        \
                   /         |         \
        Medical Imaging   Voice AI   Workflow / Claims
             │               │             │
             ▼               ▼             ▼
MedicalImageRecognition  MediCall_AI  DisabilityClaim
             │
             ▼
medicalcare-electronic-application
       integration consumer
```

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
- **OpenAI Vision**: `AI_OPENAI_API_KEY` 設定時に GPT-4o 等で候補枠・所見を生成（`provider=openai`）
- **結果キャッシュ**: 同一画像の再解析を高速化
- **同時実行制御**: `AI_MAX_CONCURRENT_ANALYSES`
- クラウド未接続時もローカルCVにフォールバック

本結果は診断支援候補であり、確定診断ではありません。

### OpenAI の使い方

Railway では Variables に **`OPENAI_API_KEY`** を設定してください（標準名）。  
`AI_OPENAI_API_KEY` でも可です。

```text
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o          # 任意
```

サービス画面で「OpenAI Vision」を選択するか、`POST /analyze` で `provider=openai` を指定します。  
キー未設定時はローカルCVへフォールバックします。

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