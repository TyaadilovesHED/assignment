from __future__ import annotations

import base64
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

DB_PATH = Path(__file__).with_name("products.db")
DATABASE_URL = os.environ.get("DATABASE_URL")
STATIC_DIR = Path(__file__).with_name("static")
USE_POSTGRES = DATABASE_URL is not None
app = FastAPI(
    title="Product Browser API",
    description="Browse products newest-first with stable cursor pagination.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    price: float
    created_at: datetime
    updated_at: datetime


class ProductsPage(BaseModel):
    items: List[ProductOut]
    next_cursor: Optional[str] = None
    snapshot: str
    page_size: int


def init_db() -> None:
    if USE_POSTGRES:
        connection = psycopg.connect(DATABASE_URL, autocommit=True)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price DOUBLE PRECISION NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_created_at_id ON products(created_at DESC, id DESC);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_category_created_at_id ON products(category, created_at DESC, id DESC);"
        )
        connection.close()
    else:
        connection = sqlite3.connect(DB_PATH)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_created_at_id ON products(created_at DESC, id DESC);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_category_created_at_id ON products(category, created_at DESC, id DESC);"
        )
        connection.commit()
        connection.close()


@app.on_event("startup")
def startup_event() -> None:
    init_db()


def create_connection():
    if USE_POSTGRES:
        connection = psycopg.connect(DATABASE_URL, autocommit=False, row_factory=dict_row)
        return connection

    connection = sqlite3.connect(
        DB_PATH,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection


def encode_cursor(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def decode_cursor(token: str) -> Dict[str, Any]:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        payload = json.loads(decoded)
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=400, detail="Invalid cursor format.")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid cursor payload.")

    required_keys = {"snapshot", "category"}
    if not required_keys.issubset(payload.keys()):
        raise HTTPException(status_code=400, detail="Cursor is missing required data.")

    return payload


def parse_timestamp(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp in cursor: {value}") from exc


@app.get("/products", response_model=ProductsPage)
def list_products(
    category: Optional[str] = Query(None, description="Filter by category."),
    page_size: int = Query(25, ge=1, le=100, description="Number of products to return."),
    cursor: Optional[str] = Query(None, description="Cursor for the next page."),
) -> ProductsPage:
    cursor_data = None
    snapshot = None
    category_filter: Optional[str] = category
    last_created_at: Optional[str] = None
    last_id: Optional[int] = None

    if cursor:
        cursor_data = decode_cursor(cursor)
        snapshot = cursor_data["snapshot"]
        category_filter = cursor_data.get("category")
        last_created_at = cursor_data.get("last_created_at")
        last_id = cursor_data.get("last_id")

        if category is not None and category != category_filter:
            raise HTTPException(
                status_code=400,
                detail="Category must stay the same when continuing a paginated session.",
            )
    else:
        snapshot = datetime.utcnow().isoformat(timespec="microseconds")

    if last_created_at is not None and last_id is None:
        raise HTTPException(status_code=400, detail="Cursor is missing last_id.")

    connection = create_connection()
    placeholder = "%s" if USE_POSTGRES else "?"

    query = "SELECT id, name, category, price, created_at, updated_at FROM products"
    filters = [f"created_at <= {placeholder}"]
    params: List[Any] = [snapshot]

    if category_filter is not None:
        filters.append(f"category = {placeholder}")
        params.append(category_filter)

    if last_created_at is not None and last_id is not None:
        filters.append(f"(created_at < {placeholder} OR (created_at = {placeholder} AND id < {placeholder}))")
        params.extend([last_created_at, last_created_at, last_id])

    query += " WHERE " + " AND ".join(filters)
    query += f" ORDER BY created_at DESC, id DESC LIMIT {placeholder}"
    params.append(page_size + 1)

    rows = connection.execute(query, params).fetchall()
    if USE_POSTGRES:
        connection.commit()
    connection.close()

    items = []
    for row in rows[:page_size]:
        items.append(
            ProductOut(
                id=row["id"],
                name=row["name"],
                category=row["category"],
                price=row["price"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        )

    next_cursor = None
    if len(rows) > page_size:
        last = rows[page_size - 1]
        next_cursor = encode_cursor(
            {
                "snapshot": snapshot,
                "category": category_filter,
                "last_created_at": last["created_at"],
                "last_id": last["id"],
            }
        )

    return ProductsPage(
        items=items,
        next_cursor=next_cursor,
        snapshot=snapshot,
        page_size=page_size,
    )


@app.get("/categories", response_model=List[str])
def list_categories() -> List[str]:
    connection = create_connection()
    rows = connection.execute(
        "SELECT DISTINCT category FROM products ORDER BY category ASC"
    ).fetchall()
    if USE_POSTGRES:
        connection.commit()
    connection.close()
    return [row["category"] for row in rows]


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="UI not found")
    return index_path.read_text(encoding="utf-8")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
