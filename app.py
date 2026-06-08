import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================================================
# SECRETS HARDCODÉS — Lab DevSecOps Free Mobile
# Objectif : détecter ces secrets avec Gitleaks, TruffleHog et Bandit
# ============================================================

FREEMOBILE_API_KEY    = "fm-api-prod-4f8a2c1e9b3d7f0566ae12bc"
JWT_SIGNING_SECRET    = "fm-jwt-s1gn1ng-k3y-pr0d-2024-!xZ9"
DB_PASSWORD           = "Fr33M0b!leProd2024#SQL"
AWS_ACCESS_KEY_ID     = "AKIAIOSFODNN7FREEMOB1"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYFREEMOBILE"
SMTP_PASSWORD         = "smtp-relay-free-m0bile-2024"
STRIPE_SECRET_KEY     = "fm-payments-prod-secret-k3y-9aZ3kX2w"
OAUTH_CLIENT_SECRET   = "oauth2-sso-freemobile-client-secret-v2"
TWILIO_AUTH_TOKEN     = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"

DB_PATH = "freemobile.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id      INTEGER PRIMARY KEY,
            msisdn  TEXT,
            name    TEXT,
            plan    TEXT,
            account TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS billing_events (
            id          INTEGER PRIMARY KEY,
            msisdn      TEXT,
            amount      REAL,
            description TEXT,
            date        TEXT
        )
    """)
    if not conn.execute("SELECT 1 FROM subscribers LIMIT 1").fetchone():
        conn.executemany("INSERT INTO subscribers VALUES (?,?,?,?,?)", [
            (1, "0612345678", "Jean Dupont",   "Free 5G 210Go", "ACC-001"),
            (2, "0698765432", "Marie Martin",  "Free 4G 80Go",  "ACC-002"),
            (3, "0634567890", "Ahmed Benali",  "Free 5G 130Go", "ACC-003"),
            (4, "0623456789", "Sophie Leclerc","Free 2€",       "ACC-004"),
        ])
        conn.executemany("INSERT INTO billing_events VALUES (?,?,?,?,?)", [
            (1, "0612345678", 19.99, "Forfait Free 5G 210Go - Juin 2024", "2024-06-01"),
            (2, "0698765432", 15.99, "Forfait Free 4G 80Go - Juin 2024",  "2024-06-01"),
            (3, "0634567890", 19.99, "Forfait Free 5G 130Go - Juin 2024", "2024-06-01"),
            (4, "0623456789",  2.00, "Forfait Free 2€ - Juin 2024",       "2024-06-01"),
        ])
        conn.commit()
    conn.close()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "freemobile-api"})


@app.route("/api/v1/lines")
def lines():
    msisdn = request.args.get("msisdn", "")
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM subscribers WHERE msisdn = ?", (msisdn,)
    ).fetchall()
    conn.close()
    return jsonify([
        {"id": r[0], "msisdn": r[1], "name": r[2], "plan": r[3], "account": r[4]}
        for r in rows
    ])


@app.route("/api/v1/usage")
def usage():
    msisdn = request.args.get("msisdn", "")
    return jsonify({
        "msisdn": msisdn,
        "data_used_gb": 47.3,
        "data_total_gb": 210,
        "voice_used_min": 312,
        "sms_sent": 58,
        "cycle_end": "2024-06-30"
    })


@app.route("/api/v1/billing")
def billing():
    msisdn = request.args.get("msisdn", "")
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM billing_events WHERE msisdn = ?", (msisdn,)
    ).fetchall()
    conn.close()
    return jsonify([
        {"id": r[0], "msisdn": r[1], "amount": r[2], "description": r[3], "date": r[4]}
        for r in rows
    ])


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
