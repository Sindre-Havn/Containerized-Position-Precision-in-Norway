# Estimation of DOP Along Norwegian Roads, Taking in Terrain as a Factor

Første gang man Cloner prosjektet må man også følge stegene under Laste ned høydedata og Laste ned ephemeris fra CDDIS. Når dette er på plass, skal det funke å starte prosjekte slik som under starte backend og starte frontend.

## Systemkrav

Python ≥ 3.10

Node.js ≥ 18.x

Git installert

Anbefalt editor: VS Code

## Starte backend

1. Start en terminal

2. Naviger til backend-mappen:

```bash
 cd backend
```

3. Opprett et virtuelt miljø:

- <b> Mac/Linux: </b>
```bash
python3 -m venv venv
```

- <b>Windows (PowerShell):</b>
```bash
python -m venv venv
```


4. Aktiver det virtuelle miljøet:

- <b> Mac/Linux: </b>
```bash
source venv/bin/activate
```
- <b>Windows (PowerShell):</b>
```bash
.\venv\Scripts\Activate.ps1
```

5. Installer alle avhengigheter:
```bash
pip install -r requirements.txt
```


6. Start Flask-serveren:
```bash
python app.py
```

### Starte Frontend

1. Start en ny terminal

2. Naviger til frontend-mappen:
```bash
cd frontend
```

3. Installer nødvendige pakker:
```bash
npm install
```

4. Start frontend-applikasjonen:
```bash
 npm start
```
## Laste ned høydedata


Dette prosjektet er satt opp til å bruke **landsdekkende høydedata (DTM 10m)** fra [hoydedata.no](https://hoydedata.no/LaserInnsyn2/). Følg stegene nedenfor for å laste ned og bruke datasettet:

### Trinn for nedlasting:

1. Gå til: [https://hoydedata.no/LaserInnsyn2](https://hoydedata.no/LaserInnsyn2/)
2. Klikk på **meny-ikonet** (øverst til venstre).
3. Velg **Eksport**.
4. Velg type eksport:
   - **Landsdekkende** (anbefalt og forventet av koden)
   - Du kan også velge **lokal eksport** hvis du tilpasser koden selv.
5. I eksportpanelet:
   - Velg **Nasjonal høydemodell (DTM)**.
   - Velg **Oppløsning: 10 meter**.
     - *NB: Koden er laget for 10 m-data. Ved 1 m må du endre terrengberegningssteget i `find_dop_on_point()` fra 5 m til lavere.*
   - Velg **UTM Sone 33**.
6. Klikk **Klargjør eksport**, fyll inn e-postadresse og last ned filen når den kommer.

---

### Når datasettet er lastet ned:

1. Pakk ut `.zip`-filen du får tilsendt.
2. Flytt hele mappen til prosjektets mappe:
   ```bash
   backend/data/dtm10/




## Laste ned ephemeris fra CDDIS

For å laste ned GNSS-ephemeris (RINEX/BRDC) fra [CDDIS (NASA's Crustal Dynamics Data Information System)](https://cddis.nasa.gov), må du:

1. Opprette en Earthdata-bruker
2. Lage en `.netrc`-fil i hjemmemappen din
3. Bruke `wget` eller `curl` for nedlasting

---

### 1. Opprett Earthdata-bruker

1. Gå til: https://urs.earthdata.nasa.gov/users/new
2. Opprett en konto
3. Aktiver kontoen via e-post

---

### 2. Sett opp `.netrc`-fil

#### Plassering:
- På **Mac/Linux**: `~/.netrc`
- På **Windows (WSL/git bash)**: `C:\Users\DittBrukernavn\.netrc` eller bruk WSL sitt `~/.netrc`

#### Innhold:

> _Bytt ut `brukernavn` og `passord` med din Earthdata-pålogging_

```
machine urs.earthdata.nasa.gov
login brukernavn
password passord
```

---

#### Viktig! Rettigheter må være sikre

- På Linux/macOS:
```bash
chmod 600 ~/.netrc
```

---

### 3. Last ned filer med `wget` eller `curl`

#### Eksempel med `wget`:
```bash
wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies \
https://cddis.nasa.gov/archive/gnss/data/daily/2024/brdc/brdc1230.24n.Z
```

- `--load-cookies` og `--save-cookies` trengs for autentisering
- Du må kanskje pakke ut `.Z`-filene med `uncompress` etterpå:
```bash
uncompress brdc1230.24n.Z
```

---

