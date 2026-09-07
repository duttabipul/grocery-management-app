import sqlite3

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db():
    database = get_db()
    with current_app.open_resource("schema.sql") as schema:
        database.executescript(schema.read().decode("utf8"))


@click.command("seed-demo")
def seed_demo_command():
    database = get_db()
    products = [
        ("APL-001", "Honeycrisp Apples", "Produce", 1.99, 34, 10),
        ("MLK-001", "Whole Milk", "Dairy", 3.49, 8, 10),
        ("RCE-001", "Basmati Rice", "Pantry", 15.99, 16, 5),
        ("BRD-001", "Whole Wheat Bread", "Bakery", 3.29, 4, 6),
    ]
    database.executemany(
        """INSERT OR IGNORE INTO products
           (sku, name, category, unit_price, quantity, low_stock_threshold)
           VALUES (?, ?, ?, ?, ?, ?)""",
        products,
    )
    database.commit()
    click.echo("Demo products added.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(seed_demo_command)

