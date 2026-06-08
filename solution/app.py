import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# CORRIGÉ — secrets chargés depuis les variables d'environnement
API_TOKEN             = os.environ.get("API_TOKEN")
JWT_SECRET            = os.environ.get("JWT_SECRET")
DB_PASSWORD           = os.environ.get("DB_PASSWORD")
AWS_ACCESS_KEY_ID     = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

DB_PATH = "freemobile.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id     INTEGER PRIMARY KEY,
            msisdn TEXT,
            name   TEXT,
            plan   TEXT
        )
    """)
    if not conn.execute("SELECT 1 FROM subscribers LIMIT 1").fetchone():
        conn.executemany("INSERT INTO subscribers VALUES (?,?,?,?)", [
            (1, "0612345678", "Jean Dupont",    "Free 5G 210Go"),
            (2, "0698765432", "Marie Martin",   "Free 4G 80Go"),
            (3, "0634567890", "Ahmed Benali",   "Free 5G 130Go"),
        ])
        conn.commit()
    conn.close()


@app.route("/subscriber")
def subscriber():
    msisdn = request.args.get("msisdn", "")
    conn = get_db()
    # CORRIGÉ — requête paramétrée, SQL injection impossible
    rows = conn.execute(
        "SELECT * FROM subscribers WHERE msisdn = ?", (msisdn,)
    ).fetchall()
    conn.close()
    return jsonify([{"id": r[0], "msisdn": r[1], "name": r[2], "plan": r[3]} for r in rows])


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)  # CORRIGÉ — debug=False
