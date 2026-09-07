# GrocerEase — Grocery Management App

A responsive inventory and sales management application built with Python, Flask, and SQLite. This project modernizes an earlier grocery CRUD prototype into a practical portfolio application.

## Features

- Dashboard with product count, stock totals, inventory value, and recorded revenue
- Product creation, editing, deletion, and validation
- Automatic inventory-value calculations
- Search by product name, SKU, or category
- Custom low-stock thresholds and dashboard alerts
- Sales recording with automatic stock reduction
- Protection against selling more units than are available
- Recent-sales history
- Responsive interface for desktop and mobile
- Automated tests for core workflows

## Technology

- Python 3.10+
- Flask 3
- SQLite
- HTML and CSS
- pytest

## Run locally on Windows

Open the project folder in VS Code, then open **Terminal → New Terminal** and run:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
flask --app run.py seed-demo
py run.py
```

Open <http://127.0.0.1:5000> in your browser. Stop the server with `Ctrl+C`.

## Run tests

```powershell
py -m pytest
```

## Project structure

```text
grocery-management-app/
├── grocery_app/
│   ├── static/styles.css
│   ├── templates/
│   ├── __init__.py
│   ├── db.py
│   ├── routes.py
│   └── schema.sql
├── tests/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── run.py
```

## Data and security

The local SQLite database, environment files, IDE settings, and virtual environments are excluded from Git. The repository contains no customer, university, or personal records. Set a strong `SECRET_KEY` environment variable before any production deployment.

## Background

The original 2022 learning project provided basic create, read, update, and delete functionality in Django. This portfolio edition was rebuilt with a clearer data model, automatic calculations, inventory safeguards, sales tracking, search, testing, responsive design, and documentation.

## Author

**Bipul Dutta**  
[GitHub](https://github.com/duttabipul) · [Portfolio](https://duttabipul.github.io/) · [LinkedIn](https://www.linkedin.com/in/bipuldutta2/)

## License

Released under the [MIT License](LICENSE).
