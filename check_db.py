import os
import psycopg

url = os.environ.get("DATABASE_URL")
if not url:
    raise SystemExit("Set DATABASE_URL env var first")

with psycopg.connect(url, autocommit=True) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS cnt FROM products;")
        print('Total products:', cur.fetchone()[0])
        
        cur.execute("SELECT id, name, category, price FROM products ORDER BY id DESC LIMIT 5;")
        print("\nLast 5 products:")
        for row in cur.fetchall():
            print(f"  {row}")