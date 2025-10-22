
# Branch Sales App

Simple Flask app to collect daily AM/PM sales and room counts for multiple branches.
Seeded admin and branch accounts are created automatically.

## Pre-seeded accounts
- Admin: **admin** / **admin123**
- Branch users (username format is lowercase with underscores; initial password is `pass123`):
- Jacob Main: username **jacob_main**, password **pass123** (branch)
- Jacob Annex: username **jacob_annex**, password **pass123** (branch)
- Concepcion: username **concepcion**, password **pass123** (branch)
- Legazpi: username **legazpi**, password **pass123** (branch)
- Daet: username **daet**, password **pass123** (branch)
- Pili Main: username **pili_main**, password **pass123** (branch)
- Pili Annex: username **pili_annex**, password **pass123** (branch)
- Diversion: username **diversion**, password **pass123** (branch)
- Tabuc Main: username **tabuc_main**, password **pass123** (branch)
- Tabuc Annex: username **tabuc_annex**, password **pass123** (branch)


## Run locally
1. Create a virtualenv and install requirements:
```
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
2. Run:
```
python app.py
```

## Deploy to Render
1. Push this repo to GitHub.
2. Create a new Web Service on Render:
   - Connect your GitHub repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
3. Set environment variable `SECRET_KEY` in Render for production.

