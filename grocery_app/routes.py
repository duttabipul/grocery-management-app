import sqlite3
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .db import get_db

bp = Blueprint("main", __name__)


def product_form_data(form):
    errors = []
    sku = form.get("sku", "").strip().upper()
    name = form.get("name", "").strip()
    category = form.get("category", "").strip()

    if not sku:
        errors.append("SKU is required.")
    if not name:
        errors.append("Product name is required.")
    if not category:
        errors.append("Category is required.")

    try:
        price = Decimal(form.get("unit_price", ""))
        if price < 0:
            raise InvalidOperation
    except (InvalidOperation, TypeError):
        errors.append("Unit price must be zero or greater.")
        price = Decimal("0")

    try:
        quantity = int(form.get("quantity", ""))
        threshold = int(form.get("low_stock_threshold", ""))
        if quantity < 0 or threshold < 0:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Quantity and low-stock threshold must be whole numbers of zero or greater.")
        quantity, threshold = 0, 5

    return (sku, name, category, float(price), quantity, threshold), errors


@bp.route("/")
def dashboard():
    database = get_db()
    stats = database.execute(
        """SELECT COUNT(*) AS products,
                  COALESCE(SUM(quantity), 0) AS units,
                  COALESCE(SUM(unit_price * quantity), 0) AS value,
                  COALESCE(SUM(CASE WHEN quantity <= low_stock_threshold THEN 1 ELSE 0 END), 0) AS low_stock
           FROM products"""
    ).fetchone()
    sales_total = database.execute(
        "SELECT COALESCE(SUM(quantity * unit_price), 0) AS total FROM sales"
    ).fetchone()["total"]
    low_stock = database.execute(
        "SELECT * FROM products WHERE quantity <= low_stock_threshold ORDER BY quantity, name LIMIT 6"
    ).fetchall()
    recent_sales = database.execute(
        """SELECT sales.*, products.name, products.sku
           FROM sales JOIN products ON products.id = sales.product_id
           ORDER BY sales.sold_at DESC, sales.id DESC LIMIT 6"""
    ).fetchall()
    return render_template(
        "dashboard.html", stats=stats, sales_total=sales_total,
        low_stock=low_stock, recent_sales=recent_sales,
    )


@bp.route("/inventory")
def inventory():
    query = request.args.get("q", "").strip()
    database = get_db()
    if query:
        search = f"%{query}%"
        products = database.execute(
            """SELECT * FROM products
               WHERE sku LIKE ? OR name LIKE ? OR category LIKE ?
               ORDER BY name""",
            (search, search, search),
        ).fetchall()
    else:
        products = database.execute("SELECT * FROM products ORDER BY name").fetchall()
    return render_template("inventory.html", products=products, query=query)


@bp.route("/products/new", methods=("GET", "POST"))
def add_product():
    if request.method == "POST":
        data, errors = product_form_data(request.form)
        if not errors:
            try:
                database = get_db()
                database.execute(
                    """INSERT INTO products
                       (sku, name, category, unit_price, quantity, low_stock_threshold)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    data,
                )
                database.commit()
                flash("Product added successfully.", "success")
                return redirect(url_for("main.inventory"))
            except sqlite3.IntegrityError:
                errors.append("That SKU already exists.")
        for error in errors:
            flash(error, "error")
    return render_template("product_form.html", product=None, title="Add product")


@bp.route("/products/<int:product_id>/edit", methods=("GET", "POST"))
def edit_product(product_id):
    database = get_db()
    product = database.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("main.inventory"))
    if request.method == "POST":
        data, errors = product_form_data(request.form)
        if not errors:
            try:
                database.execute(
                    """UPDATE products SET sku=?, name=?, category=?, unit_price=?, quantity=?,
                       low_stock_threshold=?, updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                    (*data, product_id),
                )
                database.commit()
                flash("Product updated successfully.", "success")
                return redirect(url_for("main.inventory"))
            except sqlite3.IntegrityError:
                errors.append("That SKU already exists.")
        for error in errors:
            flash(error, "error")
    return render_template("product_form.html", product=product, title="Edit product")


@bp.post("/products/<int:product_id>/delete")
def delete_product(product_id):
    database = get_db()
    try:
        database.execute("DELETE FROM products WHERE id = ?", (product_id,))
        database.commit()
        flash("Product deleted.", "success")
    except sqlite3.IntegrityError:
        flash("Products with sales history cannot be deleted.", "error")
    return redirect(url_for("main.inventory"))


@bp.route("/sales", methods=("GET", "POST"))
def sales():
    database = get_db()
    if request.method == "POST":
        try:
            product_id = int(request.form.get("product_id", ""))
            quantity = int(request.form.get("quantity", ""))
        except ValueError:
            product_id, quantity = 0, 0
        product = database.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            flash("Select a valid product.", "error")
        elif quantity <= 0:
            flash("Sale quantity must be at least 1.", "error")
        elif quantity > product["quantity"]:
            flash(f"Only {product['quantity']} units are in stock.", "error")
        else:
            database.execute(
                "INSERT INTO sales (product_id, quantity, unit_price) VALUES (?, ?, ?)",
                (product_id, quantity, product["unit_price"]),
            )
            database.execute(
                "UPDATE products SET quantity=quantity-?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (quantity, product_id),
            )
            database.commit()
            flash("Sale recorded and inventory updated.", "success")
            return redirect(url_for("main.sales"))
    products = database.execute("SELECT * FROM products WHERE quantity > 0 ORDER BY name").fetchall()
    history = database.execute(
        """SELECT sales.*, products.name, products.sku
           FROM sales JOIN products ON products.id=sales.product_id
           ORDER BY sold_at DESC, sales.id DESC"""
    ).fetchall()
    return render_template("sales.html", products=products, history=history)

