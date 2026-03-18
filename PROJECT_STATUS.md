# NewsOrbit — Project Status & Live Data Evidence

> **Status: RUNNING ✅** — Flask server live at `http://localhost:5000`

---

## What the Project Does

**NewsOrbit** is a Global Intelligence Dashboard built on top of the [GDELT Project](https://www.gdeltproject.org/). It:

1. Queries the GDELT database (versions 1.0 and 2.0) via the `gdeltPyR` Python library
2. Returns structured event data — geopolitical events, news mentions, and knowledge graph entries
3. Classifies events into domains: `Politics`, `Security`, `Finance`, `Diplomacy`, `Society`, `Economy`, `Health`, `Environment`, `Business`, `Science`
4. Extracts trending news URLs ranked by mention count / tone prominence
5. Serves everything through a secured Flask web dashboard

---

## Live Fetch Logs (March 12, 2026)

The following queries were executed and returned real data from the GDELT servers:

| Time (UTC+5:30) | Date Queried | Table | GDELT Version | Records Returned |
|---|---|---|---|---|
| 09:36:32 | 2026 Feb 19 | events | **1.0** | **133,910** |
| 09:41:18 | 2026 Feb 1 | events | **2.0** | **598** |
| 09:42:58 | 2026 Feb 19 | events | **2.0** | **977** |
| 09:43:34 | 2026 Mar 10 | events | **1.0** | **126,772** |
| 09:45:42 | 2026 Feb 1 | events | **1.0** | **66,769** |

All queries returned HTTP `200 OK`. No errors.

---

## Architecture

```
Browser (http://localhost:5000)
        │
        ▼
 Flask App (app.py)
        │
        ├── /login          — Session-based auth (admin / newsOrbit2024)
        ├── /               — Main dashboard (login required)
        ├── /api/query      — POST → runs GDELT search, returns JSON
        └── /api/schema/<t> — GET  → returns column schema for a table
                │
                ▼
        gdeltPyR library
                │
                ▼
    GDELT S3 / Master File List
    (live internet fetch of CSV data)
                │
                ▼
        pandas DataFrame
        (133k–66k rows per query)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Flask + Flask-CORS |
| Data Source | GDELT 1.0 (daily) & 2.0 (15-min updates) |
| GDELT Client | `gdeltPyR` |
| Data Processing | `pandas` |
| Auth | Session-based (Flask `session`) |
| Frontend | Jinja2 templates (`templates/index.html`) |
| Python | 3.x (`.venv`) |

---

## How Data Is Fetched

1. User submits a query via the dashboard (date + table + version).
2. `POST /api/query` receives JSON: `{ "date": "2026 Feb 19", "table": "events", "version": 1 }`.
3. `gdelt.gdelt(version=1).Search(date, table=table, output='pd')` fetches the master file list from GDELT, downloads the matching CSV(s) over HTTP, and returns a pandas DataFrame.
4. The app:
   - Trims to a **10-row sample** for the UI table
   - Computes **trending news** (top 7 URLs ranked by `NumMentions`)
   - Computes **per-table statistics**
   - Attaches **metadata** (fetch timestamp, source label, `live_data: true`)
5. Returns everything as JSON to the frontend.

---

## Running the Project

```powershell
# Activate the virtual environment
& "C:\Users\satya\Downloads\gdeltPyR-master\.venv\Scripts\Activate.ps1"

# Start the dashboard
cd "C:\Users\satya\Downloads\gdeltPyR-master\gdeltPyR-master"
python app.py
```

Then open: **http://localhost:5000**  
Login: `admin` / `newsOrbit2024`

---

## Sample API Response Shape

```json
{
  "total_records": 133910,
  "columns": ["GLOBALEVENTID", "SQLDATE", "Actor1Name", "Actor2Name", "EventCode", ...],
  "sample_data": [ { "...": "..." } ],
  "trending_news": [
    {
      "title": "UNITED STATES — RUSSIA",
      "url": "https://example.com/article",
      "source": "reuters.com",
      "country": "USA",
      "mentions": 42,
      "goldstein": 3.5,
      "domain": "Diplomacy",
      "quad_icon": "🤝",
      "date": "20260219"
    }
  ],
  "stats": { "total_records": 133910, "shape": [133910, 61] },
  "metadata": {
    "query_date": "2026 Feb 19",
    "table": "events",
    "version": "GDELT 1.0",
    "fetched_at": "2026-03-12T09:36:32",
    "source": "GDELT 1.0 (daily updates)",
    "live_data": true
  }
}
```

---

*Generated automatically on March 12, 2026. Server confirmed live with 5 successful GDELT fetches.*
