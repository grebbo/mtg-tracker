# Live Counter v2 — Setup inline + Colori tile
**Data:** 2026-05-23  
**Stato:** approvato

---

## Panoramica

Due modifiche al live counter esistente (`app/templates/live.html`):

1. **Setup integrato nella griglia** — la schermata di setup separata viene sostituita da un setup direttamente sulle tile nella loro posizione finale (già ruotate). Il form appare centrato dentro la tile stessa, non in un modale overlay.

2. **Colori tile** — ogni tile ha un colore di sfondo selezionabile dall'utente, assegnato casualmente all'avvio. Il form di edit (sia durante il setup che durante la partita) include una striscia di swatches colore.

---

## Modifiche ai file

| File | Operazione | Descrizione |
|---|---|---|
| `app/templates/live.html` | Modifica | Rimozione setup screen separata, aggiunta fase setup inline, colori tile, edit inline |

---

## Stato delle tile

Ogni tile ora ha **due stati visivi** gestiti da JS:

### Stato `edit`
Il contenuto della tile mostra un form centrato (già ruotato con il contenuto):
- Select Giocatore
- Select Commander
- Striscia di 8 swatches colore (pallini cliccabili)
- Bottone "OK" per confermare

### Stato `play`
Il contenuto normale della tile:
- Numero HP grande
- Nome · Commander (piccolo, sotto)
- Sol Ring toggle (angolo)
- Icona matita (angolo) → mette la tile in stato `edit`

---

## Fase setup (nuova)

`phase: 'setup'` è il nuovo stato iniziale.

**Al caricamento di `/live`:**
- La griglia è immediatamente visibile con layout e rotazioni finali
- Tutte le tile partono in stato `edit`
- Il centro mostra: bottoni numero giocatori (2–6) + bottone "Inizia Partita" (disabilitato finché non tutte le tile sono confermate)
- Se c'è uno stato salvato in localStorage con `phase: 'play'`, mostrare banner di resume nel centro al posto dei bottoni

**Flusso setup:**
1. L'utente seleziona il numero di giocatori dal centro → le tile si mostrano/nascondono. Le tile già confermate restano in stato `play`; le tile appena rese visibili partono in stato `edit`
2. Ogni giocatore compila la propria tile (form ruotato verso di lui) e preme OK
3. La tile confermata passa in stato `play` con HP = 40
4. Quando tutte le tile visibili sono in stato `play`, il bottone "Inizia Partita" si attiva
5. Tap "Inizia Partita" → sorteggio → fase `play` (come prima)

**Modifica allo stato slot:** aggiungere campo `color` (stringa hex). Viene assegnato casualmente dalla palette all'avvio del setup.

---

## Edit inline durante la partita

Il flusso è identico al setup:
- Tap icona matita su una tile → la tile passa in stato `edit` con valori attuali pre-popolati
- L'utente modifica player, commander e/o colore
- Tap OK → la tile torna in stato `play`

**Il modale `#edit-modal` esistente viene rimosso** — non più necessario.

---

## Colori tile

### Palette

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
```

### Assegnazione casuale

All'avvio del setup, i colori vengono assegnati ai slot in ordine ciclico dopo uno shuffle della palette: `TILE_COLORS[(shuffleIndex + slotIndex) % TILE_COLORS.length]`.

### Testo adattivo

Il colore del testo (bianco o nero) si calcola dalla luminanza del colore di sfondo:

```javascript
function textColor(hex) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return (0.299*r + 0.587*g + 0.114*b) > 128 ? '#000000' : '#ffffff';
}
```

### Persistenza

Il campo `color` è salvato in `localStorage` come parte dello stato slot.

---

## Struttura CSS aggiuntiva

```css
/* Tile in stato edit */
.tile.tile-editing .tile-play-content { display: none; }
.tile.tile-editing .tile-edit-content { display: flex; }
.tile:not(.tile-editing) .tile-play-content { display: flex; }
.tile:not(.tile-editing) .tile-edit-content { display: none; }

/* Edit content: form centrato nella tile */
.tile-edit-content {
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem;
  width: 100%;
  height: 100%;
}

/* Color swatches */
.color-swatch {
  width: 1.1rem; height: 1.1rem;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
}
.color-swatch.selected { border-color: inherit; /* bianco o nero adattivo */ }
```

---

## Rimozioni

- Elemento `#live-setup` (l'intera schermata separata) → rimosso
- Elemento `#edit-modal` → rimosso
- Funzione `initSetupSlots()` → rimossa
- Funzione `openEditModal()` → rimossa
- CSS per `#live-setup`, `#edit-modal`, `.seat-slot` → rimosso

---

## Stato slot aggiornato

```javascript
{
  playerId: number,
  playerName: string,
  commanderId: number,
  commanderName: string,
  hp: number,           // 40 al setup, poi varia
  solRing: boolean,
  eliminated: boolean,
  turnEliminated: null | number,
  color: string,        // NEW: hex color
  confirmed: boolean,   // NEW: true dopo OK nel setup
}
```
