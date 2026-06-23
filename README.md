# assignment
# CodeVector Internship Take Home Task

This project implements a small backend for browsing products with fast, stable pagination.

## Overview

- Backend: `FastAPI`
- Database: `SQLite` with indexed newest-first ordering
- Pagination: cursor-based with snapshot consistency
- Seed: `seed_products.py` generates and inserts 200,000 products efficiently

## Run locally

1. Create the database and seed products:

```bash
C:/Python312/python.exe seed_products.py
```

2. Start the API server:

```bash
C:/Python312/python.exe -m uvicorn main:app --reload
```

3. Browse products:

- `GET /products?page_size=25`
- `GET /products?category=Electronics&page_size=25`

4. Continue pagination with the returned `next_cursor`.

## Pagination behavior

- Uses `created_at DESC, id DESC` ordering.
- `snapshot` ensures all pages are consistent with the same view of newest products.
- `cursor` stores the last row position so no items are skipped or repeated.

## Notes

- Add new products while browsing: new items are excluded from the active pagination session because the snapshot is fixed at the first request.
- This protects against duplicates or missing items when the data changes during browsing.

## API

- `GET /products`
  - query params: `category`, `page_size`, `cursor`
- `GET /health`

## Improvements with more time

- Add database migrations and a more robust RDBMS such as PostgreSQL for deployment.
- Add full-text search and additional filters.
- Add a lightweight UI to browse and paginate products.
- Deploy to Render or Supabase.
$env:DATABASE_URL="<external-url>"
python seed_products.py