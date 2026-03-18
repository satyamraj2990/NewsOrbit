# NewsOrbit — Architecture & How It Works

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                               │
│                    http://localhost:5000                             │
│                                                                     │
│   Login Page ──► Main Dashboard ──► Query Form ──► Results View    │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP (REST)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FLASK WEB SERVER                               │
│                          app.py                                     │
│                                                                     │
│   /login            /logout           /                             │
│   /api/query  ◄──── POST JSON ──────► /api/schema/<table>          │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ Python call
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    gdeltPyR LIBRARY                                 │
│                   gdelt/base.py                                     │
│                                                                     │
│   gdelt.gdelt(version=1 or 2)                                       │
│      └── .Search(date, table, output='pd')                          │
└──────┬──────────────────────────────────────────┬───────────────────┘
       │ builds URLs                              │ returns
       ▼                                          ▼
┌──────────────────┐                  ┌────────────────────────────┐
│  vectorizingFuncs│                  │     pandas DataFrame       │
│  _urlBuilder()   │                  │  (up to 133,000+ rows)    │
│                  │                  └────────────────────────────┘
│  Constructs CSV  │
│  URLs pointing   │
│  to GDELT S3     │
└──────┬───────────┘
       │ HTTP GET (parallel)
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│               GDELT DATA SERVERS (Internet)                         │
│                                                                     │
│   GDELT 1.0:  http://data.gdeltproject.org/events/                  │
│   GDELT 2.0:  http://data.gdeltproject.org/gdeltv2/                 │
│                                                                     │
│   Files delivered as compressed CSV (.CSV.zip)                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Frontend (Browser)

| File | Role |
|---|---|
| `templates/login.html` | Login form — session-based auth |
| `templates/index.html` | Main dashboard UI (charts, tables, news feed) |
| `static/images/` | Logo and static assets |

User actions flow:
1. `GET /` → redirected to `/login` if no session
2. Submit credentials → `POST /login` → session set → redirect to `/`
3. Select date, table, version → `POST /api/query` → render results

---

### 2. Flask Application (`app.py`)

**Routes:**

| Route | Method | Description |
|---|---|---|
| `/login` | GET / POST | Auth page; sets `session['logged_in']` |
| `/logout` | GET | Clears session, redirects to login |
| `/` | GET | Serves dashboard (login required) |
| `/api/query` | POST | Main data endpoint — queries GDELT |
| `/api/schema/<table>` | GET | Returns column schema for a table |

**Key logic in `/api/query`:**

```
1. Parse JSON body: { date, table, version }
2. Lazy-load gdelt instance (gd1 or gd2)
3. Call gd.Search(date, table=table, output='pd')
4. If 0 rows → return 404 with suggested dates
5. Otherwise:
   a. Clean NaN values
   b. Build trending_news  → get_trending_news(results, table)
   c. Build stats          → get_statistics(results, table)
   d. Return JSON with: total_records, columns, sample_data (10 rows),
                        trending_news, stats, metadata
```

**Session security:**
- `login_required` decorator wraps protected routes
- Secret key used for session cookie signing

---

### 3. gdeltPyR Library (`gdelt/`)

```
gdelt/
├── __init__.py          ← exposes gdelt.gdelt class
├── base.py              ← core Search() method + NoDaemonProcessPool
├── dateFuncs.py         ← _dateRanger(), _gdeltRangeString()
├── vectorizingFuncs.py  ← _urlBuilder() constructs CSV download URLs
├── parallel.py          ← _mp_worker() downloads & parses each CSV
├── multipdf.py          ← _parallelize_dataframe() merges chunks
├── extractors.py        ← column extraction helpers
├── getHeaders.py        ← column name lists for each table type
├── inputChecks.py       ← validates date inputs
└── helpers.py           ← CAMEO codes, table info
```

**`Search()` execution flow:**

```
Search("2026 Feb 19", table="events", version=1)
        │
        ├─ inputChecks._date_input_check()      validate & normalise date
        ├─ dateFuncs._dateRanger()              expand date range
        ├─ dateFuncs._gdeltRangeString()        format for URL building
        ├─ vectorizingFuncs._urlBuilder()       generate list of CSV URLs
        │
        │   e.g. http://data.gdeltproject.org/events/20260219.export.CSV.zip
        │
        ├─ parallel._mp_worker(url)             [runs in thread pool]
        │       └── requests.get(url)           download .CSV.zip
        │       └── pd.read_csv(BytesIO(...))   decompress & parse
        │
        └─ multipdf._parallelize_dataframe()    concat all chunks
                └── returns single pandas DataFrame
```

---

### 4. GDELT Data Source

GDELT provides two versions:

| | GDELT 1.0 | GDELT 2.0 |
|---|---|---|
| Update frequency | Daily | Every 15 minutes |
| Base URL | `data.gdeltproject.org/events/` | `data.gdeltproject.org/gdeltv2/` |
| File format | `YYYYMMDD.export.CSV.zip` | `YYYYMMDDHHMMSS.export.CSV.zip` |
| Typical size | 60,000–134,000 rows/day | 600–1,000 rows/15 min |
| Tables | `events` | `events`, `mentions`, `gkg` |

**CAMEO Event Codes** (loaded from `data/cameoCodes.json`) map numeric codes to human-readable event names and Goldstein conflict-cooperation scores.

---

### 5. Data Processing Pipeline (per query)

```
Raw DataFrame (133,910 rows for events v1)
        │
        ├── get_trending_news()
        │       ├── Filter rows where SOURCEURL starts with 'http'
        │       ├── Sort by NumMentions DESC
        │       ├── Deduplicate URLs
        │       └── Return top 7 as [{title, url, source, country,
        │                             mentions, goldstein, domain,
        │                             quad_icon, date}]
        │
        ├── get_statistics()
        │       ├── [events]  top countries, actors, event categories,
        │       │             Goldstein min/avg/max, CAMEO code freq,
        │       │             hierarchical Country→Domain→Events tree
        │       ├── [gkg]     top sources, themes, persons, orgs,
        │       │             avg tone, article cards
        │       └── [mentions] unique events, avg/max mentions,
        │                      source breakdown, mention types, confidence
        │
        └── classify_event_domain()   [per-row, called during stats]
                ├── Uses CAMEO EventCode prefix (01–20)
                ├── Checks Actor names for keywords
                └── Returns one of: Politics, Diplomacy, Security,
                                    Economy, Finance, Society, Health,
                                    Environment, Business, Science, General
```

---

### 6. Authentication Flow

```
Browser                Flask
   │                     │
   │── GET /  ──────────►│
   │                     │── session.get('logged_in') == False
   │◄── 302 /login ──────│
   │                     │
   │── GET /login ───────►│
   │◄── 200 login.html ──│
   │                     │
   │── POST /login ──────►│
   │   {user, pass}       │── compare with DASHBOARD_USER / DASHBOARD_PASS
   │                     │── session['logged_in'] = True
   │◄── 302 / ───────────│
   │                     │
   │── GET / ────────────►│
   │◄── 200 index.html ──│
```

---

### 7. Concurrency Model

- GDELT 2.0 can return multiple 15-minute file URLs for a date range
- `gdeltPyR` uses `concurrent.futures` / `multiprocessing.pool` to download multiple CSVs in **parallel**
- `NoDaemonProcessPool` (subclass of `multiprocessing.pool.Pool`) allows nested process pools
- All chunks are concatenated into a single DataFrame via `_parallelize_dataframe()`

---

## Data Flow Diagram (End-to-End)

```
User Input: "2026 Feb 19 | events | v1"
        │
        ▼
POST /api/query
{ "date": "2026 Feb 19", "table": "events", "version": 1 }
        │
        ▼
gdelt.gdelt(version=1).Search("2026 Feb 19", table="events", output="pd")
        │
        ▼
URL: http://data.gdeltproject.org/events/20260219.export.CSV.zip
        │
        ▼
requests.get(url)  →  decompress ZIP  →  pd.read_csv()
        │
        ▼
DataFrame: 133,910 rows × 61 columns
        │
        ├──► trending_news  [top 7 URLs by NumMentions]
        ├──► statistics     [countries, actors, Goldstein, CAMEO codes]
        └──► sample_data    [first 10 rows, NaN → ""]
        │
        ▼
JSON Response → Browser → Dashboard renders charts & news feed
```

---

## Technology Stack

```
Layer               Technology
─────────────────── ──────────────────────────────────
Web server          Flask 2.x + Flask-CORS
Templating          Jinja2
Auth                Flask session (signed cookie)
Data fetch          requests (HTTP GET to GDELT S3)
Parallelism         concurrent.futures + multiprocessing
Data wrangling      pandas, numpy
Date parsing        python-dateutil
Event taxonomy      CAMEO codes (cameoCodes.json)
Runtime             Python 3.x (.venv)
```

---

*Architecture documented on March 12, 2026 — server confirmed live with successful GDELT fetches.*
