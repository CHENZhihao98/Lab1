import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# ── FAILLE #1 — Secrets en dur dans le code (détecté par gitleaks) ────────────
API_KEY = "a1b2c3d4e5f60718293a4b5c6d7e8f90"
DB_PASSWORD = "SuperPassw0rd!"

DB_PATH = "shop.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Crée et amorce la base au démarrage pour que l'app tourne du premier coup."""
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"
    )
    if not conn.execute("SELECT 1 FROM products LIMIT 1").fetchone():
        conn.executemany(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            [("Clavier", 49.9), ("Souris", 19.9), ("Ecran", 199.0)],
        )
        conn.commit()
    conn.close()


@app.route("/product")
def product():
    # ── FAILLE #2 — Injection SQL (concaténation directe) — détecté par Semgrep ──
    pid = request.args.get("id")
    conn = get_db()
    query = "SELECT name, price FROM products WHERE id = " + str(pid)
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify(rows)


@app.route("/health")
def health():
    # Fuite de secret via l'API
    return {"status": "ok", "api_key": API_KEY}


if __name__ == "__main__":
    init_db()
    # ── FAILLE #4 — debug=True exposé (console Werkzeug = exécution de code) ──────
    app.run(host="0.0.0.0", port=5000, debug=True)
