const $ = id => document.getElementById(id);

// ============================================================
// CONFIGURE AQUI: cole a URL do seu backend no Render
// Exemplo: "https://plux-api.onrender.com"
// ============================================================
const API_URL = "https://plux-uubb.onrender.com";
// ============================================================

let currentPlatform = 'youtube';
let currentMode = 'video';
let history = JSON.parse(localStorage.getItem('dl_history') || '[]');
let stats = JSON.parse(localStorage.getItem('dl_stats') || '{"total":0,"youtube":0,"tiktok":0,"instagram":0}');

const placeholders = {
  youtube:   'https://www.youtube.com/watch?v=...',
  tiktok:    'https://www.tiktok.com/@user/video/...',
  instagram: 'https://www.instagram.com/reel/... ou /stories/...',
};

const gradients = {
  youtube:   'linear-gradient(90deg, #ff0044, #ff4488, #ff0044)',
  tiktok:    'linear-gradient(90deg, #00f2ea, #69f0ae, #00f2ea)',
  instagram: 'linear-gradient(90deg, #e1306c, #fd1d1d, #f77737, #e1306c)',
};

const btnClasses  = { youtube: 'btn-yt', tiktok: 'btn-tt', instagram: 'btn-ig' };
const fillClasses = { youtube: 'fill-youtube', tiktok: 'fill-tiktok', instagram: 'fill-instagram' };
const tabKeys     = { youtube: 'yt', tiktok: 'tt', instagram: 'ig' };
const typeLabels  = { story: 'Story', reel: 'Reel', post: 'Post' };

const downloadIcon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
  <polyline points="7 10 12 15 17 10"/>
  <line x1="12" y1="15" x2="12" y2="3"/>
</svg>`;

const audioIcon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M9 18V5l12-2v13"/>
  <circle cx="6" cy="18" r="3"/>
  <circle cx="18" cy="16" r="3"/>
</svg>`;

const videoQualityOptions = [
  { value: 'best', label: 'Melhor disponível' },
  { value: '2160', label: '4K (2160p)' },
  { value: '1080', label: 'Full HD (1080p)' },
  { value: '720',  label: 'HD (720p)' },
  { value: '480',  label: 'Média (480p)' },
  { value: '360',  label: 'Baixa (360p)' },
];

const audioQualityOptions = [
  { value: 'best', label: 'Melhor disponível' },
  { value: '320', label: 'Alta (320kbps)' },
  { value: '192', label: 'Média (192kbps)' },
  { value: '128', label: 'Baixa (128kbps)' },
];

function setMode(mode) {
  currentMode = mode;
  $('modeVideo').classList.toggle('active', mode === 'video');
  $('modeAudio').classList.toggle('active', mode === 'audio');

  const select = $('quality');
  const options = mode === 'audio' ? audioQualityOptions : videoQualityOptions;
  select.innerHTML = '';
  options.forEach((opt, i) => {
    const el = document.createElement('option');
    el.value = opt.value;
    el.textContent = opt.label;
    if (i === 0) el.selected = true;
    select.appendChild(el);
  });

  const btn = $('btnDownload');
  if (mode === 'audio') {
    btn.innerHTML = audioIcon + ' Baixar MP3';
  } else {
    btn.innerHTML = downloadIcon + ' Baixar vídeo';
  }
}

// --- Platform ---
function selectPlatform(platform) {
  currentPlatform = platform;
  document.querySelectorAll('.platform-tab').forEach(t => t.classList.remove('active'));
  document.querySelector('.tab-' + tabKeys[platform]).classList.add('active');
  $('url').placeholder = placeholders[platform];
  $('btnDownload').className = 'btn ' + (btnClasses[platform] || '');
  document.querySelector('.container').style.setProperty('--accent-gradient', gradients[platform]);
}

function detectPlatform(url) {
  if (url.includes('tiktok.com')) return 'tiktok';
  if (url.includes('instagram.com')) return 'instagram';
  return 'youtube';
}

// --- Formatters ---
function formatDuration(s) {
  if (!s) return '';
  const m = Math.floor(s / 60), sec = s % 60;
  return `${m}:${String(sec).padStart(2, '0')}`;
}

function formatViews(n) {
  if (!n) return '';
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M views';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K views';
  return n + ' views';
}

function formatTime(date) {
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function setStatus(text, type = '') {
  $('status').textContent = text;
  $('status').className = 'status ' + type;
}

function resetBtn() {
  const btn = $('btnDownload');
  btn.disabled = false;
  if (currentMode === 'audio') {
    btn.innerHTML = audioIcon + ' Baixar MP3';
  } else {
    btn.innerHTML = downloadIcon + ' Baixar vídeo';
  }
}

// --- Paste ---
async function colarURL() {
  try {
    const text = await navigator.clipboard.readText();
    $('url').value = text;
    $('url').dispatchEvent(new Event('input'));
    const btn = $('pasteBtn');
    btn.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Colado!`;
    setTimeout(() => {
      btn.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Colar`;
    }, 1500);
  } catch {
    setStatus('Permissão de colar negada', 'error');
  }
}

// --- Quality ---
function updateQualityOptions(resolutions) {
  if (currentMode === 'audio') return;
  const select = $('quality');
  const current = select.value;
  select.innerHTML = '';
  videoQualityOptions.forEach(opt => {
    const el = document.createElement('option');
    el.value = opt.value;
    if (opt.value === 'best') {
      el.textContent = opt.label;
    } else {
      const available = resolutions.includes(parseInt(opt.value));
      el.textContent = opt.label + (available ? '  ✓' : '');
    }
    if (opt.value === current) el.selected = true;
    select.appendChild(el);
  });
}

// --- Stats ---
function updateStats() {
  $('statTotal').textContent = stats.total;
  $('statYt').textContent = stats.youtube;
  $('statTt').textContent = stats.tiktok;
  $('statIg').textContent = stats.instagram;
}

function incrementStats(platform) {
  stats.total++;
  stats[platform] = (stats[platform] || 0) + 1;
  localStorage.setItem('dl_stats', JSON.stringify(stats));
  updateStats();
}

// --- History ---
function addToHistory(item) {
  history.unshift(item);
  if (history.length > 20) history.pop();
  localStorage.setItem('dl_history', JSON.stringify(history));
  renderHistory();
}

function limparHistorico() {
  history = [];
  stats = { total: 0, youtube: 0, tiktok: 0, instagram: 0 };
  localStorage.setItem('dl_history', JSON.stringify(history));
  localStorage.setItem('dl_stats', JSON.stringify(stats));
  renderHistory();
  updateStats();
}

function renderHistory() {
  const list = $('historyList');
  if (history.length === 0) {
    list.innerHTML = `
      <div class="empty-history">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <div>Nenhum download ainda</div>
      </div>`;
    return;
  }
  list.innerHTML = history.map(h => `
    <div class="history-item">
      ${h.thumbnail ? `<img src="${h.thumbnail}" alt="">` : ''}
      <div class="history-info">
        <div class="history-title">${h.title}</div>
        <div class="history-meta">
          <span class="platform-badge badge-${h.platform}" style="font-size:9px;padding:1px 5px">${h.platform}</span>
          ${h.quality ? h.quality : ''}
          ${h.time ? '&bull; ' + h.time : ''}
        </div>
      </div>
      <div class="history-check">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
    </div>
  `).join('');
}

// --- Download ---
function montarLinkArquivo(url, quality, mode, index) {
  const p = new URLSearchParams({ url, quality, mode });
  if (index) p.set('index', index);
  return API_URL + '/api/file?' + p.toString();
}

// Usa um iframe escondido: o servidor responde com Content-Disposition:
// attachment, então o navegador salva o arquivo sem sair da página.
function triggerDownload(url) {
  const f = document.createElement('iframe');
  f.style.display = 'none';
  f.src = url;
  document.body.appendChild(f);
  setTimeout(() => f.remove(), 10 * 60 * 1000);
}

let lastVideoInfo = null;

async function iniciar() {
  const url = $('url').value.trim();
  if (!url) { setStatus('Cole uma URL primeiro!', 'error'); return; }

  const detected = detectPlatform(url);
  if (detected !== currentPlatform) selectPlatform(detected);

  const btn = $('btnDownload');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Buscando info...';
  $('videoCard').classList.remove('show');
  $('progressArea').classList.remove('show');
  $('typeBadge').style.display = 'none';
  $('countInfo').style.display = 'none';
  setStatus('');

  try {
    // 1. Buscar info do vídeo
    const infoRes = await fetch(API_URL + '/api/info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    const info = await infoRes.json();

    if (info.error) {
      setStatus(info.error, 'error');
      resetBtn();
      return;
    }

    lastVideoInfo = info;
    const platform = info.platform || detected;
    if (platform !== currentPlatform) selectPlatform(platform);

    if (info.resolutions && info.resolutions.length > 0) {
      updateQualityOptions(info.resolutions);
    }

    $('thumb').src = info.thumbnail || '';
    $('thumb').style.display = info.thumbnail ? '' : 'none';
    $('videoTitle').textContent = info.title;

    const badge = $('platformBadge');
    badge.textContent = platform;
    badge.className = 'platform-badge badge-' + platform;

    const typeBadge = $('typeBadge');
    if (info.type && platform === 'instagram') {
      typeBadge.textContent = typeLabels[info.type] || info.type;
      typeBadge.className = 'platform-badge badge-' + info.type;
      typeBadge.style.display = '';
    } else {
      typeBadge.style.display = 'none';
    }

    const countInfo = $('countInfo');
    if (info.count > 1) {
      $('countText').textContent = `${info.count} itens serão baixados`;
      countInfo.style.display = '';
    } else {
      countInfo.style.display = 'none';
    }

    const metaParts = [info.channel, formatDuration(info.duration), formatViews(info.views)].filter(Boolean);
    $('videoMeta').textContent = metaParts.join('  •  ');
    $('videoCard').classList.add('show');

    // 2. Validar o link antes de baixar
    const quality = $('quality').value;
    btn.innerHTML = '<span class="spinner"></span> Preparando...';
    setStatus('Preparando download...', 'loading');

    const dlRes = await fetch(API_URL + '/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, quality, mode: currentMode }),
    });
    const dlData = await dlRes.json();

    if (dlData.error) {
      setStatus(dlData.error, 'error');
      resetBtn();
      return;
    }

    // 3. O servidor baixa e devolve o arquivo pronto
    if (dlData.links && dlData.links.length > 0) {
      dlData.links.forEach((link, i) => {
        setTimeout(
          () => triggerDownload(montarLinkArquivo(url, quality, currentMode, link.index)),
          i * 1000
        );
      });

      let qualityLabel;
      if (currentMode === 'audio') {
        qualityLabel = quality === 'best' ? 'MP3' : 'MP3 ' + quality + 'kbps';
      } else {
        qualityLabel = quality === 'best' ? 'Melhor' : quality + 'p';
      }
      incrementStats(platform);
      addToHistory({
        title: info.title,
        thumbnail: info.thumbnail || '',
        platform,
        quality: qualityLabel,
        time: formatTime(new Date()),
      });

      const count = dlData.links.length;
      setStatus(
        count > 1
          ? `${count} downloads iniciados! O servidor está processando, aguarde.`
          : 'Download iniciado! O servidor está processando, aguarde.',
        'success'
      );
    } else {
      setStatus('Nenhum link de download encontrado', 'error');
    }

    resetBtn();
  } catch (err) {
    setStatus('Erro de conexão com o servidor', 'error');
    resetBtn();
  }
}

// --- Events ---
$('url').addEventListener('input', () => {
  const v = $('url').value.trim();
  if (v.length > 10) {
    const d = detectPlatform(v);
    if (d !== currentPlatform) selectPlatform(d);
  }
});

$('url').addEventListener('keydown', e => { if (e.key === 'Enter') iniciar(); });

// --- Gif loop ---
function loopGif() {
  const gif = document.querySelector('.logo-gif');
  if (!gif) return;
  const src = gif.getAttribute('src').split('?')[0];
  setInterval(() => { gif.src = src + '?t=' + Date.now(); }, 3000);
}

// --- Init ---
selectPlatform('youtube');
updateStats();
renderHistory();
loopGif();
