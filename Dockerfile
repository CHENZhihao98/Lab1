# ── FAILLE #5 — image de base ancienne, criblée de CVE (détecté par Trivy) ──────
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

# Le conteneur tourne en root (aucun USER non-privilégié défini) → mauvaise pratique
CMD ["python", "app.py"]
