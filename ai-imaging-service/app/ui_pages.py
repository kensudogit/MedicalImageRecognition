"""サービス画面（ブラウザUI）の HTML"""

from app.config import settings


def landing_page_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{settings.app_name}</title>
  <link rel="icon" href="/favicon.ico" />
  <style>
    :root {{ color-scheme: light; }}
    body {{
      margin: 0; font-family: "Segoe UI", "Hiragino Sans", Meiryo, sans-serif;
      background: linear-gradient(160deg, #f0fdfa 0%, #e2e8f0 100%);
      color: #0f172a; min-height: 100vh;
    }}
    main {{ max-width: 720px; margin: 0 auto; padding: 3rem 1.25rem; }}
    h1 {{ font-size: 1.75rem; margin: 0 0 0.5rem; }}
    .badge {{
      display: inline-block; background: #134e4a; color: #ccfbf1;
      font-size: 0.75rem; padding: 0.25rem 0.6rem; border-radius: 999px;
    }}
    p {{ color: #334155; line-height: 1.6; }}
    .warn {{
      background: #fffbeb; border: 1px solid #f59e0b; border-radius: 8px;
      padding: 0.75rem 1rem; font-size: 0.875rem; color: #78350f; margin: 1rem 0;
    }}
    .primary {{
      display: block; text-align: center; text-decoration: none;
      background: #0f766e; color: #fff; font-weight: 600; font-size: 1.05rem;
      border-radius: 12px; padding: 1.1rem 1.25rem; margin: 1.25rem 0 1.5rem;
      box-shadow: 0 8px 20px rgba(15,118,110,.25);
    }}
    .primary:hover {{ background: #115e59; }}
    .primary small {{ display: block; font-weight: 400; opacity: .9; margin-top: .35rem; font-size: .85rem; }}
    ul {{ list-style: none; padding: 0; display: grid; gap: 0.75rem; margin: 0; }}
    a.card {{
      display: block; text-decoration: none; color: inherit;
      background: white; border: 1px solid #cbd5e1; border-radius: 10px;
      padding: 1rem 1.25rem;
    }}
    a.card:hover {{ border-color: #0f766e; box-shadow: 0 4px 14px rgba(15,118,110,.12); }}
    a.card strong {{ color: #0f766e; }}
    code {{ background: #f1f5f9; padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.85em; }}
    h2 {{ font-size: .95rem; color: #64748b; margin: 1.5rem 0 .75rem; font-weight: 600; }}
  </style>
</head>
<body>
  <main>
    <span class="badge">v{settings.app_version}</span>
    <h1>{settings.app_name}</h1>
    <p>医療画像認識 AI サービス（X線 / CT / MRI / 超音波 / 内視鏡 / 病理 / DICOM）</p>
    <div class="warn">本サービスは診断支援用途です。AI出力は確定診断ではありません。</div>

    <a class="primary" href="/service">
      サービス画面を開く
      <small>画像アップロード・病変候補検出・所見表示 · 利用手順パレット付き</small>
    </a>

    <h2>開発・管理</h2>
    <ul>
      <li><a class="card" href="/docs"><strong>Swagger UI</strong><br />API ドキュメント・試行</a></li>
      <li><a class="card" href="/redoc"><strong>ReDoc</strong><br />API リファレンス</a></li>
      <li><a class="card" href="/health"><strong>Health</strong><br /><code>GET /health</code></a></li>
      <li><a class="card" href="/providers"><strong>Providers</strong><br /><code>GET /providers</code></a></li>
    </ul>
  </main>
</body>
</html>"""


def service_page_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>サービス画面 | {settings.app_name}</title>
  <link rel="icon" href="/favicon.ico" />
  <style>
    :root {{ color-scheme: light; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: "Segoe UI", "Hiragino Sans", Meiryo, sans-serif;
      background: linear-gradient(160deg, #ecfdf5 0%, #e2e8f0 55%, #f8fafc 100%);
      color: #0f172a; min-height: 100vh;
    }}
    header {{
      background: #134e4a; color: #fff; padding: 1rem 1.25rem;
      display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;
    }}
    header a {{ color: #99f6e4; text-decoration: none; font-size: .9rem; }}
    header h1 {{ margin: 0; font-size: 1.2rem; font-weight: 600; }}
    header .sub {{ opacity: .85; font-size: .75rem; margin-top: .2rem; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 1.25rem; display: grid; gap: 1rem; }}
    @media (min-width: 900px) {{
      .wrap {{ grid-template-columns: 340px 1fr; align-items: start; }}
    }}
    .panel {{
      background: #fff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 1rem 1.1rem;
      box-shadow: 0 2px 10px rgba(15,23,42,.04);
    }}
    .warn {{
      background: #fffbeb; border: 1px solid #f59e0b; border-radius: 8px;
      padding: .75rem 1rem; font-size: .85rem; color: #78350f; grid-column: 1 / -1;
    }}
    label {{ display: block; font-size: .85rem; font-weight: 600; margin: .75rem 0 .35rem; }}
    input[type=file], select, textarea, input[type=text] {{
      width: 100%; border: 1px solid #cbd5e1; border-radius: 8px; padding: .55rem .7rem; font: inherit;
      background: #fff;
    }}
    textarea {{ min-height: 64px; resize: vertical; }}
    button#run, button.secondary {{
      width: 100%; margin-top: .9rem; border: 0; border-radius: 8px; padding: .75rem 1rem;
      background: #0f766e; color: #fff; font-weight: 600; font-size: .95rem; cursor: pointer;
    }}
    button#run:hover, button.secondary:hover {{ background: #115e59; }}
    button:disabled {{ opacity: .55; cursor: not-allowed; }}
    .viewer {{
      position: relative; display: inline-block; max-width: 100%; background: #000; border-radius: 8px; overflow: hidden;
    }}
    .viewer img {{ display: block; max-width: 100%; max-height: 70vh; }}
    .viewer canvas {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; pointer-events: none; }}
    .muted {{ color: #64748b; font-size: .85rem; }}
    .status {{ margin-top: .75rem; font-size: .85rem; padding: .6rem .75rem; border-radius: 8px; display: none; }}
    .status.ok {{ display: block; background: #ecfdf5; color: #065f46; }}
    .status.err {{ display: block; background: #fef2f2; color: #991b1b; }}
    .findings {{
      white-space: pre-wrap; background: #fff7ed; border: 1px solid #fdba74; border-radius: 8px;
      padding: .85rem 1rem; font-size: .9rem; line-height: 1.55; margin-top: .75rem;
    }}
    .tag {{
      display: inline-block; background: #134e4a; color: #ccfbf1; font-size: .7rem;
      padding: .15rem .5rem; border-radius: 999px; margin-right: .35rem;
    }}
    .boxes {{ list-style: none; padding: 0; margin: .75rem 0 0; display: grid; gap: .4rem; }}
    .boxes li {{
      border: 1px solid #e2e8f0; border-radius: 8px; padding: .5rem .7rem; font-size: .85rem;
      display: flex; justify-content: space-between; gap: .5rem;
    }}
    .empty {{
      min-height: 240px; display: flex; align-items: center; justify-content: center;
      color: #94a3b8; background: #f1f5f9; border-radius: 8px;
    }}
    .samples {{
      display: grid; grid-template-columns: repeat(3, 1fr); gap: .5rem; margin-top: .5rem;
    }}
    .sample {{
      border: 2px solid #e2e8f0; border-radius: 8px; overflow: hidden; cursor: pointer;
      background: #0f172a; padding: 0; text-align: left; width: 100%; margin: 0;
    }}
    .sample:hover, .sample.active {{ border-color: #0f766e; box-shadow: 0 0 0 2px rgba(15,118,110,.25); }}
    .sample img {{ display: block; width: 100%; height: 72px; object-fit: cover; }}
    .sample span {{
      display: block; font-size: .68rem; padding: .3rem .35rem; color: #334155; background: #f8fafc;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .selected-file {{ font-size: .8rem; color: #0f766e; margin-top: .4rem; min-height: 1.2em; }}
    .hdr-actions {{ display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; }}
    .btn-guide {{
      border: 1px solid #5eead4; background: rgba(255,255,255,.12); color: #fff;
      border-radius: 8px; padding: .45rem .85rem; font: inherit; font-size: .85rem;
      font-weight: 600; cursor: pointer;
    }}
    .btn-guide:hover {{ background: rgba(255,255,255,.22); }}

    /* 利用手順モーダル（参照パレットと同系デザイン） */
    .guide-backdrop {{
      position: fixed; inset: 0; z-index: 40; pointer-events: none;
    }}
    .guide-modal {{
      --g-teal: #0f766e;
      --g-teal-mid: #5ba8a0;
      --g-teal-border: #9fd4ce;
      --g-card-bg: #f3faf9;
      --g-ink: #1a2332;
      --g-muted: #6b7c8a;
      position: fixed; z-index: 50; top: 72px; right: 24px; width: min(420px, calc(100vw - 24px));
      max-height: min(78vh, 720px); display: flex; flex-direction: column;
      background: #fff; border: 1px solid var(--g-teal-border); border-radius: 14px;
      box-shadow: 0 18px 48px rgba(15, 118, 110, .18), 0 2px 8px rgba(15, 23, 42, .08);
      overflow: hidden; pointer-events: auto;
      font-family: "Segoe UI", "Hiragino Sans", "Noto Sans JP", Meiryo, sans-serif;
    }}
    .guide-modal.collapsed .guide-body {{ display: none; }}
    .guide-modal.hidden {{ display: none; }}
    .guide-head {{
      display: grid; grid-template-columns: 1fr auto 1fr; align-items: center;
      gap: .5rem; padding: .85rem 1rem .75rem; border-bottom: 2px solid var(--g-teal-mid);
      background: #fff; cursor: grab; user-select: none; touch-action: none;
    }}
    .guide-head:active {{ cursor: grabbing; }}
    .guide-head-left {{ display: flex; align-items: flex-start; gap: .55rem; min-width: 0; }}
    .guide-burger {{
      width: 18px; height: 14px; margin-top: .35rem; flex-shrink: 0;
      background:
        linear-gradient(var(--g-ink), var(--g-ink)) 0 0 / 100% 2px no-repeat,
        linear-gradient(var(--g-ink), var(--g-ink)) 0 6px / 100% 2px no-repeat,
        linear-gradient(var(--g-ink), var(--g-ink)) 0 12px / 100% 2px no-repeat;
    }}
    .guide-title {{ margin: 0; font-size: 1.15rem; font-weight: 700; color: var(--g-ink); line-height: 1.2; }}
    .guide-sub {{ margin: .15rem 0 0; font-size: .65rem; letter-spacing: .06em; color: var(--g-muted); font-weight: 600; }}
    .guide-drag-hint {{
      justify-self: center; font-size: .72rem; color: var(--g-teal); font-weight: 600; white-space: nowrap;
    }}
    .guide-head-right {{ justify-self: end; display: flex; gap: .35rem; }}
    .guide-icon-btn {{
      width: 28px; height: 28px; border-radius: 999px; border: 1px solid #d8e8e6;
      background: #f4fafa; color: #64748b; cursor: pointer; display: grid; place-items: center;
      font-size: .7rem; line-height: 1; padding: 0;
    }}
    .guide-icon-btn:hover {{ background: #e6f5f3; color: var(--g-teal); }}
    .guide-body {{
      overflow: auto; padding: .9rem 1rem 1.1rem; display: grid; gap: .85rem;
      background: linear-gradient(180deg, #fbfdfe 0%, #f7fbfb 100%);
    }}
    .guide-card {{
      background: var(--g-card-bg); border: 1px solid var(--g-teal-border);
      border-radius: 12px; padding: 1rem 1.05rem;
    }}
    .guide-kicker {{
      margin: 0 0 .35rem; font-size: .68rem; font-weight: 700; letter-spacing: .08em;
      color: var(--g-teal); text-transform: uppercase;
    }}
    .guide-card h3 {{
      margin: 0 0 .55rem; font-size: 1.05rem; font-weight: 700; color: var(--g-ink); line-height: 1.35;
    }}
    .guide-card p {{ margin: 0; font-size: .84rem; line-height: 1.65; color: #334155; }}
    .guide-pills {{ display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .75rem; }}
    .guide-pill {{
      display: inline-block; background: #fff; border: 1px solid var(--g-teal-border);
      color: #0f4c48; border-radius: 999px; padding: .22rem .65rem; font-size: .72rem; font-weight: 600;
    }}
    .guide-row {{ display: flex; align-items: center; gap: .55rem; flex-wrap: wrap; margin-bottom: .55rem; }}
    .guide-badge {{
      display: inline-block; background: var(--g-teal); color: #fff; font-size: .65rem;
      font-weight: 700; letter-spacing: .04em; padding: .28rem .55rem; border-radius: 6px;
    }}
    .guide-row-title {{ font-size: .95rem; font-weight: 700; color: var(--g-ink); }}
    .guide-card ul {{
      margin: .65rem 0 0; padding: 0 0 0 1.1rem; color: #334155; font-size: .84rem; line-height: 1.7;
    }}
    .guide-card li {{ margin: .2rem 0; }}
    .guide-card li::marker {{ color: var(--g-teal-mid); }}
    .guide-card code {{
      font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
      font-size: .8em; background: #fff; border: 1px solid #d5e8e5; border-radius: 4px;
      padding: .05rem .3rem; color: #0f4c48;
    }}
    .guide-warn-inline {{
      margin-top: .7rem; padding: .55rem .7rem; border-radius: 8px;
      background: #fffbeb; border: 1px solid #fcd34d; color: #78350f; font-size: .8rem; line-height: 1.5;
    }}
    @media (max-width: 640px) {{
      .guide-modal {{ top: auto; bottom: 12px; right: 12px; left: 12px; width: auto; max-height: 70vh; }}
      .guide-drag-hint {{ display: none; }}
      .guide-head {{ grid-template-columns: 1fr auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>医療画像AI サービス画面</h1>
      <div class="sub">診断支援候補の表示 — 確定診断ではありません</div>
    </div>
    <div class="hdr-actions">
      <button type="button" class="btn-guide" id="openGuide" aria-haspopup="dialog">利用手順</button>
      <a href="/">← トップに戻る</a>
    </div>
  </header>

  <div id="guideModal" class="guide-modal" role="dialog" aria-labelledby="guideTitle" aria-modal="false">
    <div class="guide-head" id="guideDragHandle" title="ドラッグで移動">
      <div class="guide-head-left">
        <span class="guide-burger" aria-hidden="true"></span>
        <div>
          <h2 class="guide-title" id="guideTitle">利用手順</h2>
          <p class="guide-sub">ARCHITECTURE &amp; OPS</p>
        </div>
      </div>
      <span class="guide-drag-hint">ドラッグで移動</span>
      <div class="guide-head-right">
        <button type="button" class="guide-icon-btn" id="guideCollapse" title="折りたたむ" aria-label="折りたたむ">▼</button>
        <button type="button" class="guide-icon-btn" id="guideClose" title="閉じる" aria-label="閉じる">✕</button>
      </div>
    </div>
    <div class="guide-body" id="guideBody">
      <article class="guide-card">
        <p class="guide-kicker">PORTFOLIO-READY DEMO</p>
        <h3>Medical Imaging AI → 候補検出</h3>
        <p>
          サンプル画像または DICOM / 一般画像をアップロードし、ローカルCV（または接続済みクラウド）で
          病変候補枠・分類・所見文を生成します。医師確認前提の診断支援デモです。
        </p>
        <div class="guide-pills">
          <span class="guide-pill">FastAPI · Python</span>
          <span class="guide-pill">Local CV</span>
          <span class="guide-pill">DICOM</span>
          <span class="guide-pill">OpenCV</span>
          <span class="guide-pill">Cache</span>
          <span class="guide-pill">マルチプロバイダー</span>
        </div>
      </article>

      <article class="guide-card">
        <div class="guide-row">
          <span class="guide-badge">ARCHITECTURE</span>
          <span class="guide-row-title">エンドツーエンド・パイプライン</span>
        </div>
        <p>
          画像受付 → DICOM/プレビュー前処理 → プロバイダー推論（既定: ローカルCV）→
          結果キャッシュ → バウンディングボックス / 所見表示。
          性能は <code>GET /metrics/performance</code> で確認できます。
        </p>
      </article>

      <article class="guide-card">
        <div class="guide-row">
          <span class="guide-badge">RECOMMENDED</span>
          <span class="guide-row-title">最短・安全な進め方</span>
        </div>
        <p>サービス画面での推奨フローです。</p>
        <ul>
          <li>ギャラリーからサンプルを選ぶ（またはファイルを選択）</li>
          <li>モダリティを確認（空欄なら自動判定）</li>
          <li>画像認識サービスはまず <code>自社AIモデル</code>（ローカルCV）</li>
          <li><strong>解析を実行</strong> → 枠・所見を確認</li>
          <li>同一画像の再実行はキャッシュで高速化されます</li>
        </ul>
        <div class="guide-warn-inline">
          AI出力は確定診断ではありません。誤検出・見逃しを前提に、必ず原画像を医師が確認してください。
        </div>
      </article>

      <article class="guide-card">
        <div class="guide-row">
          <span class="guide-badge">OPS</span>
          <span class="guide-row-title">起動・計測・API</span>
        </div>
        <ul>
          <li>起動: <code>uvicorn app.main:app --port 8090</code></li>
          <li>画面: <code>/service</code> · API: <code>POST /analyze</code></li>
          <li>性能ベンチ: <code>python -m app.benchmark_performance</code></li>
          <li>クラウド未接続時もローカルCVにフォールバック</li>
        </ul>
      </article>
    </div>
  </div>

  <div class="wrap">
    <div class="warn">
      <strong>重要:</strong> 本画面の AI 出力は診断支援候補です。誤検出・見逃しを前提に、必ず医師が原画像を確認してください。
      サンプル画像はデモ用の合成画像です。
    </div>

    <aside class="panel">
      <h2 style="margin:0 0 .5rem;font-size:1rem;">解析設定</h2>

      <label>サンプル画像（クリックで選択・表示）</label>
      <div id="samples" class="samples"><span class="muted">読み込み中…</span></div>
      <div id="selectedLabel" class="selected-file"></div>

      <label for="file">またはファイルを選択</label>
      <input id="file" type="file" accept=".dcm,.dicom,image/*,.png,.jpg,.jpeg,.bmp,.tif,.tiff,.webp" />

      <label for="modality">モダリティ</label>
      <select id="modality">
        <option value="">自動判定</option>
        <option value="XRAY">X線</option>
        <option value="CT">CT</option>
        <option value="MRI">MRI</option>
        <option value="ULTRASOUND">超音波</option>
        <option value="ENDOSCOPY">内視鏡</option>
        <option value="PATHOLOGY">病理</option>
        <option value="DICOM">DICOM</option>
        <option value="OTHER">その他</option>
      </select>

      <label for="provider">画像認識サービス</label>
      <select id="provider">
        <option value="inhouse">自社AIモデル</option>
        <option value="sagemaker">AWS SageMaker</option>
        <option value="azure">Azure AI</option>
        <option value="google">Google Cloud</option>
        <option value="external">外部医療AI API</option>
      </select>

      <label for="context">臨床情報（任意）</label>
      <textarea id="context" placeholder="例: 発熱・咳嗽あり"></textarea>

      <button id="run" type="button">解析を実行</button>
      <div id="status" class="status"></div>
      <p class="muted" style="margin-top:.85rem;">API: <code>POST /analyze</code> · 一覧: <code>GET /api/samples</code></p>
    </aside>

    <section class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:.5rem;flex-wrap:wrap;">
        <h2 style="margin:0;font-size:1rem;">画像プレビュー / 解析結果</h2>
        <span id="meta" class="muted"></span>
      </div>
      <div id="empty" class="empty">サンプル画像をクリックするか、ファイルを選択してください</div>
      <div id="viewerWrap" class="viewer" style="display:none;margin-top:.75rem;">
        <img id="preview" alt="preview" />
        <canvas id="overlay"></canvas>
      </div>
      <div id="resultBlock" style="display:none;margin-top:1rem;">
        <span class="tag">NOT A DIAGNOSIS</span>
        <span id="providerTag" class="tag"></span>
        <div id="findings" class="findings"></div>
        <ul id="boxes" class="boxes"></ul>
      </div>
    </section>
  </div>

  <script>
    const fileInput = document.getElementById('file');
    const runBtn = document.getElementById('run');
    const statusEl = document.getElementById('status');
    const preview = document.getElementById('preview');
    const canvas = document.getElementById('overlay');
    const viewerWrap = document.getElementById('viewerWrap');
    const empty = document.getElementById('empty');
    const resultBlock = document.getElementById('resultBlock');
    const findingsEl = document.getElementById('findings');
    const boxesEl = document.getElementById('boxes');
    const metaEl = document.getElementById('meta');
    const providerTag = document.getElementById('providerTag');
    const samplesEl = document.getElementById('samples');
    const selectedLabel = document.getElementById('selectedLabel');
    const modalityEl = document.getElementById('modality');

    let currentBoxes = [];
    let selectedSample = null; // {{ url, filename, modality, title }}
    let selectedFile = null;

    function setStatus(msg, ok) {{
      statusEl.textContent = msg;
      statusEl.className = 'status ' + (ok ? 'ok' : 'err');
    }}

    function showImage(url, label) {{
      empty.style.display = 'none';
      viewerWrap.style.display = 'inline-block';
      resultBlock.style.display = 'none';
      currentBoxes = [];
      preview.src = url + (url.includes('?') ? '&' : '?') + 't=' + Date.now();
      selectedLabel.textContent = label || '';
      metaEl.textContent = label || '';
    }}

    function drawBoxes() {{
      const ctx = canvas.getContext('2d');
      const w = preview.clientWidth;
      const h = preview.clientHeight;
      if (!w || !h) return;
      canvas.width = w;
      canvas.height = h;
      ctx.clearRect(0, 0, w, h);
      const colors = ['#14b8a6', '#f59e0b', '#ef4444', '#3b82f6', '#a855f7'];
      currentBoxes.forEach((b, i) => {{
        const color = colors[i % colors.length];
        const x = b.x * w, y = b.y * h, bw = b.width * w, bh = b.height * h;
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, bw, bh);
        const label = `${{b.label}} ${{Math.round((b.confidence || 0) * 100)}}%`;
        ctx.font = '12px sans-serif';
        const tw = ctx.measureText(label).width;
        ctx.fillStyle = color;
        ctx.fillRect(x, Math.max(0, y - 18), tw + 8, 18);
        ctx.fillStyle = '#fff';
        ctx.fillText(label, x + 4, Math.max(12, y - 5));
      }});
    }}

    preview.addEventListener('load', drawBoxes);
    window.addEventListener('resize', drawBoxes);

    async function loadSamples() {{
      try {{
        const res = await fetch('/api/samples');
        const data = await res.json();
        samplesEl.innerHTML = '';
        (data.samples || []).forEach(s => {{
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'sample';
          btn.title = s.title;
          btn.innerHTML = `<img src="${{s.url}}" alt="${{s.title}}" /><span>${{s.title}}</span>`;
          btn.addEventListener('click', () => {{
            document.querySelectorAll('.sample').forEach(el => el.classList.remove('active'));
            btn.classList.add('active');
            selectedSample = s;
            selectedFile = null;
            fileInput.value = '';
            modalityEl.value = s.modality || '';
            showImage(s.url, s.title + ' / ' + s.modality);
            setStatus('サンプル「' + s.title + '」を表示中。解析を実行できます。', true);
          }});
          samplesEl.appendChild(btn);
        }});
        if (!(data.samples || []).length) {{
          samplesEl.innerHTML = '<span class="muted">サンプルがありません</span>';
        }}
      }} catch (e) {{
        samplesEl.innerHTML = '<span class="muted">サンプル読込失敗</span>';
      }}
    }}

    fileInput.addEventListener('change', () => {{
      const file = fileInput.files && fileInput.files[0];
      if (!file) return;
      selectedFile = file;
      selectedSample = null;
      document.querySelectorAll('.sample').forEach(el => el.classList.remove('active'));
      showImage(URL.createObjectURL(file), file.name);
      setStatus('ファイル「' + file.name + '」を表示中。解析を実行できます。', true);
    }});

    async function resolveFileForAnalyze() {{
      if (selectedFile) return selectedFile;
      if (selectedSample) {{
        const res = await fetch(selectedSample.url);
        const blob = await res.blob();
        return new File([blob], selectedSample.filename, {{ type: blob.type || 'image/png' }});
      }}
      return null;
    }}

    runBtn.addEventListener('click', async () => {{
      const file = await resolveFileForAnalyze();
      if (!file) {{
        setStatus('サンプル画像またはファイルを選択してください', false);
        return;
      }}
      runBtn.disabled = true;
      setStatus('解析中…', true);

      const form = new FormData();
      form.append('file', file);
      const modality = modalityEl.value;
      const provider = document.getElementById('provider').value;
      const context = document.getElementById('context').value;
      if (modality) form.append('modality', modality);
      if (provider) form.append('provider', provider);
      form.append('generate_findings', 'true');
      if (context) form.append('patient_context', context);

      try {{
        const res = await fetch('/analyze', {{ method: 'POST', body: form }});
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || JSON.stringify(data));

        currentBoxes = data.boxes || [];
        const previewUrl = (data.raw && data.raw.preview_url) ? data.raw.preview_url : null;

        empty.style.display = 'none';
        viewerWrap.style.display = 'inline-block';
        resultBlock.style.display = 'block';

        if (previewUrl) {{
          preview.src = previewUrl + '?t=' + Date.now();
        }} else if (selectedSample) {{
          preview.src = selectedSample.url + '?t=' + Date.now();
        }} else {{
          preview.src = URL.createObjectURL(file);
        }}

        findingsEl.textContent = data.findings_text || '（所見なし）';
        providerTag.textContent = data.provider || provider;
        metaEl.textContent = `${{data.modality || ''}} · ${{data.model_version || ''}} · ${{data.processing_ms || 0}} ms${{(data.raw && data.raw.cache_hit) ? ' · cache' : ''}}`;

        boxesEl.innerHTML = '';
        (data.classifications || []).forEach(c => {{
          const li = document.createElement('li');
          li.innerHTML = `<span>${{c.label}}${{c.category ? ' <small class="muted">' + c.category + '</small>' : ''}}</span><span>${{Math.round((c.confidence||0)*1000)/10}}%</span>`;
          boxesEl.appendChild(li);
        }});
        currentBoxes.forEach(b => {{
          const li = document.createElement('li');
          li.innerHTML = `<span>枠: ${{b.label}}</span><span>${{Math.round((b.confidence||0)*100)}}%</span>`;
          boxesEl.appendChild(li);
        }});

        setStatus('解析完了（診断支援候補・確定診断ではありません）', true);
        setTimeout(drawBoxes, 50);
      }} catch (e) {{
        setStatus('解析失敗: ' + (e.message || e), false);
      }} finally {{
        runBtn.disabled = false;
      }}
    }});

    loadSamples();

    /* 利用手順モーダル: 開閉・折りたたみ・ドラッグ */
    (function () {{
      const modal = document.getElementById('guideModal');
      const handle = document.getElementById('guideDragHandle');
      const collapseBtn = document.getElementById('guideCollapse');
      const closeBtn = document.getElementById('guideClose');
      const openBtn = document.getElementById('openGuide');
      if (!modal || !handle) return;

      let dragging = false;
      let ox = 0, oy = 0;

      function placeDefault() {{
        modal.style.left = '';
        modal.style.top = '';
        modal.style.right = '24px';
        modal.style.bottom = '';
      }}

      openBtn.addEventListener('click', () => {{
        modal.classList.remove('hidden', 'collapsed');
        collapseBtn.textContent = '▼';
        placeDefault();
      }});
      closeBtn.addEventListener('click', (e) => {{
        e.stopPropagation();
        modal.classList.add('hidden');
      }});
      collapseBtn.addEventListener('click', (e) => {{
        e.stopPropagation();
        modal.classList.toggle('collapsed');
        collapseBtn.textContent = modal.classList.contains('collapsed') ? '▲' : '▼';
      }});

      handle.addEventListener('pointerdown', (e) => {{
        if (e.target.closest('button')) return;
        dragging = true;
        const rect = modal.getBoundingClientRect();
        ox = e.clientX - rect.left;
        oy = e.clientY - rect.top;
        modal.style.right = 'auto';
        modal.style.left = rect.left + 'px';
        modal.style.top = rect.top + 'px';
        handle.setPointerCapture(e.pointerId);
      }});
      handle.addEventListener('pointermove', (e) => {{
        if (!dragging) return;
        const x = Math.min(window.innerWidth - 80, Math.max(8, e.clientX - ox));
        const y = Math.min(window.innerHeight - 48, Math.max(8, e.clientY - oy));
        modal.style.left = x + 'px';
        modal.style.top = y + 'px';
      }});
      handle.addEventListener('pointerup', () => {{ dragging = false; }});
      handle.addEventListener('pointercancel', () => {{ dragging = false; }});
    }})();
  </script>
</body>
</html>"""
