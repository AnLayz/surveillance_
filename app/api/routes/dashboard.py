from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])

_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Survivalence — Панель управления</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f0f13;
      color: #e8e8f0;
      min-height: 100vh;
      padding: 24px 16px 48px;
    }

    /* ── Header ── */
    header {
      display: flex;
      align-items: center;
      gap: 14px;
      max-width: 900px;
      margin: 0 auto 32px;
    }
    .logo {
      width: 44px; height: 44px;
      background: #e53935;
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px;
      flex-shrink: 0;
    }
    header h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }
    header p  { font-size: 13px; color: #888; margin-top: 2px; }

    .status-pill {
      margin-left: auto;
      display: flex; align-items: center; gap: 8px;
      background: #1c1c24;
      border: 1px solid #2a2a36;
      border-radius: 999px;
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 500;
      white-space: nowrap;
    }
    .dot {
      width: 9px; height: 9px;
      border-radius: 50%;
      background: #555;
      transition: background 0.4s;
    }
    .dot.online  { background: #4caf50; box-shadow: 0 0 6px #4caf5088; }
    .dot.offline { background: #e53935; }

    /* ── Grid ── */
    .grid {
      max-width: 900px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    @media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }

    /* ── Card ── */
    .card {
      background: #16161e;
      border: 1px solid #2a2a36;
      border-radius: 16px;
      padding: 22px 24px;
    }
    .card.full { grid-column: 1 / -1; }
    .card-title {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: #666;
      margin-bottom: 16px;
    }

    /* ── Stream card ── */
    .stream-card {
      grid-column: 1 / -1;
      background: linear-gradient(135deg, #1a1a24, #1e1422);
      border-color: #3a2a3a;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
    }
    .stream-info h2 { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
    .stream-info p  { font-size: 14px; color: #999; line-height: 1.5; }
    .btn-watch {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: #e53935;
      color: #fff;
      text-decoration: none;
      font-size: 15px;
      font-weight: 600;
      padding: 13px 28px;
      border-radius: 12px;
      transition: background 0.2s, transform 0.1s;
      white-space: nowrap;
      flex-shrink: 0;
    }
    .btn-watch:hover  { background: #c62828; }
    .btn-watch:active { transform: scale(0.97); }

    /* ── Stats ── */
    .stats-row {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }
    .stat-box {
      background: #0f0f13;
      border-radius: 12px;
      padding: 16px 12px;
      text-align: center;
    }
    .stat-value {
      font-size: 32px;
      font-weight: 800;
      color: #fff;
      line-height: 1;
      margin-bottom: 6px;
      font-variant-numeric: tabular-nums;
    }
    .stat-value.red   { color: #e53935; }
    .stat-value.green { color: #4caf50; }
    .stat-label { font-size: 12px; color: #666; }

    /* ── Alerts list ── */
    .alert-list { display: flex; flex-direction: column; gap: 10px; }
    .alert-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      background: #0f0f13;
      border-radius: 10px;
      padding: 12px 14px;
      animation: fadeIn 0.3s ease;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; } }
    .alert-icon {
      font-size: 18px;
      flex-shrink: 0;
      margin-top: 1px;
    }
    .alert-msg  { font-size: 14px; color: #ddd; line-height: 1.4; }
    .alert-time { font-size: 12px; color: #555; margin-top: 3px; }
    .no-alerts  { font-size: 14px; color: #555; text-align: center; padding: 20px 0; }

    /* ── Refresh hint ── */
    .refresh-hint {
      font-size: 11px;
      color: #444;
      margin-top: 14px;
      text-align: right;
    }

    /* ── Zone info card ── */
    .zone-diagram {
      display: flex;
      gap: 12px;
      align-items: stretch;
      margin-bottom: 14px;
    }
    .zone-half {
      flex: 1;
      border-radius: 8px;
      height: 72px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
    }
    .zone-safe {
      background: #1a2a1a;
      border: 1px solid #2a4a2a;
      color: #4caf50;
    }
    .zone-restricted {
      background: #2a1a1a;
      border: 2px solid #e5393566;
      color: #e53935;
    }
    .zone-legend { display: flex; flex-direction: column; gap: 6px; }
    .legend-row  {
      display: flex; align-items: center; gap: 8px;
      font-size: 13px; color: #aaa;
    }
    .legend-dot {
      width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
    }

    /* ── Telegram card ── */
    .tg-row { display: flex; align-items: center; gap: 12px; }
    .tg-icon {
      width: 42px; height: 42px; border-radius: 50%;
      background: #229ED9;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px; flex-shrink: 0;
    }
    .tg-text h3 { font-size: 15px; font-weight: 600; margin-bottom: 3px; }
    .tg-text p  { font-size: 13px; color: #777; line-height: 1.4; }

    /* ── Help section ── */
    .help-list { display: flex; flex-direction: column; gap: 12px; }
    .help-item { display: flex; gap: 12px; align-items: flex-start; }
    .help-num {
      width: 26px; height: 26px; border-radius: 50%;
      background: #2a2a36;
      display: flex; align-items: center; justify-content: center;
      font-size: 12px; font-weight: 700;
      flex-shrink: 0; color: #aaa;
    }
    .help-text h4 { font-size: 14px; font-weight: 600; margin-bottom: 2px; }
    .help-text p  { font-size: 13px; color: #777; line-height: 1.4; }
  </style>
</head>
<body>

<header>
  <div class="logo">&#128249;</div>
  <div>
    <h1>Survivalence</h1>
    <p>Система видеонаблюдения</p>
  </div>
  <div class="status-pill">
    <div class="dot" id="statusDot"></div>
    <span id="statusText">Проверка...</span>
  </div>
</header>

<div class="grid">

  <!-- ── Прямой эфир ── -->
  <div class="card stream-card">
    <div class="stream-info">
      <h2>&#127909; Прямой эфир</h2>
      <p>Видео с камеры в реальном времени.<br>
         Объекты выделены рамками, запрещённая зона помечена красным.</p>
    </div>
    <a class="btn-watch" href="/api/v1/stream/" target="_blank">
      &#9654; Смотреть
    </a>
  </div>

  <!-- ── Статистика ── -->
  <div class="card">
    <div class="card-title">Статистика</div>
    <div class="stats-row">
      <div class="stat-box">
        <div class="stat-value" id="statDetections">—</div>
        <div class="stat-label">Кадров записано</div>
      </div>
      <div class="stat-box">
        <div class="stat-value red" id="statAlerts">—</div>
        <div class="stat-label">Нарушений зоны</div>
      </div>
      <div class="stat-box">
        <div class="stat-value green" id="statActive">—</div>
        <div class="stat-label">Объектов сейчас</div>
      </div>
    </div>
    <div class="refresh-hint" id="statsAge"></div>
  </div>

  <!-- ── Зона ── -->
  <div class="card">
    <div class="card-title">Запрещённая зона</div>
    <div class="zone-diagram">
      <div class="zone-half zone-safe">Свободная<br>зона</div>
      <div class="zone-half zone-restricted">&#128683; Запрещено</div>
    </div>
    <div class="zone-legend">
      <div class="legend-row">
        <div class="legend-dot" style="background:#e53935;"></div>
        Правая половина экрана — запрещённая зона
      </div>
      <div class="legend-row">
        <div class="legend-dot" style="background:#4caf50;"></div>
        Зелёная рамка — обнаруженный объект
      </div>
      <div class="legend-row">
        <div class="legend-dot" style="background:#ff5252;"></div>
        Красная рамка — объект нарушает зону
      </div>
    </div>
  </div>

  <!-- ── Последние алерты ── -->
  <div class="card full">
    <div class="card-title">Последние нарушения</div>
    <div class="alert-list" id="alertList">
      <div class="no-alerts">Загрузка...</div>
    </div>
    <div class="refresh-hint" id="alertsAge"></div>
  </div>

  <!-- ── Telegram ── -->
  <div class="card">
    <div class="card-title">Уведомления</div>
    <div class="tg-row">
      <div class="tg-icon">&#9992;</div>
      <div class="tg-text">
        <h3>Telegram-бот</h3>
        <p>При каждом нарушении вы получаете сообщение в Telegram.<br>
           Повторный алерт — не чаще одного раза в 30 секунд.</p>
      </div>
    </div>
  </div>

  <!-- ── Как пользоваться ── -->
  <div class="card">
    <div class="card-title">Как пользоваться</div>
    <div class="help-list">
      <div class="help-item">
        <div class="help-num">1</div>
        <div class="help-text">
          <h4>Запустите сервер</h4>
          <p>Откройте терминал и запустите систему. Статус вверху страницы станет зелёным.</p>
        </div>
      </div>
      <div class="help-item">
        <div class="help-num">2</div>
        <div class="help-text">
          <h4>Откройте прямой эфир</h4>
          <p>Нажмите кнопку «Смотреть» — откроется окно с камерой.</p>
        </div>
      </div>
      <div class="help-item">
        <div class="help-num">3</div>
        <div class="help-text">
          <h4>Следите за нарушениями</h4>
          <p>Как только кто-то войдёт в правую часть экрана — придёт уведомление в Telegram.</p>
        </div>
      </div>
    </div>
  </div>

</div><!-- /grid -->

<script>
  // ── Утилиты ──────────────────────────────────────────────────────────
  function timeAgo(isoStr) {
    const sec = Math.round((Date.now() - new Date(isoStr).getTime()) / 1000);
    if (sec < 5)  return "только что";
    if (sec < 60) return sec + " сек назад";
    const min = Math.round(sec / 60);
    if (min < 60) return min + " мин назад";
    return Math.round(min / 60) + " ч назад";
  }

  function formatTime(isoStr) {
    const d = new Date(isoStr);
    return d.toLocaleDateString("ru-RU") + " " +
           d.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function translateMessage(msg) {
    return msg
      .replace(/Person/gi, "Человек")
      .replace(/Car/gi, "Машина")
      .replace(/Truck/gi, "Грузовик")
      .replace(/entered restricted zone/gi, "вошёл в запрещённую зону");
  }

  // ── Статус сервера ────────────────────────────────────────────────────
  async function checkStatus() {
    const dot  = document.getElementById("statusDot");
    const text = document.getElementById("statusText");
    try {
      const r = await fetch("/health", { cache: "no-store" });
      if (r.ok) {
        dot.className  = "dot online";
        text.textContent = "Система работает";
      } else throw new Error();
    } catch {
      dot.className  = "dot offline";
      text.textContent = "Нет соединения";
    }
  }

  // ── Статистика ────────────────────────────────────────────────────────
  async function loadStats() {
    try {
      const r = await fetch("/api/v1/stats/", { cache: "no-store" });
      if (!r.ok) return;
      const d = await r.json();
      document.getElementById("statDetections").textContent = d.total_detections ?? "—";
      document.getElementById("statAlerts").textContent     = d.total_alerts ?? "—";
      document.getElementById("statActive").textContent     = d.active_tracked_objects ?? "—";
      document.getElementById("statsAge").textContent = "Обновлено " + new Date().toLocaleTimeString("ru-RU");
    } catch {}
  }

  // ── Алерты ───────────────────────────────────────────────────────────
  async function loadAlerts() {
    try {
      const r = await fetch("/api/v1/alerts/?limit=8", { cache: "no-store" });
      if (!r.ok) return;
      const data = await r.json();
      const list = document.getElementById("alertList");

      if (!data.alerts || data.alerts.length === 0) {
        list.innerHTML = '<div class="no-alerts">Нарушений пока не зафиксировано</div>';
        return;
      }

      list.innerHTML = data.alerts.map(a => `
        <div class="alert-item">
          <div class="alert-icon">&#128680;</div>
          <div>
            <div class="alert-msg">${translateMessage(a.message)}</div>
            <div class="alert-time">${formatTime(a.triggered_at)}</div>
          </div>
        </div>
      `).join("");

      document.getElementById("alertsAge").textContent =
        "Обновлено " + new Date().toLocaleTimeString("ru-RU");
    } catch {}
  }

  // ── Запуск ────────────────────────────────────────────────────────────
  checkStatus();
  loadStats();
  loadAlerts();

  setInterval(checkStatus, 10000);
  setInterval(loadStats,   5000);
  setInterval(loadAlerts,  8000);
</script>
</body>
</html>"""


@router.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    return HTMLResponse(content=_HTML)
