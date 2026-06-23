Deployment notes — quick guide

Goal: Host the backend and DB for a public demo.

Options
- Backend: Render (free tier) or Fly/railway.
- Database: Neon or Supabase Postgres (free tiers available).

High-level steps (recommended production changes)
1. Replace SQLite with PostgreSQL
   - Add `psycopg[binary]` or `asyncpg` and use `DATABASE_URL` env var.
   - Use SQLAlchemy or a lightweight data layer and run migrations (Alembic).
   - Update seed script to bulk-insert into Postgres using `executemany` or `COPY`.

2. Prepare app for Render
   - Create a `requirements.txt`:
     ```
     fastapi
     uvicorn[standard]
     psycopg[binary]
     ```
   - Use startup command: `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
   - Set `DATABASE_URL` in Render's environmental variables.

3. Setup Postgres (Neon/Supabase)
   - Create a new database.
   - Run schema SQL (`CREATE TABLE products (...)`), then run the adapted seed script.

4. Adjust indexes
   - Run: `CREATE INDEX idx_products_created_at_id ON products (created_at DESC, id DESC);`
   - And: `CREATE INDEX idx_products_category_created_at_id ON products (category, created_at DESC, id DESC);`

5. Health checks & logging
   - Configure a `/health` endpoint (already present).
   - Add basic logging and monitoring in Render settings.

Notes & tradeoffs
- Using Postgres gives better concurrency, backups, and ability to scale beyond one machine.
- For very high throughput, consider read replicas or a dedicated search index for complex queries.

Quick deploy (Render)
1. Push repo to GitHub.
2. Create a new Web Service in Render that points to the repo.
3. Select Environment: Python, Build Command: `pip install -r requirements.txt`, Start Command: `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`.
4. Add `DATABASE_URL` and other env vars.
5. After the service is live, connect to Postgres and run the seed/migration.

If you want, I can help adapt `seed_products.py` to target Postgres and create a `requirements.txt` and `Procfile` for Render.