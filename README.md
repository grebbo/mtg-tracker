# MTG Commander Tracker

Web app per tracciare le partite di Magic: The Gathering in formato Commander. Costruita con Flask e SQLite, deployabile su qualsiasi server tramite Docker Compose con connettività Tailscale.

---

## Funzionalità

### Dashboard

La home page aggrega tutte le statistiche del gruppo:

- **Totale partite** giocate
- **Classifica giocatori**: partite, vittorie, win rate, Sol Ring al turno 1
- **Statistiche commander**: partite giocate, vittorie, kill effettuate, win rate
- **Statistiche per identità di colore**: aggregazione per combinazione cromatica e per singolo colore (W/U/B/R/G)
- **Statistiche sulla durata**: turni medi, mediana, minimo e massimo (con info sul vincitore della partita più lunga/corta)
- **Ultime 5 partite**

### Live Counter

→ vedi sezione dedicata più in basso.

### Registrazione partite

Form per inserire una nuova partita con supporto da 2 a 6 giocatori. Per ogni giocatore si registrano:

| Campo | Descrizione |
|---|---|
| Giocatore | Chi ha giocato |
| Commander | Mazzo usato |
| Piazzamento | Posizione finale (1 = vittoria) |
| Ordine di turno | Posizione nel giro |
| Sol Ring T1 | Se ha giocato Sol Ring al primo turno |
| Turno eliminazione | A quale turno è stato eliminato |
| Eliminato da | Quale commander ha causato l'eliminazione |
| Condizione di vittoria | Combat Damage, Commander Damage, Drain/Burn, Poison, Combo, Mill |
| Condizione di sconfitta | Combat Damage, Commander Damage, Drain/Burn, Poison, Concede |
| Note | Testo libero sulla partita |

Le partite esistenti sono modificabili ed eliminabili.

### Storico partite

Elenco paginato (15 per pagina) di tutte le partite in ordine cronologico decrescente, filtrabile per giocatore e/o commander.

### Gestione commander

Pagina dedicata alla gestione del roster di commander con:

- Aggiunta, modifica ed eliminazione di commander
- Selezione dell'identità di colore tramite 5 pulsanti toggle (W/U/B/R/G), composti nell'ordine canonico MTG
- Identità di colore con nomi MTG (es. `UBR` → Grixis)
- Statistiche per commander: partite, vittorie, kill, win rate
- Protezione da eliminazione se il commander ha partite registrate

### Live Counter

Segnapunti fullscreen per giocare dal vivo, accessibile da `/live`.

**Setup inline:**
- La griglia dei giocatori è visibile da subito con il layout finale (tile già ruotate verso ogni giocatore)
- Ogni tile mostra un form di configurazione direttamente al suo interno: selezione giocatore, commander, colore di sfondo, Sol Ring T1
- Il pannello centrale permette di scegliere il numero di giocatori (2–6); il bottone "Inizia Partita" si attiva solo quando tutti i giocatori hanno confermato la propria tile
- Se esiste una partita salvata non terminata, viene proposto un banner di ripresa

**Layout orizzontale (ottimizzato per dispositivi in landscape):**

| Giocatori | Disposizione |
|---|---|
| 2 | Sopra (180°) + sotto (0°) |
| 3 | 2 speculari sinistra top/bottom + 1 destra full-height (270°) |
| 4 | 2×2 simmetrico |
| 5 | 2×2 a sinistra + 1 destra full-height (270°) |
| 6 | 1 sinistra full-height (90°) + 2×2 centro + 1 destra full-height (270°) |

**Fase di gioco:**
- Tap metà sinistra/destra della tile → ±1 PV
- Pressione lunga → input numerico libero
- Pulsante ✏ (angolo esterno della tile, posizione adattiva) → modifica giocatore/commander/colore in-play
- Centro schermo: contatore turni con −/+; pressione lunga sul numero → compare "⌂ Home" (esce dal fullscreen) e "Termina partita"
- Tile eliminata (PV ≤ 0): opacità ridotta, registrazione automatica del turno

**Handoff:** al termine partita i dati vengono scritti in `sessionStorage` e `/game/new` li usa per pre-compilare il form.

### Import / Export Excel

- **Import**: carica un file `.xlsx` per importare partite in blocco
- **Export**: scarica l'intero database in formato `.xlsx`
- Il file Excel viene sincronizzato automaticamente ad ogni modifica

### Debug Excel

Tool diagnostico (`/debug/excel`) per verificare la struttura di un file `.xlsx` prima dell'importazione: mostra header, colonne rilevate e prime righe grezze.

---

## Stack tecnico

- **Backend**: Python 3.12, Flask, SQLAlchemy, Gunicorn
- **Database**: SQLite (file persistito in `/app/data`)
- **Container**: Docker + Docker Compose
- **Rete**: Tailscale (l'app è esposta sulla rete privata con hostname `mtg-tracker`)

---

## Modalità test

La modalità test avvia l'app con un database completamente separato da quello di produzione. Utile per provare funzionalità senza toccare i dati reali.

**Caratteristiche:**
- DB isolato in `data/test/mtg.db` (produzione usa `data/mtg.db`)
- DB sempre azzerato e ri-seedato ad ogni avvio
- Banner arancione visibile in tutte le pagine
- Pulsante **Reset DB** per azzerare il DB mid-session senza riavviare

### Avvio in locale (sviluppo)

```bash
MTG_TEST_MODE=1 python run.py
```

L'app sarà disponibile su `http://localhost:5000`.

### Avvio con Docker Compose

Aggiungi la variabile al file `.env`:

```
MTG_TEST_MODE=1
```

oppure solo per una sessione:

```bash
MTG_TEST_MODE=1 docker compose up --build
```

---

## Deploy

### Prerequisiti

- Docker e Docker Compose installati sul server
- Tailscale installato e attivo sul server
- Una Tailscale Auth Key ([genera qui](https://login.tailscale.com/admin/settings/keys))

### 1 — Copia il progetto sul server

**Via scp** (dal PC Windows, usa l'IP Tailscale del server):

```bash
scp -r "C:\Users\enric\Documents\Projects\mtg-tracker" user@<tailscale-ip>:~/mtg-tracker
```

**Via rsync** (più efficiente per aggiornamenti futuri):

```bash
rsync -avz "C:\Users\enric\Documents\Projects\mtg-tracker/" user@<tailscale-ip>:~/mtg-tracker/
```

**Via git** (se il repo è su GitHub/GitLab):

```bash
git clone <url-repo> ~/mtg-tracker
```

### 2 — Crea il file `.env`

Sul server, dentro la cartella del progetto:

```bash
cd ~/mtg-tracker
cat > .env << 'EOF'
TS_AUTHKEY=tskey-auth-XXXXXXXXXXXXX
EOF
```

> La Auth Key si genera dall'[admin panel di Tailscale](https://login.tailscale.com/admin/settings/keys). Abilita **Reusable** per evitare di rigenerarla ad ogni riavvio.

### 3 — Crea la cartella `data`

```bash
mkdir -p ~/mtg-tracker/data
```

Questa cartella persiste il database SQLite e i file Excel fuori dal container. Non viene mai eliminata da Docker.

### 4 — Avvia i container

```bash
cd ~/mtg-tracker
docker compose up -d --build
```

Al primo avvio `--build` costruisce l'immagine dall'immagine base `python:3.12-slim`. Nei riavvii successivi si può omettere se il codice non è cambiato.

### 5 — Verifica

```bash
docker compose ps
```

Dopo qualche secondo il container `tailscale` si registra sulla rete Tailscale con hostname **mtg-tracker**. L'app è raggiungibile da qualsiasi dispositivo nella rete Tailscale all'indirizzo:

```
http://mtg-tracker:5000
```

oppure tramite IP Tailscale del server:

```
http://100.x.x.x:5000
```

---

## Comandi utili post-deploy

### Stato e log

```bash
# Stato dei container
docker compose ps

# Log in tempo reale
docker compose logs -f

# Log solo dell'app
docker compose logs -f app
```

### Aggiornamento dopo modifiche al codice

```bash
cd ~/mtg-tracker
git pull                          # se usi git
docker compose up -d --build app  # ricostruisce solo il container dell'app
```

### Stop e riavvio

```bash
# Ferma senza rimuovere i dati
docker compose stop

# Ferma e rimuove i container (i dati in ./data sono al sicuro)
docker compose down

# Riavvio completo
docker compose up -d
```

### Backup del database

```bash
cp ~/mtg-tracker/data/mtg.db ~/backup-mtg-$(date +%Y%m%d).db
```

### Accesso alla shell del container

```bash
docker compose exec app bash
```

### Reset completo (attenzione: elimina tutti i dati)

```bash
docker compose down
rm -rf ~/mtg-tracker/data
mkdir ~/mtg-tracker/data
docker compose up -d --build
```
