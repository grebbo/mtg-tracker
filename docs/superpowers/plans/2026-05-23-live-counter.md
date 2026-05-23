# Live Counter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere una pagina `/live` con life counter fullscreen per partite di Commander, con persistenza in localStorage e handoff pre-compilato a `/game/new`.

**Architecture:** Pagina Flask `GET /live` che renderizza `live.html`; tutta la logica di gioco è client-side JS con stato in `localStorage`. Al termine della partita, lo stato viene serializzato in `sessionStorage` e il redirect a `/game/new` legge il prefill automaticamente.

**Tech Stack:** Flask/Jinja2, Tailwind CSS (CDN già presente), vanilla JS, localStorage/sessionStorage, Web Fullscreen API.

---

## File map

| File | Operazione | Responsabilità |
|---|---|---|
| `app/routes.py` | Modifica | Aggiunta route `GET /live` |
| `app/templates/base.html` | Modifica | Link "Live" nella navbar |
| `app/templates/live.html` | Crea | Setup screen + play screen + tutta la logica JS |
| `app/templates/game_form.html` | Modifica | Lettura `sessionStorage['mtg_prefill']` per pre-fill |

---

## Task 1: Route `/live` e link navbar

**Files:**
- Modify: `app/routes.py`
- Modify: `app/templates/base.html`

- [ ] **Step 1: Aggiungere la route in routes.py**

In `app/routes.py`, dopo la route `dashboard`, aggiungere:

```python
@main.route('/live')
def live():
    players = Player.query.order_by(Player.name).all()
    commanders = Commander.query.order_by(Commander.name).all()
    players_json = [{'id': p.id, 'name': p.name} for p in players]
    commanders_json = [{'id': c.id, 'name': c.name, 'color_identity': c.color_identity} for c in commanders]
    return render_template('live.html', players_json=players_json, commanders_json=commanders_json)
```

- [ ] **Step 2: Aggiungere "Live" nella navbar di base.html**

In `app/templates/base.html`, nella riga dei link navbar (attorno alla riga 79), aggiungere dopo il link "+ Partita":

```html
<a href="/live" class="nav-link {% if request.endpoint == 'main.live' %}active{% endif %}">Live</a>
```

- [ ] **Step 3: Verificare**

Avviare l'app (`python run.py`) e visitare `http://localhost:5000/live` — deve rispondere 200 con template non trovato (normale, il template non esiste ancora). Il link "Live" deve apparire in navbar.

- [ ] **Step 4: Commit**

```bash
git add app/routes.py app/templates/base.html
git commit -m "feat: aggiungi route /live e link navbar"
```

---

## Task 2: `live.html` — scheletro e setup screen

**Files:**
- Create: `app/templates/live.html`

- [ ] **Step 1: Creare il file con setup screen**

```html
{% extends "base.html" %}
{% block title %}Live Counter{% endblock %}

{% block extra_head %}
<style>
  /* ── fullscreen play mode ─────────────────────── */
  body.live-play nav,
  body.live-play footer,
  body.live-play > main > *:not(#live-play) { display: none !important; }
  body.live-play main { padding: 0 !important; max-width: none !important; }

  /* ── setup screen ─────────────────────────────── */
  #live-setup { max-width: 32rem; margin: 0 auto; }
  .seat-slot { background: #1a1d27; border: 1px solid #2d3147; border-radius: 0.75rem; padding: 1rem; margin-bottom: 0.75rem; }
  .seat-slot.hidden { display: none; }

  /* ── play screen ──────────────────────────────── */
  #live-play { display: none; position: fixed; inset: 0; background: #000; overflow: hidden; touch-action: none; }
  #play-grid { position: absolute; inset: 0; display: grid; gap: 2px; background: #111; }

  /* ── tile ─────────────────────────────────────── */
  .tile { position: relative; overflow: hidden; background: #0a0a0a; cursor: pointer; user-select: none; }
  .tile.eliminated { opacity: 0.35; }
  .tile.sorteggio-highlight { background: #3b0764; }
  .tile-inner { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
  .tile-content { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; }
  .tile-hp {
    font-size: clamp(2.5rem, 10vw, 5.5rem);
    font-weight: 900;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    color: #f1f5f9;
    transition: color 0.2s;
  }
  .tile.eliminated .tile-hp { color: #475569; }
  .tile-name { font-size: clamp(0.55rem, 2vw, 0.85rem); color: #64748b; margin-top: 0.35rem; letter-spacing: 0.05em; text-transform: uppercase; }
  .tile-corner { position: absolute; top: 0.4rem; left: 0.4rem; display: flex; gap: 0.35rem; z-index: 10; }
  .tile-corner button {
    background: transparent; border: none; font-size: clamp(0.75rem, 2.5vw, 1rem);
    cursor: pointer; opacity: 0.4; padding: 0.2rem; line-height: 1;
  }
  .tile-corner button.sol-active { opacity: 1; }
  .tile-corner button:hover { opacity: 0.9; }
  .tile-elim-overlay {
    display: none; position: absolute; inset: 0;
    align-items: center; justify-content: center;
    font-size: clamp(1.5rem, 6vw, 3rem); color: #475569;
    background: rgba(0,0,0,0.3);
  }
  .tile.eliminated .tile-elim-overlay { display: flex; }
  /* hp flash on change */
  @keyframes hp-flash { 0%,100%{opacity:1} 50%{opacity:0.4} }
  .hp-flash { animation: hp-flash 0.18s ease; }

  /* ── turn center ──────────────────────────────── */
  #turn-center {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    z-index: 50; display: flex; align-items: center; gap: 0.5rem;
    background: rgba(0,0,0,0.75); border-radius: 1rem;
    padding: 0.4rem 0.75rem; backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.08);
  }
  .turn-btn {
    background: transparent; border: none; color: #94a3b8;
    font-size: 1.3rem; cursor: pointer; padding: 0 0.2rem; line-height: 1;
  }
  .turn-btn:hover { color: #e2e8f0; }
  #turn-num {
    font-size: 1.6rem; font-weight: 900; min-width: 2.5rem;
    text-align: center; color: #f1f5f9; cursor: pointer;
    border-radius: 0.4rem; padding: 0 0.2rem;
  }
  #turn-num[contenteditable="true"] { background: #1e293b; outline: none; }
  #end-game-btn {
    display: none; position: absolute; top: calc(100% + 0.5rem);
    left: 50%; transform: translateX(-50%);
    white-space: nowrap; background: #7f1d1d; color: #fca5a5;
    border: none; padding: 0.4rem 1rem; border-radius: 0.5rem;
    font-size: 0.78rem; cursor: pointer; font-weight: 600;
  }
  #end-game-btn:hover { background: #991b1b; }

  /* ── edit modal ───────────────────────────────── */
  #edit-modal {
    display: none; position: fixed; inset: 0; z-index: 100;
    background: rgba(0,0,0,0.85); align-items: center; justify-content: center;
  }
  #edit-modal.open { display: flex; }
  #edit-modal-inner {
    background: #1a1d27; border: 1px solid #2d3147; border-radius: 1rem;
    padding: 1.5rem; width: min(90vw, 20rem); display: flex; flex-direction: column; gap: 1rem;
  }

  /* ── auto-end overlay ─────────────────────────── */
  #end-overlay {
    display: none; position: fixed; inset: 0; z-index: 100;
    background: rgba(0,0,0,0.88); align-items: center;
    justify-content: center; flex-direction: column; gap: 1.25rem;
    text-align: center; padding: 2rem;
  }
  #end-overlay.open { display: flex; }
  #end-overlay-msg { font-size: 1.1rem; color: #e2e8f0; font-weight: 600; }

  /* ── hp input overlay ─────────────────────────── */
  #hp-input-overlay {
    display: none; position: fixed; inset: 0; z-index: 100;
    background: rgba(0,0,0,0.88); align-items: center; justify-content: center;
  }
  #hp-input-overlay.open { display: flex; }
  #hp-input-inner {
    background: #1a1d27; border: 1px solid #2d3147; border-radius: 1rem;
    padding: 1.5rem; width: min(90vw, 16rem); display: flex; flex-direction: column; gap: 1rem; align-items: center;
  }
  #hp-input-field { font-size: 2rem; text-align: center; width: 100%; }
</style>
{% endblock %}

{% block content %}

<!-- ══ SETUP SCREEN ══════════════════════════════════════════ -->
<div id="live-setup">
  <h1 class="text-xl font-bold text-white mb-6">⚔️ Nuova Partita Live</h1>

  <!-- Player count -->
  <div class="card p-4 mb-4">
    <label class="mb-2">Numero di giocatori</label>
    <div class="flex gap-2">
      {% for n in [2,3,4,5,6] %}
      <button type="button"
              class="count-btn btn-sm px-3 py-1.5 font-bold {% if n == 4 %}ring-2 ring-mtg-accent{% endif %}"
              data-count="{{ n }}">{{ n }}</button>
      {% endfor %}
    </div>
  </div>

  <!-- Seat slots -->
  <div id="seat-slots" class="mb-4">
    {% for i in range(6) %}
    <div class="seat-slot {% if i >= 4 %}hidden{% endif %}" data-seat="{{ i }}">
      <div class="text-xs text-slate-500 mb-2 font-medium">Posto {{ i + 1 }}</div>
      <div class="flex gap-2">
        <select class="seat-player flex-1" data-seat="{{ i }}">
          <option value="">— Giocatore —</option>
        </select>
        <select class="seat-commander flex-1" data-seat="{{ i }}">
          <option value="">— Commander —</option>
        </select>
      </div>
    </div>
    {% endfor %}
  </div>

  <!-- resume banner (shown if saved game exists) -->
  <div id="resume-banner" class="hidden card p-4 mb-4" style="border-color:#f59e0b">
    <p class="text-amber-300 text-sm mb-2">⚠ C'è una partita in corso non terminata.</p>
    <div class="flex gap-2">
      <button id="resume-btn" class="btn-primary text-sm">Riprendi</button>
      <button id="discard-btn" class="btn-sm text-sm">Scarta</button>
    </div>
  </div>

  <button id="start-btn" class="btn-primary w-full py-3 text-base font-bold opacity-50 cursor-not-allowed" disabled>
    Inizia Partita
  </button>
</div>

<!-- ══ PLAY SCREEN ═══════════════════════════════════════════ -->
<div id="live-play">
  <div id="play-grid"></div>

  <!-- Turn center -->
  <div id="turn-center">
    <button class="turn-btn" id="turn-minus">−</button>
    <span id="turn-num" title="Premi a lungo per terminare">1</span>
    <button class="turn-btn" id="turn-plus">+</button>
    <button id="end-game-btn">Termina partita</button>
  </div>

  <!-- Edit modal -->
  <div id="edit-modal">
    <div id="edit-modal-inner">
      <h3 class="text-white font-semibold">Modifica posizione</h3>
      <div>
        <label>Giocatore</label>
        <select id="edit-player-sel"></select>
      </div>
      <div>
        <label>Commander</label>
        <select id="edit-commander-sel"></select>
      </div>
      <div class="flex gap-2">
        <button id="edit-confirm" class="btn-primary flex-1">Conferma</button>
        <button id="edit-cancel" class="btn-sm flex-1">Annulla</button>
      </div>
    </div>
  </div>

  <!-- Auto-end overlay -->
  <div id="end-overlay">
    <p id="end-overlay-msg"></p>
    <div class="flex gap-3">
      <button id="end-overlay-confirm" class="btn-primary px-6 py-2">Conferma</button>
      <button id="end-overlay-ignore" class="btn-sm px-6 py-2">Ignora</button>
    </div>
  </div>

  <!-- HP free-input overlay -->
  <div id="hp-input-overlay">
    <div id="hp-input-inner">
      <label class="text-slate-300">Punti vita</label>
      <input id="hp-input-field" type="number" class="text-center" min="-999" max="999">
      <div class="flex gap-2 w-full">
        <button id="hp-input-confirm" class="btn-primary flex-1">OK</button>
        <button id="hp-input-cancel" class="btn-sm flex-1">Annulla</button>
      </div>
    </div>
  </div>
</div>

<script>
const PLAYERS    = {{ players_json | tojson }};
const COMMANDERS = {{ commanders_json | tojson }};
const STATE_KEY  = 'mtg_live_game';

// ── State helpers ──────────────────────────────────────────────
function getState() {
  try { return JSON.parse(localStorage.getItem(STATE_KEY)); } catch { return null; }
}
function saveState(s) { localStorage.setItem(STATE_KEY, JSON.stringify(s)); }
function clearState() { localStorage.removeItem(STATE_KEY); }

function makeInitialState(playerCount, slots) {
  return {
    phase: 'play',
    playerCount,
    slots,               // [{playerId,playerName,commanderId,commanderName,hp,solRing,eliminated,turnEliminated}]
    currentTurn: 1,
    firstPlayerIndex: null,
    startedAt: new Date().toISOString().slice(0, 10),
  };
}
</script>
{% endblock %}
```

- [ ] **Step 2: Verificare che la pagina si carichi**

Visitare `http://localhost:5000/live`. Deve mostrare la setup screen con i slot giocatori.

- [ ] **Step 3: Commit**

```bash
git add app/templates/live.html
git commit -m "feat: aggiungi live.html scheletro setup screen"
```

---

## Task 3: Setup screen — JS interattivo

**Files:**
- Modify: `app/templates/live.html` (aggiungere nel blocco `<script>` esistente)

- [ ] **Step 1: Aggiungere JS setup nel blocco script di live.html**

Aggiungere dopo la funzione `makeInitialState`:

```javascript
// ── Setup screen ───────────────────────────────────────────────
let selectedCount = 4;

function esc(s) {
  return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function playerOptions(selId) {
  return '<option value="">— Giocatore —</option>' +
    PLAYERS.map(p => `<option value="${p.id}" ${p.id==selId?'selected':''}>${esc(p.name)}</option>`).join('');
}

function commanderOptions(selId) {
  return '<option value="">— Commander —</option>' +
    COMMANDERS.map(c => `<option value="${c.id}" ${c.id==selId?'selected':''}>${esc(c.name)} (${esc(c.color_identity)})</option>`).join('');
}

function initSetupSlots(count) {
  selectedCount = count;
  document.querySelectorAll('.count-btn').forEach(btn => {
    btn.classList.toggle('ring-2', parseInt(btn.dataset.count) === count);
    btn.classList.toggle('ring-mtg-accent', parseInt(btn.dataset.count) === count);
  });
  document.querySelectorAll('.seat-slot').forEach((slot, i) => {
    slot.classList.toggle('hidden', i >= count);
  });
  // Populate selects once
  document.querySelectorAll('.seat-player').forEach(sel => {
    if (!sel.innerHTML.includes('option value="')) sel.innerHTML = playerOptions(null);
  });
  document.querySelectorAll('.seat-commander').forEach(sel => {
    if (!sel.innerHTML.includes('option value="')) sel.innerHTML = commanderOptions(null);
  });
  validateSetup();
}

function validateSetup() {
  const slots = Array.from(document.querySelectorAll('.seat-slot')).slice(0, selectedCount);
  const allFilled = slots.every(slot => {
    const p = slot.querySelector('.seat-player').value;
    const c = slot.querySelector('.seat-commander').value;
    return p && c;
  });
  const btn = document.getElementById('start-btn');
  btn.disabled = !allFilled;
  btn.classList.toggle('opacity-50', !allFilled);
  btn.classList.toggle('cursor-not-allowed', !allFilled);
}

document.querySelectorAll('.count-btn').forEach(btn => {
  btn.addEventListener('click', () => initSetupSlots(parseInt(btn.dataset.count)));
});
document.querySelectorAll('.seat-player, .seat-commander').forEach(sel => {
  sel.addEventListener('change', validateSetup);
});

// Resume banner
const saved = getState();
if (saved && saved.phase === 'play') {
  document.getElementById('resume-banner').classList.remove('hidden');
}
document.getElementById('resume-btn')?.addEventListener('click', () => {
  enterPlay(getState());
});
document.getElementById('discard-btn')?.addEventListener('click', () => {
  clearState();
  document.getElementById('resume-banner').classList.add('hidden');
});

// Start button
document.getElementById('start-btn').addEventListener('click', () => {
  const slots = Array.from(document.querySelectorAll('.seat-slot'))
    .slice(0, selectedCount)
    .map(slot => {
      const pId = parseInt(slot.querySelector('.seat-player').value);
      const cId = parseInt(slot.querySelector('.seat-commander').value);
      const player = PLAYERS.find(p => p.id === pId);
      const commander = COMMANDERS.find(c => c.id === cId);
      return {
        playerId: pId,
        playerName: player?.name ?? '',
        commanderId: cId,
        commanderName: commander?.name ?? '',
        hp: 40,
        solRing: false,
        eliminated: false,
        turnEliminated: null,
      };
    });
  const state = makeInitialState(selectedCount, slots);
  saveState(state);
  enterPlay(state, true);  // true = run sorteggio
});

// Initialize with 4 players
initSetupSlots(4);
```

- [ ] **Step 2: Verificare**

Aprire `/live`, selezionare giocatori e commander per tutti gli slot → il bottone "Inizia Partita" diventa attivo. Cambiare il numero di giocatori → gli slot si mostrano/nascondono correttamente.

- [ ] **Step 3: Commit**

```bash
git add app/templates/live.html
git commit -m "feat: setup screen live counter interattivo"
```

---

## Task 4: Layout grid play screen

**Files:**
- Modify: `app/templates/live.html`

- [ ] **Step 1: Aggiungere LAYOUT_CONFIG e buildGrid nel blocco script**

```javascript
// ── Grid layout config ─────────────────────────────────────────
// slots: [row, col, rowSpan, colSpan, rotationDeg]
// Grid è 1-indexed CSS grid
const LAYOUT_CONFIG = {
  2: { rows: '1fr 1fr', cols: '1fr',
       slots: [[2,1,1,1,0], [1,1,1,1,180]] },
  3: { rows: '1fr 1fr', cols: '1fr 1fr',
       slots: [[2,1,1,2,0], [1,1,1,1,180], [1,2,1,1,180]] },
  4: { rows: '1fr 1fr', cols: '1fr 1fr',
       slots: [[2,1,1,1,0], [2,2,1,1,0], [1,1,1,1,180], [1,2,1,1,180]] },
  5: { rows: '1fr 1fr 1fr', cols: '1fr 1fr',
       slots: [[3,1,1,1,0], [3,2,1,1,0], [2,2,1,1,90], [1,1,1,1,180], [1,2,1,1,180]] },
  6: { rows: '1fr 1fr 1fr', cols: '1fr 1fr',
       slots: [[3,1,1,1,0], [3,2,1,1,0], [2,2,1,1,90], [1,1,1,1,180], [1,2,1,1,180], [2,1,1,1,270]] },
};

// ── Build play grid ────────────────────────────────────────────
function buildGrid(state) {
  const cfg = LAYOUT_CONFIG[state.playerCount];
  const grid = document.getElementById('play-grid');
  grid.style.gridTemplateRows = cfg.rows;
  grid.style.gridTemplateColumns = cfg.cols;
  grid.innerHTML = '';

  state.slots.forEach((slot, i) => {
    const [row, col, rowSpan, colSpan, rotate] = cfg.slots[i];
    const tile = document.createElement('div');
    tile.className = 'tile' + (slot.eliminated ? ' eliminated' : '');
    tile.dataset.slot = i;
    tile.dataset.rotate = rotate;
    tile.style.gridRow = `${row} / span ${rowSpan}`;
    tile.style.gridColumn = `${col} / span ${colSpan}`;

    tile.innerHTML = `
      <div class="tile-inner">
        <div class="tile-content" style="transform:rotate(${rotate}deg)">
          <div class="tile-corner">
            <button class="sol-btn ${slot.solRing ? 'sol-active' : ''}" data-slot="${i}" title="Sol Ring T1">🪙</button>
            <button class="edit-btn" data-slot="${i}" title="Modifica">✏</button>
          </div>
          <div class="tile-hp" data-slot="${i}">${slot.hp}</div>
          <div class="tile-name">${esc(slot.playerName)} · ${esc(slot.commanderName)}</div>
        </div>
        <div class="tile-elim-overlay">✕</div>
      </div>`;

    grid.appendChild(tile);
  });
}
```

- [ ] **Step 2: Aggiungere la funzione enterPlay (stub per ora)**

```javascript
function enterPlay(state, runSorteggio = false) {
  document.getElementById('live-setup').style.display = 'none';
  document.getElementById('live-play').style.display = 'block';
  document.body.classList.add('live-play');

  // Try fullscreen
  const el = document.documentElement;
  if (el.requestFullscreen) el.requestFullscreen().catch(() => {});

  buildGrid(state);
  updateTurnDisplay(state);

  if (runSorteggio) {
    startSorteggio(state);
  } else {
    // Resume: bindPlayInteractions viene chiamato qui (non dal sorteggio)
    bindPlayInteractions(state);
  }
}

function updateTurnDisplay(state) {
  document.getElementById('turn-num').textContent = state.currentTurn;
}
```

- [ ] **Step 3: Verificare visivamente**

Aprire `/live`, completare il setup con 4 giocatori e cliccare "Inizia Partita". La pagina deve entrare in modalità fullscreen con 4 tile (2 normali in basso, 2 ruotate 180° in alto). Verificare anche con 2, 3, 5, 6 giocatori.

- [ ] **Step 4: Commit**

```bash
git add app/templates/live.html
git commit -m "feat: play screen grid layout con rotazioni per 2-6 giocatori"
```

---

## Task 5: Animazione sorteggio

**Files:**
- Modify: `app/templates/live.html`

- [ ] **Step 1: Aggiungere startSorteggio nel blocco script**

```javascript
// ── Sorteggio animation ────────────────────────────────────────
function startSorteggio(state) {
  const tiles = document.querySelectorAll('.tile');
  const n = state.playerCount;
  const winnerIdx = Math.floor(Math.random() * n);

  const FAST_CYCLES = 3;
  const totalFast = FAST_CYCLES * n;
  const fastEndPos = totalFast % n;
  let slowExtra = (winnerIdx - fastEndPos + n) % n;
  if (slowExtra === 0) slowExtra = n;  // almeno un giro lento completo
  const totalSteps = totalFast + slowExtra;

  let step = 0;
  let prevPos = -1;

  function tick() {
    const pos = step % n;
    if (prevPos >= 0 && prevPos < tiles.length) tiles[prevPos].classList.remove('sorteggio-highlight');
    if (pos < tiles.length) tiles[pos].classList.add('sorteggio-highlight');
    prevPos = pos;
    step++;

    if (step >= totalSteps) {
      // Rimane evidenziato il vincitore per 900ms poi parte la partita
      setTimeout(() => {
        tiles.forEach(t => t.classList.remove('sorteggio-highlight'));
        state.firstPlayerIndex = winnerIdx;
        saveState(state);
        bindPlayInteractions(state);
      }, 900);
      return;
    }

    const isFast = step < totalFast;
    const delay = isFast ? 80 : 80 + (step - totalFast) * 140;
    setTimeout(tick, delay);
  }

  // Disabilita le interazioni durante l'animazione
  document.getElementById('play-grid').style.pointerEvents = 'none';
  setTimeout(() => {
    document.getElementById('play-grid').style.pointerEvents = '';
  }, (totalSteps * 80) + 900 + 200);

  tick();
}
```

- [ ] **Step 2: Verificare**

Aprire `/live`, completare il setup e avviare la partita. Le tile devono illuminarsi in sequenza, rallentare e fermarsi su un giocatore casuale.

- [ ] **Step 3: Commit**

```bash
git add app/templates/live.html
git commit -m "feat: animazione sorteggio primo giocatore"
```

---

## Task 6: Interazioni tile (tap +/-1, long press, sol ring, edit)

**Files:**
- Modify: `app/templates/live.html`

- [ ] **Step 1: Aggiungere bindPlayInteractions e gestori tile**

```javascript
// ── Play interactions ──────────────────────────────────────────
let longPressTimer = null;
let longPressSlot = null;
const LONG_PRESS_MS = 500;

function changeHp(state, slotIdx, delta) {
  if (state.slots[slotIdx].eliminated) return;
  state.slots[slotIdx].hp += delta;
  updateTileHp(state, slotIdx);
  checkElimination(state, slotIdx);
  saveState(state);
}

function setHp(state, slotIdx, value) {
  if (state.slots[slotIdx].eliminated) return;
  state.slots[slotIdx].hp = parseInt(value) || 0;
  updateTileHp(state, slotIdx);
  checkElimination(state, slotIdx);
  saveState(state);
}

function updateTileHp(state, slotIdx) {
  const hpEl = document.querySelector(`.tile-hp[data-slot="${slotIdx}"]`);
  if (!hpEl) return;
  hpEl.textContent = state.slots[slotIdx].hp;
  hpEl.classList.remove('hp-flash');
  void hpEl.offsetWidth;  // reflow per riattivare animazione
  hpEl.classList.add('hp-flash');
}

function checkElimination(state, slotIdx) {
  const slot = state.slots[slotIdx];
  if (!slot.eliminated && slot.hp <= 0) {
    slot.eliminated = true;
    slot.turnEliminated = state.currentTurn;
    saveState(state);
    const tile = document.querySelector(`.tile[data-slot="${slotIdx}"]`);
    if (tile) tile.classList.add('eliminated');
    checkAutoEnd(state);
  }
}

function checkAutoEnd(state) {
  const active = state.slots.filter(s => !s.eliminated);
  if (active.length === 1) {
    const winner = active[0];
    const msg = document.getElementById('end-overlay-msg');
    msg.textContent = `Rimane solo ${winner.playerName}. Terminare la partita?`;
    document.getElementById('end-overlay').classList.add('open');
  }
}

// HP free-input overlay
let hpInputSlot = null;
function openHpInput(state, slotIdx) {
  hpInputSlot = slotIdx;
  document.getElementById('hp-input-field').value = state.slots[slotIdx].hp;
  document.getElementById('hp-input-overlay').classList.add('open');
  document.getElementById('hp-input-field').focus();
  document.getElementById('hp-input-field').select();
}

document.getElementById('hp-input-confirm').addEventListener('click', () => {
  if (hpInputSlot === null) return;
  const val = document.getElementById('hp-input-field').value;
  setHp(window._liveState, hpInputSlot, val);
  document.getElementById('hp-input-overlay').classList.remove('open');
  hpInputSlot = null;
});
document.getElementById('hp-input-cancel').addEventListener('click', () => {
  document.getElementById('hp-input-overlay').classList.remove('open');
  hpInputSlot = null;
});

function bindPlayInteractions(state) {
  // Store state reference globally for overlay handlers
  window._liveState = state;

  const grid = document.getElementById('play-grid');

  // Tap +/- con gestione rotazione
  grid.addEventListener('pointerdown', e => {
    const tile = e.target.closest('.tile');
    if (!tile) return;
    if (e.target.closest('button')) return;  // bottoni corner gestiti separatamente

    const slotIdx = parseInt(tile.dataset.slot);
    const rotate = parseInt(tile.dataset.rotate);

    // Long press → HP libre input
    longPressSlot = slotIdx;
    longPressTimer = setTimeout(() => {
      longPressTimer = null;
      openHpInput(state, slotIdx);
    }, LONG_PRESS_MS);
  });

  grid.addEventListener('pointerup', e => {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    } else {
      return;  // era long press, già gestito
    }

    const tile = e.target.closest('.tile');
    if (!tile || e.target.closest('button')) return;
    if (state.slots[parseInt(tile.dataset.slot)].eliminated) return;

    const slotIdx = parseInt(tile.dataset.slot);
    const rotate = parseInt(tile.dataset.rotate);
    const rect = tile.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;

    // Determina +1 o -1 in base alla rotazione
    let isRight;
    switch (rotate) {
      case 0:   isRight = cx > rect.width / 2;  break;
      case 180: isRight = cx < rect.width / 2;  break;
      case 90:  isRight = cy < rect.height / 2; break;
      case 270: isRight = cy > rect.height / 2; break;
      default:  isRight = cx > rect.width / 2;
    }
    changeHp(state, slotIdx, isRight ? 1 : -1);
  });

  grid.addEventListener('pointercancel', () => {
    if (longPressTimer) { clearTimeout(longPressTimer); longPressTimer = null; }
  });

  // Sol Ring toggle
  grid.addEventListener('click', e => {
    const btn = e.target.closest('.sol-btn');
    if (!btn) return;
    const slotIdx = parseInt(btn.dataset.slot);
    state.slots[slotIdx].solRing = !state.slots[slotIdx].solRing;
    btn.classList.toggle('sol-active', state.slots[slotIdx].solRing);
    saveState(state);
  });

  // Edit button
  grid.addEventListener('click', e => {
    const btn = e.target.closest('.edit-btn');
    if (!btn) return;
    openEditModal(state, parseInt(btn.dataset.slot));
  });
}
```

- [ ] **Step 2: Verificare**

Avviare una partita e testare:
- Tap sinistra tile → PV scende di 1, tap destra → sale di 1 (verificare per tile ruotate 180° che la direzione sia quella del giocatore)
- Pressione lunga su tile → si apre l'input numerico libero
- Sol Ring si attiva/disattiva con colore diverso

- [ ] **Step 3: Commit**

```bash
git add app/templates/live.html
git commit -m "feat: interazioni tile tap +/-1 e long press HP"
```

---

## Task 7: Edit modal e turn counter

**Files:**
- Modify: `app/templates/live.html`

- [ ] **Step 1: Aggiungere openEditModal nel blocco script**

```javascript
// ── Edit modal ─────────────────────────────────────────────────
let editSlotIdx = null;

function openEditModal(state, slotIdx) {
  editSlotIdx = slotIdx;
  const slot = state.slots[slotIdx];

  const pSel = document.getElementById('edit-player-sel');
  pSel.innerHTML = PLAYERS.map(p =>
    `<option value="${p.id}" ${p.id===slot.playerId?'selected':''}>${esc(p.name)}</option>`
  ).join('');

  const cSel = document.getElementById('edit-commander-sel');
  cSel.innerHTML = COMMANDERS.map(c =>
    `<option value="${c.id}" ${c.id===slot.commanderId?'selected':''}>${esc(c.name)} (${esc(c.color_identity)})</option>`
  ).join('');

  document.getElementById('edit-modal').classList.add('open');
}

document.getElementById('edit-confirm').addEventListener('click', () => {
  if (editSlotIdx === null) return;
  const state = window._liveState;
  const pId = parseInt(document.getElementById('edit-player-sel').value);
  const cId = parseInt(document.getElementById('edit-commander-sel').value);
  const player = PLAYERS.find(p => p.id === pId);
  const commander = COMMANDERS.find(c => c.id === cId);
  state.slots[editSlotIdx].playerId = pId;
  state.slots[editSlotIdx].playerName = player?.name ?? '';
  state.slots[editSlotIdx].commanderId = cId;
  state.slots[editSlotIdx].commanderName = commander?.name ?? '';
  saveState(state);
  // Aggiorna tile visualmente
  buildGrid(state);
  bindPlayInteractions(state);
  document.getElementById('edit-modal').classList.remove('open');
  editSlotIdx = null;
});

document.getElementById('edit-cancel').addEventListener('click', () => {
  document.getElementById('edit-modal').classList.remove('open');
  editSlotIdx = null;
});
```

- [ ] **Step 2: Aggiungere gestori turn counter**

```javascript
// ── Turn counter ───────────────────────────────────────────────
let turnLongPressTimer = null;
let endGameVisible = false;

document.getElementById('turn-minus').addEventListener('click', () => {
  const state = window._liveState;
  if (!state) return;
  state.currentTurn = Math.max(1, state.currentTurn - 1);
  updateTurnDisplay(state);
  saveState(state);
});

document.getElementById('turn-plus').addEventListener('click', () => {
  const state = window._liveState;
  if (!state) return;
  state.currentTurn++;
  updateTurnDisplay(state);
  saveState(state);
});

// Flag per evitare che long press attivi anche il click successivo
let turnLongPressed = false;

// Tap diretto sul numero → contenteditable
document.getElementById('turn-num').addEventListener('click', function() {
  if (turnLongPressed) { turnLongPressed = false; return; }
  this.contentEditable = 'true';
  this.focus();
  const range = document.createRange();
  range.selectNodeContents(this);
  window.getSelection().removeAllRanges();
  window.getSelection().addRange(range);
});

document.getElementById('turn-num').addEventListener('blur', function() {
  const state = window._liveState;
  if (!state) return;
  const val = parseInt(this.textContent);
  state.currentTurn = isNaN(val) || val < 1 ? 1 : val;
  this.contentEditable = 'false';
  updateTurnDisplay(state);
  saveState(state);
});

document.getElementById('turn-num').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') { e.preventDefault(); this.blur(); }
});

// Long press sul turn center → mostra/nascondi "Termina partita"
document.getElementById('turn-center').addEventListener('pointerdown', e => {
  if (e.target.closest('button') || e.target.id === 'turn-num') return;
  turnLongPressTimer = setTimeout(() => {
    endGameVisible = !endGameVisible;
    document.getElementById('end-game-btn').style.display = endGameVisible ? 'block' : 'none';
  }, LONG_PRESS_MS);
});

document.getElementById('turn-center').addEventListener('pointerup', () => {
  if (turnLongPressTimer) { clearTimeout(turnLongPressTimer); turnLongPressTimer = null; }
});

// Long press sul numero di turno stesso
document.getElementById('turn-num').addEventListener('pointerdown', e => {
  turnLongPressTimer = setTimeout(() => {
    turnLongPressed = true;  // impedisce il click contenteditable successivo
    endGameVisible = !endGameVisible;
    document.getElementById('end-game-btn').style.display = endGameVisible ? 'block' : 'none';
  }, LONG_PRESS_MS);
});

document.getElementById('turn-num').addEventListener('pointerup', () => {
  if (turnLongPressTimer) { clearTimeout(turnLongPressTimer); turnLongPressTimer = null; }
});
```

- [ ] **Step 3: Verificare**

- Il turno si incrementa/decrementa con i bottoni
- Tap sul numero → campo editabile, Enter o blur lo salva
- Long press sul numero → appare/scompare "Termina partita"
- Edit modal si apre, modifica player/commander e ricostruisce la griglia

- [ ] **Step 4: Commit**

```bash
git add app/templates/live.html
git commit -m "feat: turn counter editabile, edit modal tile, long press end-game"
```

---

## Task 8: Fine partita e handoff sessionStorage

**Files:**
- Modify: `app/templates/live.html`

- [ ] **Step 1: Aggiungere endGame nel blocco script**

```javascript
// ── End game ───────────────────────────────────────────────────
function endGame(state) {
  // Serializza per pre-fill di /game/new
  const slots = state.slots;
  const winnerIdx = slots.findIndex(s => !s.eliminated);

  // Ordina i perdenti per turno di eliminazione (più alto = sopravvissuto più a lungo = piazzamento migliore)
  const rows = slots.map((slot, i) => ({
    player_id: slot.playerId,
    commander_id: slot.commanderId,
    is_winner: i === winnerIdx,
    sol_ring: slot.solRing,
    turn_eliminated: slot.turnEliminated,
    turn_order: i + 1,
  }));

  const prefill = {
    date: state.startedAt,
    total_turns: state.currentTurn,
    rows,
  };

  sessionStorage.setItem('mtg_prefill', JSON.stringify(prefill));
  clearState();

  // Esci da fullscreen
  if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
  document.body.classList.remove('live-play');

  window.location.href = '/game/new';
}

// Bottone "Termina partita" (long press sul turno)
document.getElementById('end-game-btn').addEventListener('click', () => {
  endGame(window._liveState);
});

// Auto-end overlay
document.getElementById('end-overlay-confirm').addEventListener('click', () => {
  document.getElementById('end-overlay').classList.remove('open');
  endGame(window._liveState);
});
document.getElementById('end-overlay-ignore').addEventListener('click', () => {
  document.getElementById('end-overlay').classList.remove('open');
});
```

- [ ] **Step 2: Verificare**

Avviare una partita, portare tutti tranne uno a 0 PV → appare l'overlay "Rimane solo X". Confermare → redirect a `/game/new`. Verificare che `sessionStorage.getItem('mtg_prefill')` contenga i dati corretti (aprire DevTools prima del redirect).

Testare anche il percorso manuale: long press sul turno → "Termina partita" → redirect.

- [ ] **Step 3: Commit**

```bash
git add app/templates/live.html
git commit -m "feat: endGame serializza sessionStorage e redirect a /game/new"
```

---

## Task 9: Pre-fill di `/game/new` da sessionStorage

**Files:**
- Modify: `app/templates/game_form.html`

- [ ] **Step 1: Aggiungere lettura prefill nel blocco script di game_form.html**

In `app/templates/game_form.html`, sostituire il blocco di inizializzazione finale (righe 197–201):

```javascript
// Vecchio codice da sostituire:
// if (INIT_DATA.length) {
//   INIT_DATA.forEach(d => addRow(d));
// } else {
//   for (let i = 0; i < 4; i++) addRow();
// }
```

Con:

```javascript
const prefill = (() => {
  try {
    const raw = sessionStorage.getItem('mtg_prefill');
    if (!raw) return null;
    sessionStorage.removeItem('mtg_prefill');
    return JSON.parse(raw);
  } catch { return null; }
})();

if (prefill) {
  // Imposta la data
  const dateInput = document.querySelector('[name="date"]');
  if (dateInput && prefill.date) dateInput.value = prefill.date;
  // Aggiunge le righe pre-compilate
  prefill.rows.forEach(r => addRow({
    player_id:      r.player_id,
    commander_id:   r.commander_id,
    is_winner:      r.is_winner,
    sol_ring:       r.sol_ring,
    turn_eliminated: r.turn_eliminated,
  }));
  // Seleziona il radio vincitore
  syncWinnerUI();
} else if (INIT_DATA.length) {
  INIT_DATA.forEach(d => addRow(d));
} else {
  for (let i = 0; i < 4; i++) addRow();
}
```

- [ ] **Step 2: Verificare il pre-fill completo**

Eseguire una partita live completa (dalla pagina `/live`):
1. Setup con 3–4 giocatori
2. Portare tutti tranne uno a 0 PV
3. Confermare la fine partita
4. Verificare che `/game/new` si apra con i giocatori, commander, Sol Ring e turni di eliminazione già compilati
5. Verificare che la data sia quella di oggi
6. Verificare che il radio "vincitore" sia sul giocatore corretto

- [ ] **Step 3: Commit**

```bash
git add app/templates/game_form.html
git commit -m "feat: pre-fill /game/new da sessionStorage dopo partita live"
```

---

## Task 10: Test integrazione finale e pulizia

**Files:**
- Modify: `app/templates/live.html` (eventuali fix da test)

- [ ] **Step 1: Test flusso completo 4 giocatori**

1. Aprire `/live`
2. Selezionare 4 giocatori e commander diversi
3. Avviare: verificare animazione sorteggio
4. Modificare PV con tap sx/dx per ogni tile
5. Portare 3 giocatori a 0 → verificare eliminazione automatica e overlay finale
6. Confermare fine partita
7. Su `/game/new`: verificare pre-fill corretto, aggiungere condizioni vittoria/sconfitta e salvare
8. Verificare che la partita appaia in `/history` e in `/` (dashboard)

- [ ] **Step 2: Test resume partita**

1. Avviare una partita, modificare qualche PV
2. Chiudere il tab/browser
3. Riaprire `/live` → deve apparire il banner "Riprendi partita"
4. Cliccare "Riprendi" → la griglia si ricostruisce con i PV salvati

- [ ] **Step 3: Test 6 giocatori**

Verificare che con 6 giocatori le tile siano leggibili da ogni lato e le rotazioni siano corrette (sinistra 270°, destra 90°, alto 180°, basso 0°).

- [ ] **Step 4: Verificare su mobile (DevTools emulation)**

Aprire Chrome DevTools → modalità dispositivo mobile (375×812 iPhone SE). Verificare che i numeri PV siano grandi, le tile occupino tutto lo schermo e il counter di turno al centro sia visibile.

- [ ] **Step 5: Commit finale**

```bash
git add -A
git commit -m "feat: live counter completo con pre-fill game form"
```
