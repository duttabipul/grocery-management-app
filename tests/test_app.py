from grocery_app.db import get_db


def test_dashboard_and_inventory(client):
    assert b"Inventory at a glance" in client.get("/").data
    response = client.get("/inventory?q=Apples")
    assert response.status_code == 200
    assert b"Test Apples" in response.data


def test_add_product(client):
    response = client.post(
        "/products/new",
        data={"sku": "MLK-002", "name": "Oat Milk", "category": "Dairy",
              "unit_price": "4.25", "quantity": "8", "low_stock_threshold": "2"},
        follow_redirects=True,
    )
    assert b"Product added successfully" in response.data
    assert b"Oat Milk" in response.data


def test_sale_reduces_inventory(app, client):
    with app.app_context():
        product_id = get_db().execute("SELECT id FROM products WHERE sku='TST-001'").fetchone()["id"]
    response = client.post("/sales", data={"product_id": product_id, "quantity": 3}, follow_redirects=True)
    assert b"Sale recorded and inventory updated" in response.data
    with app.app_context():
        product = get_db().execute("SELECT quantity FROM products WHERE id=?", (product_id,)).fetchone()
        assert product["quantity"] == 7


def test_rejects_sale_above_stock(app, client):
    with app.app_context():
        product_id = get_db().execute("SELECT id FROM products WHERE sku='TST-001'").fetchone()["id"]
    response = client.post("/sales", data={"product_id": product_id, "quantity": 99})
    assert b"Only 10 units are in stock" in response.data

