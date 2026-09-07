import os
import tempfile

import pytest

from grocery_app import create_app
from grocery_app.db import get_db


@pytest.fixture()
def app():
    handle, path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test"})
    with app.app_context():
        get_db().execute(
            """INSERT INTO products (sku, name, category, unit_price, quantity, low_stock_threshold)
               VALUES ('TST-001', 'Test Apples', 'Produce', 2.50, 10, 3)"""
        )
        get_db().commit()
    yield app
    os.close(handle)
    os.unlink(path)


@pytest.fixture()
def client(app):
    return app.test_client()

