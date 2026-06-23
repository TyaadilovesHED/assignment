PostgreSQL Deployment Guide

This repo supports both SQLite for local development and PostgreSQL for deployment when `DATABASE_URL` is set.

Requirements
- `psycopg[binary]`
- `DATABASE_URL` environment variable set to your Postgres connection string.

Run locally with SQLite

```bash
pip install -r requirements.txt
python seed_products.py
python -m uvicorn main:app --reload
```

Run locally with Postgres

```bash
export DATABASE_URL=postgres://user:password@host:port/dbname
python seed_products.py
python -m uvicorn main:app --reload
```

Postgres notes
- The app uses `DATABASE_URL` to decide whether to connect to Postgres.
- The seed script creates the `products` table and bulk-inserts 200k rows.
- The app creates the same indexes and supports the same `/products`, `/categories`, `/health`, and `/` routes.

Render / cloud deployment

1. Push the repo to GitHub.
2. Create a Python web service.
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
5. Set `DATABASE_URL` in service environment variables.
6. Deploy and run the seed script against the remote Postgres database.

If you want, I can also add a small `render.yaml` or `docker-compose.yml` file.