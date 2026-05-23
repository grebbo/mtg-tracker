# Live Counter — Design Spec
**Data:** 2026-05-23  
**Stato:** approvato

---

## Panoramica

Nuova pagina `/live` che funge da life counter durante le partite di Commander. Consente di tracciare punti vita, turni ed eliminazioni in tempo reale, poi trasferisce i dati raccolti al form `/game/new` pre-compilato per completare la registrazione.

---

## Architettura

**Approccio:** client-side con `localStorage` per la persistenza dello stato durante la partita.

**File nuovi:**
- `app/templates/live.html` — pagina unica con due fasi (setup / play) gestite via JS

**File modificati:**
- `app/routes.py` — aggiunta route `GET /live` che passa `players` e `commanders` al template
- `app/templates/base.html` — aggiunta voce "Live" nella navbar

**Nessun nuovo modello DB.** Il counter non scrive nel database. I dati entrano nel DB solo quando l'utente completa il form `/game/new` come nel flusso attuale.

**Stato localStorage:**  
Chiave `mtg_live_game`, oggetto JSON con fase corrente, configurazione giocatori, punti vita, turno corrente, timestamp. Scritto ad ogni modifica, cancellato solo dopo il submit del form `/game/new`.

**Handoff sessionStorage:**  
Al termine partita, i dati vengono scritti in `sessionStorage` (chiave `mtg_prefill`). `/game/new` li legge al caricamento e pre-compila il form, poi cancella la chiave.

---

## Flusso

```
/live (setup) → animazione sorteggio → /live (play) → fine partita → /game/new (pre-compilato)
```

Se l'utente esce da `/live` senza terminare la partita, `localStorage` conserva lo stato. Al rientro su `/live` viene proposto di riprendere la partita in corso.

---

## Fase 1: Setup

**Elementi:**
- Selector numero giocatori (2–6) che mostra/nasconde gli slot
- Per ogni slot (= posto al tavolo):
  - Select giocatore (dai Player nel DB)
  - Select commander (dai Commander nel DB, con color identity)
  - I posti sono mostrati visivamente come sedute attorno a un tavolo circolare
- Bottone **"Inizia partita"** — attivo solo se tutti gli slot hanno giocatore + commander

**Ordine di turno:** l'indice dello slot = ordine di turno. Lo slot 1 è il posto in basso (vicino a chi tiene il device), si procede in senso orario.

**Punti vita iniziali:** sempre 40 (Commander standard).

---

## Fase 2: Animazione sorteggio

Al tap su "Inizia partita" la pagina entra in fullscreen e parte l'animazione:
- Le tile si illuminano in sequenza (ciclo 2–3 volte, poi rallenta)
- La tile estratta rimane illuminata: è il primo giocatore
- Dopo 1–2 secondi la partita inizia

---

## Fase 3: Play screen

### Layout generale

**Fullscreen** (`position: fixed; 100vw 100vh`, Web Fullscreen API con fallback). Navbar e footer scompaiono.

Tile disposte attorno allo schermo, ognuna ruotata verso il giocatore fisico:

| N. giocatori | Disposizione |
|---|---|
| 2 | 1 sopra (180°) + 1 sotto |
| 3 | 2 sopra (180°) + 1 sotto centro |
| 4 | 2 sopra (180°) + 2 sotto |
| 5 | 2 sopra (180°) + 1 destra (90°) + 2 sotto |
| 6 | 2 sopra (180°) + 1 sinistra (270°) + 1 destra (90°) + 2 sotto |

**Centro schermo:** solo il numero di turno (grande), con `−` / `+` ai lati per incrementare. Nessun nome del giocatore attivo.

### Tile vita

- Numero PV grande al centro
- Tap **metà sinistra** → `−1`; tap **metà destra** → `+1`
- **Pressione lunga** → input numerico libero (per variazioni grandi)
- **Angolo superiore della tile:** icona Sol Ring (toggle on/off) + icona matita (edit nome/commander in-play)
- **Eliminazione:** quando PV ≤ 0 la tile diventa grigia/sbarrata e viene registrato automaticamente il turno corrente come `turn_eliminated`. Il giocatore resta visibile sulla griglia ma visivamente "spento"

### Numero di turno (centro)

- Tap `+`/`−` ai lati → incrementa/decrementa
- Tap diretto sul numero → input numerico inline (per correggere dimenticanze)
- **Pressione lunga sul numero** → appare il bottone **"Termina partita"** sotto; il numero rimane editabile. Pressione lunga di nuovo o tap fuori → si chiude senza terminare

### Fine partita automatica

Quando scende a 0 l'ultimo avversario (un solo giocatore con PV > 0), appare un overlay centrale:
> *"Rimane solo [nome]. Terminare la partita?"*

Due azioni: **Conferma** o **Ignora** (per gestire extra turni o recuperi di PV).

---

## Handoff a `/game/new`

Al termine (automatico o manuale), viene scritto in `sessionStorage`:

```json
{
  "date": "2026-05-23",
  "players": [
    {
      "player_id": 2,
      "commander_id": 14,
      "turn_order": 1,
      "sol_ring_t1": true,
      "final_hp": 28,
      "eliminated": false,
      "turn_eliminated": null
    },
    {
      "player_id": 5,
      "commander_id": 7,
      "turn_order": 2,
      "sol_ring_t1": false,
      "final_hp": 0,
      "eliminated": true,
      "turn_eliminated": 9
    }
  ],
  "total_turns": 12,
  "winner_index": 0
}
```

`/game/new` legge `mtg_prefill` da `sessionStorage` al caricamento e pre-compila:
- Data odierna
- Giocatori e commander per slot
- Ordine di turno
- Sol Ring T1
- Turni di eliminazione
- Piazzamento finale (winner_index = finish 1, gli altri ordinati per turn_eliminated decrescente)

**Campi che restano da compilare manualmente:** `victory_condition`, `loss_condition`, `eliminated_by`, `notes`.

`sessionStorage` viene cancellata subito dopo il pre-fill. `localStorage` (`mtg_live_game`) viene cancellata dopo il submit del form.

---

## Stile grafico

- Sfondo nero puro (`#000`) per massimizzare il contrasto in condizioni di luce variabile
- Tile: sfondo scuro neutro, testo bianco grande — nessun colore per colore identity (troppo distraente durante il gioco)
- Tile eliminata: opacità ridotta + overlay con `×`
- Font numerico: sistema monospace o Inter bold, molto grande
- Nessun bordo decorativo, nessun gradiente — minimalismo assoluto
- Palette coerente con il tema esistente (`mtg-bg: #0f1117`, `mtg-card: #1a1d27`) ma adattata al fullscreen
