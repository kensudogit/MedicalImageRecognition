# 画像認識スペック — 実用性能評価と改善

## 評価サマリ（改善前）

| 項目 | 評価 | 問題 |
|------|------|------|
| 検出精度 | 低（デモ） | モダリティ固定のダミー枠。画素を見ていない |
| DICOM前処理 | 中 | Slope/Intercept・MONOCHROME1・リサイズ不足 |
| レイテンシ | モックは速いが無意味 | 実推論なし。キャッシュなし |
| スループット | 低 | 同時実行制御なし、クライアント都度生成 |
| 運用可視性 | 低 | 性能メトリクスなし |

**結論:** 旧実装は「画面デモ」向きで、実用的な診断支援候補抽出としては不十分。

## 改善内容（v1.1）

1. **ローカルCVエンジン**（`local_cv_engine.py`）
   - 画素の局所コントラスト／勾配／色特徴から候補枠を生成
   - モダリティ別ヒューリスティック（X線・CT・MRI・US・内視鏡・病理）
   - NMS・信頼度フィルタ
2. **DICOM前処理強化**
   - RescaleSlope/Intercept、Window、MONOCHROME1反転、中間フレーム選択、thumbnail
3. **結果キャッシュ**
   - ファイルSHA256 + モダリティ + プロバイダーでTTLキャッシュ
4. **同時実行セマフォ**
   - `AI_MAX_CONCURRENT_ANALYSES`（デフォルト4）
5. **性能API**
   - `GET /metrics/performance`

## 目標スペック（ローカルCV）

| 指標 | 目標 | 備考 |
|------|------|------|
| 単枚解析レイテンシ | < 300ms（CPU, 512px級） | OpenCVありでさらに短縮 |
| キャッシュヒット | < 5ms | 同一画像の再解析 |
| 検出 | 画像依存の可変枠 | 固定モックではない |
| 位置づけ | 診断支援候補 | 確定診断ではない |

## 計測

```powershell
cd ai-imaging-service
.\.venv\Scripts\python -m app.benchmark_performance
```

実測例（OpenCVあり・384px解析・サンプル6種×5回）:

| 指標 | 値 |
|------|-----|
| 平均レイテンシ | ~15ms |
| p50 | ~14ms |
| 最大 | ~35ms |
| 判定 | PASS（目標 <500ms） |

または:

```text
GET /metrics/performance
```

## 環境変数

| 変数 | デフォルト | 意味 |
|------|-----------|------|
| `AI_USE_LOCAL_CV` | true | ローカルCV使用 |
| `AI_FORCE_LOCAL_CV` | false | リモートよりローカル優先 |
| `AI_CACHE_ENABLED` | true | 結果キャッシュ |
| `AI_CACHE_TTL_SECONDS` | 3600 | TTL |
| `AI_MAX_CONCURRENT_ANALYSES` | 4 | 同時解析数 |
| `AI_PREVIEW_MAX_SIZE` | 1024 | プレビュー最大辺 |
