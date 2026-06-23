from __future__ import annotations

import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import psycopg
from psycopg.rows import dict_row

DB_PATH = Path(__file__).with_name("products.db")
DATABASE_URL = os.environ.get("DATABASE_URL")
CATEGORIES = [
    "Electronics",
    "Home",
    "Books",
    "Garden",
    "Sports",
    "Fashion",
    "Toys",
    "Health",
    "Automotive",
]


def chunks(iterable: Iterable[str], size: int) -> Iterable[list[str]]:
    batch: list[str] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def generate_products(total: int = 200_000) -> list[tuple[str, str, float, str, str]]:
    random.seed(42)
    now = datetime.utcnow()
    products: list[tuple[str, str, float, str, str]] = []

    for idx in range(total):
        category = random.choice(CATEGORIES)
        created_at = now - timedelta(seconds=idx // 2)
        updated_at = created_at + timedelta(seconds=random.randint(0, 3600))
        price = round(random.uniform(5.0, 999.99), 2)
        name = f"Product {idx + 1}"
        products.append(
            (
                name,
                category,
                price,
                created_at.isoformat(timespec="microseconds"),
                updated_at.isoformat(timespec="microseconds"),
            )
        )

    return products


def seed(products: list[tuple[str, str, float, str, str]]) -> None:
    if DATABASE_URL:
        with psycopg.connect(DATABASE_URL, autocommit=True) as connection:
            connection.execute("DROP TABLE IF EXISTS products;")
            connection.execute(
                """
                CREATE TABLE products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            connection.executemany(
                "INSERT INTO products (name, category, price, created_at, updated_at) VALUES (%s, %s, %s, %s, %s);",
                products,
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_created_at_id ON products(created_at DESC, id DESC);"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_category_created_at_id ON products(category, created_at DESC, id DESC);"
            )
    else:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute(
            "DROP TABLE IF EXISTS products;"
        )
        cursor.execute(
            """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        cursor.executemany(
            "INSERT INTO products (name, category, price, created_at, updated_at) VALUES (?, ?, ?, ?, ?);",
            products,
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_created_at_id ON products(created_at DESC, id DESC);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_category_created_at_id ON products(category, created_at DESC, id DESC);"
        )
        connection.commit()
        connection.close()


def main() -> None:
    print("Generating 200,000 products...")
    products = generate_products()
    print("Seeding database... this may take a minute.")
    seed(products)
    print("Seed complete. Database saved to products.db")


if __name__ == "__main__":
    main()
