# Deploy NewsOrbit on Vercel

## 1) Import project
- In Vercel, click **Add New... > Project**.
- Select GitHub repo: `satyamraj2990/NewsOrbit`.
- Set **Root Directory** to `gdeltPyR-master`.

## 2) Build/runtime settings
- Framework preset: **Other**.
- Build command: leave empty.
- Output directory: leave empty.

## 3) Environment variables
Set these in Vercel Project Settings > Environment Variables:

- `GEMINI_API_KEY` = your Gemini key (optional but recommended)
- `FLASK_SECRET_KEY` = long random string (required for production)
- `DASHBOARD_USER` = dashboard username (optional)
- `DASHBOARD_PASS` = dashboard password (required)

## 4) Deploy
- Click **Deploy**.
- After deployment, open the generated URL.

## Notes
- `vercel.json` routes all requests to `app.py`.
- `runtime.txt` requests Python 3.11.
- `requirements.txt` is intentionally slim for Vercel compatibility.
- Full legacy dependency list is preserved in `requirements_full.txt`.
