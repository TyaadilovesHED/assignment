Interview Talking Sheet — Verbatim Answers

Opening summary (15–30s):
"I built a small backend in Python using FastAPI and a seeded SQLite dataset of 200,000 products to demonstrate stable, fast pagination and category filtering. The service orders products newest-first and uses cursor-based pagination with a session snapshot to ensure consistent pages while data changes. A minimal UI is included to demo the flow."

What the service does (30–45s):
"The API returns products ordered by `created_at DESC, id DESC` (newest-first), supports filtering by `category`, and returns pages using a cursor. The cursor contains a `snapshot` timestamp so the entire paginated session uses a consistent view of the dataset — new products created after the first request won’t appear mid-session."

Why cursor pagination (30–45s):
"Offset pagination requires skipping rows on each request which is slow on large tables and can return duplicates or miss rows when the dataset changes. Cursor pagination remembers the last returned row and asks the DB for rows after that marker; with proper indexes, it's O(page_size) and stable."

Deterministic ordering (20–30s):
"Ordering by `created_at DESC` alone can tie when timestamps are identical. Appending `id DESC` makes sorting deterministic so the pagination boundary is exact and repeatable."

Snapshot behavior (30–45s):
"The first page encodes a `snapshot` (UTC timestamp). Subsequent pages restrict to `created_at <= snapshot`. Any items created after the snapshot are excluded from that session, preventing duplicates or missed items while browsing."

Cursor contents (10–20s):
"The cursor is a base64-encoded JSON object containing `snapshot`, `category`, `last_created_at`, and `last_id`. The UI sends it back to fetch the next page."

Indexes & performance (20–30s):
"I added indexes on `(created_at DESC, id DESC)` and `(category, created_at DESC, id DESC)` so the DB can use an index-only or index-assisted scan to return pages quickly without scanning the whole table."

Data generation (20–30s):
"`seed_products.py` produces 200k products and bulk-inserts them using `executemany(...)`, which is much faster than individual inserts. The created_at values are synthetic but realistic enough to exercise pagination ordering."

Live demo script (60–90s):
1. Start the server and open the UI at `/`.
2. Load page size 25 and click Load; show the first page.
3. Click Next a few times (demonstrates `next_cursor` and stability).
4. Insert a new product with current timestamp (or run a small script) and show it does not appear in the active paginated session because of the snapshot.

What I would improve with more time (30–60s):
- Switch to PostgreSQL/Neon for production and add migrations.
- Add authenticated write endpoints and automated tests.
- Add server-side cursors, TTL on cursors, and a previous-page feature.
- Add full-text search and richer filters in the UI.

How I used AI (one-liner):
"AI helped scaffold the API, suggested pagination patterns and UI layout; I validated and corrected the code manually to ensure correctness, especially around cursor encoding and snapshot behavior."