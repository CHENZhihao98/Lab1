import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

INTERNAL_API_TOKEN = os.environ.get("INTERNAL_API_TOKEN", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

DB_PATH = "subscribers.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id        INTEGER PRIMARY KEY,
            phone     TEXT,
            name      TEXT,
            email     TEXT,
            iban      TEXT,
            line_id   TEXT,
            plan      TEXT,
            data_used_gb REAL
        )
    """)
    if not conn.execute("SELECT 1 FROM subscribers LIMIT 1").fetchone():
        conn.executemany(
            "INSERT INTO subscribers (phone, name, email, iban, line_id, plan, data_used_gb) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("0612345678", "Jean Dupont",    "jean.dupont@free.fr",      "FR76 3000 6000 0112 3456 7890 189", "FBX-29471", "Freebox Ultra",      142.3),
                ("0698765432", "Marie Martin",   "marie.martin@free.fr",     "FR76 1427 8060 0001 2345 6789 012", "FBX-18293", "Freebox Revolution", 87.1),
                ("0634567890", "Ahmed Benali",   "ahmed.benali@laposte.net", "FR76 2004 1010 0505 0013 4056 024", "FBX-44821", "Freebox Pop",        310.7),
                ("0645678901", "Sophie Leclerc", "sophie.leclerc@yahoo.fr",  "FR76 3000 4000 0300 0000 0350 461", "FBX-57392", "Freebox Ultra",      55.2),
                ("0656789012", "Pierre Moreau",  "pierre.moreau@orange.fr",  "FR76 1820 6000 2000 6543 2100 002", "FBX-61047", "Freebox Mini 4K",    201.8),
            ],
        )
        conn.commit()
    conn.close()


@app.route("/subscriber")
def subscriber():
    phone = request.args.get("phone", "")
    conn = get_db()
    rows = conn.execute(
        "SELECT id, phone, name, email, plan, data_used_gb FROM subscribers WHERE phone = ?",
        (phone,),
    ).fetchall()
    conn.close()
    keys = ["id", "phone", "name", "email", "plan", "data_used_gb"]
    return jsonify([dict(zip(keys, r)) for r in rows])


@app.route("/line-status")
def line_status():
    line_id = request.args.get("id", "")
    conn = get_db()
    row = conn.execute(
        "SELECT name, plan, data_used_gb FROM subscribers WHERE line_id = ?", (line_id,)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Ligne introuvable"}), 404
    return jsonify({
        "line_id":        line_id,
        "status":         "active",
        "subscriber":     row[0],
        "plan":           row[1],
        "data_used_gb":   row[2],
        "sync_down_mbps": 987,
        "sync_up_mbps":   642,
    })


@app.route("/invoice")
def invoice():
    account = request.args.get("account", "")
    conn = get_db()
    row = conn.execute(
        "SELECT name, email, plan FROM subscribers WHERE id = ?", (account,)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Compte introuvable"}), 404
    return jsonify({
        "account":    account,
        "subscriber": row[0],
        "email":      row[1],
        "plan":       row[2],
        "amount_eur": 39.99,
        "period":     "mai 2026",
        "status":     "payée",
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
