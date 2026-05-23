# Live Counter v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the separate setup screen with an inline tile-grid setup, and add per-tile color selection with adaptive text.

**Architecture:** Single file change — `app/templates/live.html`. The play grid is made immediately visible (fullscreen) on page load; each tile starts in `edit` mode with a form inside; a `#setup-center` overlay replaces the old `#live-setup` page for player count selection and the Start button. The `tile-editing` CSS class toggles between edit and play content within each tile.

**Tech Stack:** Vanilla JS, CSS, Jinja2 template, localStorage

---

## File structure

| File | Operation | Scope |
|---|---|---|
| `app/templates/live.html` | Modify | CSS, HTML, JS — all changes in this one file |

---

### Task 1: CSS — tile states + setup center + clean up removed elements

**Files:**
- Modify: `app/templates/live.html` (lines 5–115, the `<style>` block)

- [ ] **Step 1: Remove obsolete CSS rules**

In the `<style>` block, delete the entire `#live-setup`, `.seat-slot` block (lines 13–14) and the entire `#edit-modal` block (lines 83–93):

```css
/* DELETE these blocks: */
#live-setup { max-width: 32rem; margin: 0 auto; }
.seat-slot { background: #1a1d27; border: 1px solid #2d3147; border-radius: 0.75rem; padding: 1rem; margin-bottom: 0.75rem; }
.seat-slot.hidden { display: none; }

/* ... and ... */

#edit-modal {
  display: none; position: fixed; inset: 0; z-index: 100;
  background: rgba(0,0,0,0.85); align-items: center; justify-content: center;
}
#edit-modal.open { display: flex; }
#edit-modal-inner {
  background: #1a1d27; border: 1px solid #2d3147; border-radius: 1rem;
  padding: 1.5rem; width: min(90vw, 20rem); display: flex; flex-direction: column; gap: 1rem;
}
```

- [ ] **Step 2: Change `#live-play` to always-visible**

Replace:
```css
#live-play { display: none; position: fixed; inset: 0; background: #000; overflow: hidden; touch-action: none; }
```
With:
```css
#live-play { display: block; position: fixed; inset: 0; background: #000; overflow: hidden; touch-action: none; }
```

- [ ] **Step 3: Update `.tile-content` and add tile state CSS**

`.tile-content` becomes a transparent wrapper. Add both content sections and the toggle rules. Replace the existing `.tile-content` block (which sets flex/column/center) and add below `.tile-elim-overlay`:

```css
/* tile-content is the rotated wrapper; children fill it */
.tile-content { position: relative; width: 100%; height: 100%; }

/* play content */
.tile-play-content {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  width: 100%; height: 100%;
}

/* edit content */
.tile-edit-content {
  display: none; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.4rem; padding: 0.5rem; width: 100%; height: 100%; overflow-y: auto;
}

/* toggle */
.tile.tile-editing .tile-play-content { display: none; }
.tile.tile-editing .tile-edit-content { display: flex; }

/* color swatches */
.tile-swatches { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.3rem; margin: 0.2rem 0; }
.color-swatch {
  width: 1.1rem; height: 1.1rem; border-radius: 50%;
  cursor: pointer; border: 2px solid transparent; padding: 0;
}
.color-swatch.selected { border-color: currentColor; }

/* tile edit selects and OK button */
.tile-sel {
  font-size: clamp(0.6rem, 2vw, 0.8rem); max-width: 90%;
  background: rgba(0,0,0,0.4); color: inherit;
  border: 1px solid rgba(255,255,255,0.2); border-radius: 0.35rem; padding: 0.2rem 0.3rem;
}
.tile-ok-btn {
  margin-top: 0.2rem; padding: 0.25rem 1.2rem;
  background: rgba(255,255,255,0.15); color: inherit;
  border: 1px solid rgba(255,255,255,0.3); border-radius: 0.4rem;
  font-size: clamp(0.65rem, 2vw, 0.85rem); font-weight: 700; cursor: pointer;
}
.tile-ok-btn:disabled { opacity: 0.4; cursor: not-allowed; }
```

- [ ] **Step 4: Hide `#turn-center` by default; add `#setup-center` CSS**

Replace the existing `#turn-center` rule to start hidden:
```css
#turn-center {
  display: none;   /* shown in JS when entering play phase */
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  z-index: 50; align-items: center; gap: 0.5rem;
  background: rgba(0,0,0,0.75); border-radius: 1rem;
  padding: 0.4rem 0.75rem; backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.08);
}
```

Add `#setup-center` after `#turn-center` styles:
```css
#setup-center {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  z-index: 50; display: flex; flex-direction: column; align-items: center; gap: 0.75rem;
  background: rgba(0,0,0,0.85); border-radius: 1rem;
  padding: 1rem 1.5rem; backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.1); min-width: 13rem; text-align: center;
}
#setup-center.hidden { display: none; }
#setup-start-btn {
  width: 100%; padding: 0.5rem 1rem; background: #7c3aed; color: #fff;
  border: none; border-radius: 0.5rem; font-size: 0.9rem; font-weight: 700;
  cursor: pointer;
}
#setup-start-btn:disabled { opacity: 0.45; cursor: not-allowed; }
#setup-start-btn:not(:disabled):hover { background: #6d28d9; }
```

- [ ] **Step 5: Start the dev server and verify the page loads without console errors**

```bash
python run.py
```
Open `http://localhost:5001/live` — expect a black fullscreen page (grid not yet built, no JS to drive it), no console errors about missing elements. The old setup form should no longer appear.

- [ ] **Step 6: Commit**

```bash
git add app/templates/live.html
git commit -m "feat(live-v2): CSS for tile edit/play states and setup center"
```

---

### Task 2: HTML — remove `#live-setup`, remove `#edit-modal`, add `#setup-center`

**Files:**
- Modify: `app/templates/live.html` (the `{% block content %}` HTML section)

- [ ] **Step 1: Delete the entire `#live-setup` block**

Remove everything from line 121 (`<!-- ══ SETUP SCREEN ═...`) through line 165 (`</div>`) — the entire `<div id="live-setup">` element and its contents.

- [ ] **Step 2: Delete the `#edit-modal` block**

Inside `<div id="live-play">`, remove the entire edit modal div (currently lines 179–196):
```html
<!-- DELETE: -->
  <!-- Edit modal -->
  <div id="edit-modal">
    <div id="edit-modal-inner">
      ...
    </div>
  </div>
```

- [ ] **Step 3: Add `#setup-center` inside `#live-play`**

Insert the new setup center after the opening `<div id="live-play">` tag and before `<div id="play-grid">`:

```html
<!-- ══ PLAY SCREEN ═══════════════════════════════════════════ -->
<div id="live-play">

  <!-- Setup center (visible during setup phase) -->
  <div id="setup-center">
    <!-- Resume banner (shown instead of controls when a saved game exists) -->
    <div id="resume-banner" style="display:none">
      <p style="color:#fbbf24;font-size:0.85rem;margin-bottom:0.5rem">⚠ C'è una partita in corso non terminata.</p>
      <div style="display:flex;gap:0.5rem;justify-content:center">
        <button id="resume-btn" class="btn-primary text-sm" style="padding:0.3rem 0.8rem">Riprendi</button>
        <button id="discard-btn" class="btn-sm text-sm" style="padding:0.3rem 0.8rem">Scarta</button>
      </div>
    </div>
    <!-- Player count + start controls -->
    <div id="setup-controls">
      <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:0.4rem">Numero di giocatori</div>
      <div style="display:flex;gap:0.4rem;margin-bottom:0.75rem">
        {% for n in [2,3,4,5,6] %}
        <button type="button"
                class="count-btn btn-sm px-3 py-1.5 font-bold {% if n == 4 %}ring-2 ring-mtg-accent{% endif %}"
                data-count="{{ n }}">{{ n }}</button>
        {% endfor %}
      </div>
      <button id="setup-start-btn" disabled>Inizia Partita</button>
    </div>
  </div>

  <div id="play-grid"></div>
  ...
```

- [ ] **Step 4: Verify HTML renders without errors**

```bash
python run.py
```
Open `/live` — the page should show the black fullscreen background with the setup center in the middle (player count buttons + disabled Start button). No setup form, no edit modal.

- [ ] **Step 5: Commit**

```bash
git add app/templates/live.html
git commit -m "feat(live-v2): HTML structure — setup center, remove old setup screen and edit modal"
```

---

### Task 3: JS — TILE_COLORS constant and color helper functions

**Files:**
- Modify: `app/templates/live.html` (top of `<script>` block, after `const STATE_KEY`)

- [ ] **Step 1: Add constants and helpers right after the existing const declarations**

After `window._liveInteractionsBound = false;`, insert:

```javascript
const TILE_COLORS = [
  '#e83e8c',  // Rosa
  '#f0f0f0',  // Bianco
  '#0dcaf0',  // Cyan
  '#343a40',  // Charcoal
  '#198754',  // Verde
  '#ffc107',  // Ambra
  '#6f42c1',  // Viola
  '#fd7e14',  // Arancio
];

function textColor(hex) {
  const r = parseInt(hex.slice(1,3), 16);
  const g = parseInt(hex.slice(3,5), 16);
  const b = parseInt(hex.slice(5,7), 16);
  return (0.299*r + 0.587*g + 0.114*b) > 128 ? '#000000' : '#ffffff';
}

function assignColors(count) {
  const shuffled = [...TILE_COLORS].sort(() => Math.random() - 0.5);
  return Array.from({ length: count }, (_, i) => shuffled[i % shuffled.length]);
}
```

- [ ] **Step 2: Verify in browser console**

Open DevTools on `/live` and run:
```javascript
TILE_COLORS.length          // → 8
textColor('#f0f0f0')        // → '#000000'
textColor('#343a40')        // → '#ffffff'
assignColors(4).length      // → 4
```

- [ ] **Step 3: Commit**

```bash
git add app/templates/live.html
git commit -m "feat(live-v2): TILE_COLORS constant and color helper functions"
```

---

### Task 4: JS — buildGrid v2 (dual content + per-tile color)

**Files:**
- Modify: `app/templates/live.html` — replace the existing `buildGrid` function

- [ ] **Step 1: Replace `buildGrid` with the v2 version**

The existing `buildGrid` function (lines 359–390) generates tiles with a single `.tile-content`. Replace it entirely:

```javascript
function buildGrid(state) {
  const cfg = LAYOUT_CONFIG[state.playerCount];
  const grid = document.getElementById('play-grid');
  grid.style.gridTemplateRows = cfg.rows;
  grid.style.gridTemplateColumns = cfg.cols;
  grid.innerHTML = '';

  state.slots.slice(0, state.playerCount).forEach((slot, i) => {
    const [row, col, rowSpan, colSpan, rotate] = cfg.slots[i];
    const tile = document.createElement('div');
    const bg = slot.color || '#0a0a0a';
    const fg = slot.color ? textColor(slot.color) : '#f1f5f9';
    tile.className = 'tile' + (slot.eliminated ? ' eliminated' : '') + (!slot.confirmed ? ' tile-editing' : '');
    tile.dataset.slot = i;
    tile.dataset.rotate = rotate;
    tile.style.gridRow = `${row} / span ${rowSpan}`;
    tile.style.gridColumn = `${col} / span ${colSpan}`;
    tile.style.background = bg;
    tile.style.color = fg;

    const swatchesHtml = TILE_COLORS.map(c =>
      `<button class="color-swatch${c === bg ? ' selected' : ''}" data-color="${c}" data-slot="${i}" style="background:${c}" title="${c}"></button>`
    ).join('');

    tile.innerHTML = `
      <div class="tile-inner">
        <div class="tile-content" style="transform:rotate(${rotate}deg)">

          <div class="tile-play-content">
            <div class="tile-corner">
              <button class="sol-btn${slot.solRing ? ' sol-active' : ''}" data-slot="${i}" title="Sol Ring T1">🪙</button>
              <button class="edit-btn" data-slot="${i}" title="Modifica">✏</button>
            </div>
            <div class="tile-hp" data-slot="${i}">${slot.hp}</div>
            <div class="tile-name">${esc(slot.playerName)} · ${esc(slot.commanderName)}</div>
          </div>

          <div class="tile-edit-content">
            <select class="tile-sel tile-player-sel" data-slot="${i}">
              ${playerOptions(slot.playerId)}
            </select>
            <select class="tile-sel tile-commander-sel" data-slot="${i}">
              ${commanderOptions(slot.commanderId)}
            </select>
            <div class="tile-swatches" data-slot="${i}">${swatchesHtml}</div>
            <button class="tile-ok-btn" data-slot="${i}">OK</button>
          </div>

        </div>
        <div class="tile-elim-overlay">✕</div>
      </div>`;

    grid.appendChild(tile);
  });
}
```

- [ ] **Step 2: Verify grid renders in the browser**

In `/live`, open DevTools and call:
```javascript
// Simulate a setup state manually to test buildGrid
const testState = {
  phase: 'setup', playerCount: 4,
  slots: assignColors(6).map(color => ({
    playerId: null, playerName: '', commanderId: null, commanderName: '',
    hp: 40, solRing: false, eliminated: false, turnEliminated: null,
    color, confirmed: false,
  })),
  currentTurn: 1, firstPlayerIndex: null, startedAt: '2026-05-23'
};
buildGrid(testState);
```

Expected: 4 colored tiles appear in the grid, each showing the edit form (selects + swatches + OK button), rotated to face each player. No play content visible.

- [ ] **Step 3: Commit**

```bash
git add app/templates/live.html
git commit -m "feat(live-v2): buildGrid v2 with dual content and per-tile color"
```

---

### Task 5: JS — setup phase logic

**Files:**
- Modify: `app/templates/live.html` (JS section — replace `// ── Setup screen ──` block and add new functions)

- [ ] **Step 1: Replace `makeInitialState` with new state factories**

Replace the existing `makeInitialState` function (lines 233–242):

```javascript
function makeSetupState(playerCount) {
  const colors = assignColors(6);
  const slots = Array.from({ length: 6 }, (_, i) => ({
    playerId: null, playerName: '',
    commanderId: null, commanderName: '',
    hp: 40, solRing: false, eliminated: false, turnEliminated: null,
    color: colors[i], confirmed: false,
  }));
  return {
    phase: 'setup', playerCount,
    slots, currentTurn: 1, firstPlayerIndex: null,
    startedAt: new Date().toISOString().slice(0, 10),
  };
}

function makePlayState(state) {
  return { ...state, phase: 'play' };
}
```

- [ ] **Step 2: Add `updateStartBtn`**

```javascript
function updateStartBtn(state) {
  const allConfirmed = state.slots.slice(0, state.playerCount).every(s => s.confirmed);
  const btn = document.getElementById('setup-start-btn');
  btn.disabled = !allConfirmed;
}
```

- [ ] **Step 3: Add `handleTileOk`**

```javascript
function handleTileOk(state, slotIdx) {
  const tile = document.querySelector(`.tile[data-slot="${slotIdx}"]`);
  if (!tile) return;
  const pId = parseInt(tile.querySelector('.tile-player-sel').value);
  const cId = parseInt(tile.querySelector('.tile-commander-sel').value);
  if (!pId || !cId) return;
  const player    = PLAYERS.find(p => p.id === pId);
  const commander = COMMANDERS.find(c => c.id === cId);
  const slot = state.slots[slotIdx];
  slot.playerId      = pId;
  slot.playerName    = player?.name ?? '';
  slot.commanderId   = cId;
  slot.commanderName = commander?.name ?? '';
  slot.confirmed     = true;
  tile.querySelector('.tile-hp').textContent   = slot.hp;
  tile.querySelector('.tile-name').textContent = `${slot.playerName} · ${slot.commanderName}`;
  tile.classList.remove('tile-editing');
  saveState(state);
  if (state.phase === 'setup') updateStartBtn(state);
}
```

- [ ] **Step 4: Add `setTileEditMode`**

```javascript
function setTileEditMode(state, slotIdx) {
  const tile = document.querySelector(`.tile[data-slot="${slotIdx}"]`);
  if (!tile) return;
  const slot = state.slots[slotIdx];
  tile.querySelector('.tile-player-sel').value    = slot.playerId   ?? '';
  tile.querySelector('.tile-commander-sel').value = slot.commanderId ?? '';
  tile.querySelectorAll('.color-swatch').forEach(s => {
    s.classList.toggle('selected', s.dataset.color === slot.color);
  });
  tile.classList.add('tile-editing');
}
```

- [ ] **Step 5: Add `initSetupPhase` and `changePlayerCount`**

```javascript
function initSetupPhase(count) {
  const state = makeSetupState(count);
  window._liveState = state;
  saveState(state);
  buildGrid(state);
  updateStartBtn(state);
  // Sync active count button
  document.querySelectorAll('.count-btn').forEach(btn => {
    const n = parseInt(btn.dataset.count);
    btn.classList.toggle('ring-2', n === count);
    btn.classList.toggle('ring-mtg-accent', n === count);
  });
}

function changePlayerCount(state, newCount) {
  const oldCount = state.playerCount;
  state.playerCount = newCount;
  if (newCount > oldCount) {
    const freshColors = assignColors(6);
    for (let i = oldCount; i < newCount; i++) {
      if (!state.slots[i].confirmed) {
        state.slots[i].color = freshColors[i];
      }
    }
  }
  saveState(state);
  buildGrid(state);
  updateStartBtn(state);
}
```

- [ ] **Step 6: Verify in browser**

Open DevTools and:
```javascript
initSetupPhase(3);
// → 3 colored tiles appear, all in edit mode
// → setup-center shows 3 highlighted, Start disabled

handleTileOk(window._liveState, 0);
// → tile 0 switches to play content (HP=40, empty name since no player selected, but returns early because no player set)
// So first set a player/commander:
document.querySelector('[data-slot="0"].tile-player-sel').value = PLAYERS[0].id;
document.querySelector('[data-slot="0"].tile-commander-sel').value = COMMANDERS[0].id;
handleTileOk(window._liveState, 0);
// → tile 0 now shows play content with HP=40
// → window._liveState.slots[0].confirmed === true
```

- [ ] **Step 7: Commit**

```bash
git add app/templates/live.html
git commit -m "feat(live-v2): setup phase logic — initSetupPhase, handleTileOk, setTileEditMode"
```

---

### Task 6: JS — page load wiring, grid interactions, enterPlay update

**Files:**
- Modify: `app/templates/live.html` (JS section — replace old setup wiring, rename/update interaction binding)

- [ ] **Step 1: Remove old setup screen JS**

Delete the following blocks from the JS section:

1. `let selectedCount = 4;` declaration
2. The entire `initSetupSlots(count)` function
3. The entire `validateSetup()` function
4. `document.querySelectorAll('.count-btn').forEach(...)` — the old count-btn wiring
5. `document.querySelectorAll('.seat-player, .seat-commander').forEach(...)` — old change listener
6. The `// Resume banner` block (saved check + resume-btn + discard-btn listeners that reference `#resume-banner`)
7. `document.getElementById('start-btn').addEventListener(...)` — old start button listener
8. `initSetupSlots(4);` call at bottom of setup block

- [ ] **Step 2: Remove old `openEditModal` function and its event listeners**

Delete:
1. `let editSlotIdx = null;` declaration
2. The entire `openEditModal(state, slotIdx)` function
3. `document.getElementById('edit-confirm').addEventListener(...)` block
4. `document.getElementById('edit-cancel').addEventListener(...)` block

- [ ] **Step 3: Update `enterPlay` to start from setup phase**

Replace the current `enterPlay` function:

```javascript
function enterPlay(state, runSorteggio = false) {
  const playState = makePlayState(state);
  window._liveState = playState;
  saveState(playState);

  document.getElementById('setup-center').classList.add('hidden');
  document.getElementById('turn-center').style.display = 'flex';

  const el = document.documentElement;
  if (el.requestFullscreen) el.requestFullscreen().catch(() => {});

  buildGrid(playState);
  updateTurnDisplay(playState);

  if (runSorteggio) {
    startSorteggio(playState);
  } else {
    bindGridInteractions(playState);
  }
}
```

- [ ] **Step 4: Rename `bindPlayInteractions` → `bindGridInteractions` and update edit-btn handler**

Replace the old `function bindPlayInteractions(state)` with:

```javascript
function bindGridInteractions(state) {
  window._liveState = state;
  if (window._liveInteractionsBound) return;
  window._liveInteractionsBound = true;

  const grid = document.getElementById('play-grid');

  // Tile tap: long press → HP input; short tap → ±1
  grid.addEventListener('pointerdown', e => {
    const tile = e.target.closest('.tile');
    if (!tile || e.target.closest('button') || e.target.closest('select')) return;
    if (tile.classList.contains('tile-editing')) return;
    const slotIdx = parseInt(tile.dataset.slot);
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
      return;
    }
    const tile = e.target.closest('.tile');
    if (!tile || e.target.closest('button') || e.target.closest('select')) return;
    if (tile.classList.contains('tile-editing')) return;
    const slotIdx = parseInt(tile.dataset.slot);
    if (state.slots[slotIdx].eliminated) return;
    const rotate = parseInt(tile.dataset.rotate);
    const rect = tile.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;
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

  // Edit button → inline tile edit
  grid.addEventListener('click', e => {
    const btn = e.target.closest('.edit-btn');
    if (!btn) return;
    setTileEditMode(state, parseInt(btn.dataset.slot));
  });

  // Tile OK button → confirm edit
  grid.addEventListener('click', e => {
    const btn = e.target.closest('.tile-ok-btn');
    if (!btn) return;
    handleTileOk(state, parseInt(btn.dataset.slot));
  });

  // Color swatch click
  grid.addEventListener('click', e => {
    const swatch = e.target.closest('.color-swatch');
    if (!swatch) return;
    const slotIdx = parseInt(swatch.dataset.slot);
    const color = swatch.dataset.color;
    state.slots[slotIdx].color = color;
    const tile = document.querySelector(`.tile[data-slot="${slotIdx}"]`);
    const fg = textColor(color);
    tile.style.background = color;
    tile.style.color = fg;
    tile.querySelectorAll('.color-swatch').forEach(s => {
      s.classList.toggle('selected', s.dataset.color === color);
    });
    saveState(state);
  });
}
```

- [ ] **Step 5: Update `startSorteggio` to call `bindGridInteractions`**

Inside `startSorteggio`, find the setTimeout callback where `bindPlayInteractions` is called and rename it:

```javascript
// OLD:
bindPlayInteractions(state);
// NEW:
bindGridInteractions(playState);
```

(The variable is `state` inside `startSorteggio` — rename the call to `bindGridInteractions(state)`)

- [ ] **Step 6: Add page load wiring at the bottom of the script**

Replace the old `initSetupSlots(4);` call (and the surrounding old wiring) with new wiring at the end of the `<script>` block (before `</script>`):

```javascript
// ── Page load ──────────────────────────────────────────────────
document.body.classList.add('live-play');

// Count buttons
document.querySelectorAll('.count-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const state = window._liveState;
    if (!state || state.phase !== 'setup') return;
    const count = parseInt(btn.dataset.count);
    document.querySelectorAll('.count-btn').forEach(b => {
      b.classList.toggle('ring-2', parseInt(b.dataset.count) === count);
      b.classList.toggle('ring-mtg-accent', parseInt(b.dataset.count) === count);
    });
    changePlayerCount(state, count);
  });
});

// Start button
document.getElementById('setup-start-btn').addEventListener('click', () => {
  const state = window._liveState;
  if (!state || state.phase !== 'setup') return;
  enterPlay(state, true);
});

// Resume / discard
document.getElementById('resume-btn').addEventListener('click', () => {
  enterPlay(getState());
});
document.getElementById('discard-btn').addEventListener('click', () => {
  clearState();
  document.getElementById('resume-banner').style.display = 'none';
  document.getElementById('setup-controls').style.display = '';
  initSetupPhase(4);
});

// Check for a saved play-phase game
const saved = getState();
if (saved && saved.phase === 'play') {
  document.getElementById('resume-banner').style.display = 'block';
  document.getElementById('setup-controls').style.display = 'none';
  window._liveState = saved;
} else {
  initSetupPhase(4);
}
```

- [ ] **Step 7: Full end-to-end browser test**

Start server:
```bash
python run.py
```

Open `/live`:
1. Page loads fullscreen (no nav/footer) ✓
2. Grid shows 4 colored tiles, all in edit mode ✓
3. Center shows player count buttons (4 selected) + disabled "Inizia Partita" ✓
4. Select a player + commander in tile 0, tap OK → tile switches to play (shows 40 HP, name) ✓
5. Do the same for tiles 1, 2, 3 → "Inizia Partita" enables ✓
6. Tap a color swatch → tile background changes immediately ✓
7. Tap "Inizia Partita" → sorteggio animation runs → turn center appears, setup center hides ✓
8. Tap left/right on a tile → HP changes ±1 ✓
9. Tap ✏ on a tile → tile flips to edit mode inline ✓
10. Edit player/commander/color, tap OK → returns to play mode ✓
11. Long press turn number → "Termina partita" button appears ✓
12. Tap "Termina partita" → redirects to `/game/new` pre-filled ✓

Reload `/live` mid-game → resume banner appears in center ✓
Click "Scarta" → fresh setup ✓

- [ ] **Step 8: Commit**

```bash
git add app/templates/live.html
git commit -m "feat(live-v2): inline setup, tile colors, remove edit modal — v2 complete"
```

---

## Self-review

**Spec coverage:**
- ✅ Setup integrated in tile grid (§ "Fase setup nuova")
- ✅ Tile-editing state (form inside tile, rotated) vs tile-play state
- ✅ Player count buttons in #setup-center, Start button disabled until all confirmed
- ✅ Resume banner in center replaces setup controls when play state saved
- ✅ TILE_COLORS palette, assignColors shuffle, textColor luminance
- ✅ Color swatches in edit form, selected swatch highlighted with border-color:currentColor
- ✅ slot.color + slot.confirmed in state
- ✅ Edit during play uses same inline tile form (setTileEditMode / handleTileOk)
- ✅ #edit-modal removed, #live-setup removed, initSetupSlots/validateSetup/openEditModal removed

**No placeholders:** All code blocks are complete.

**Type consistency:**
- `makeSetupState` → returns state with `phase:'setup'`, 6 slots with `color` and `confirmed`
- `makePlayState` → returns same state with `phase:'play'`
- `buildGrid` reads `slot.color` and `slot.confirmed` — both set by `makeSetupState`
- `handleTileOk` sets `slot.confirmed = true` — read by `updateStartBtn`
- `bindGridInteractions` replaces `bindPlayInteractions` — all call sites updated
