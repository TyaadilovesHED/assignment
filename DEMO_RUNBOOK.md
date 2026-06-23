Demo Runbook — What to run and why

Prereqs
- Python 3.12 installed
- Repo cloned and current working directory is the repo root

Commands

1) Seed the database (creates `products.db` with 200k rows)

```bash
C:/Python312/python.exe seed_products.py
```

2) Start the FastAPI server

```bash
C:/Python312/python.exe -m uvicorn main:app --reload
```

3) Open the browser UI

- Navigate to: http://127.0.0.1:8000/

Live demo steps

1. Click "Load products" (default: All categories, page size 25). This performs `GET /products?page_size=25` and displays the first page.
2. Click "Next page" a few times to show the cursor advancing (each request returns a new `next_cursor`).
3. To illustrate snapshot consistency:
   - Open a second terminal and insert a new product with `created_at = now`:

```python
# insert_new_product.py (one-off test)
import sqlite3
from datetime import datetime
conn = sqlite3.connect('products.db')
cur = conn.cursor()
cur.execute("INSERT INTO products (name, category, price, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("NEW DEMO ITEM", "Electronics", 9.99, datetime.utcnow().isoformat(timespec='microseconds'), datetime.utcnow().isoformat(timespec='microseconds')))
conn.commit()
conn.close()
```

   - Run it while the UI session is active and notice the new item does NOT appear in the current pagination session (because `snapshot` was captured on the first page).

4. Show category filtering: select a category from the dropdown and click Load; demonstrate paginating inside a category.

API sanity checks (alternative to UI)

```bash
# first page
curl 'http://127.0.0.1:8000/products?page_size=5'
# second page (use next_cursor from response)
curl "http://127.0.0.1:8000/products?page_size=5&cursor=<PASTE_CURSOR>"
# categories
curl 'http://127.0.0.1:8000/categories'
```

What to highlight verbally
- Deterministic ordering: `created_at DESC, id DESC`.
- Snapshot: new rows after snapshot are excluded from the session.
- Cursor encodes last row marker so the DB can resume scanning efficiently without OFFSET.

Notes
- SQLite is used for simplicity in this demo; production should use PostgreSQL/Neon and proper migrations.