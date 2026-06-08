# Lab 1 — Détection de Secrets & CI/CD Pipeline

**Contexte** : vous êtes développeur chez Free Mobile. Une API interne vient d'être livrée par une équipe externe. En faisant la code review, vous remarquez que des credentials de production ont été commités directement dans le code. Votre mission en 3 étapes.

---

## Démarrage

```bash
git clone https://github.com/RomdhaniYacine/Lab1.git
cd Lab1
pip3 install -r requirements.txt
python3 app.py
```

Ouvrez **http://localhost:5000** — vous verrez le tableau de bord de l'API.

---

## Objectif 1 — Trouver les secrets dans le code (20 min)

Ouvrez `app.py`. Les 5 secrets sont dans les **30 premières lignes**.

| Variable | Type | Détectable par |
|----------|------|----------------|
| `PROVISIONING_TOKEN` | Token provisioning SIM | Gitleaks |
| `JWT_SECRET` | Clé signature JWT | TruffleHog |
| `CDR_DB_PASSWORD` | Mot de passe MySQL CDR | Gitleaks |
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | Credentials AWS S3 | Gitleaks + TruffleHog |
| `MVNO_PARTNER_KEY` | Clé partenaire MVNO | TruffleHog (entropie) |

**Tester l'impact :**

```bash
# Voir tous les credentials exposés en un appel
curl http://localhost:5000/internal/config

# Voir les clés AWS
curl http://localhost:5000/cdr/storage

# Générer un token JWT avec le secret hardcodé
curl "http://localhost:5000/auth/token?msisdn=0612345678"

# SQL injection — extraire tous les abonnés
curl "http://localhost:5000/subscriber/search?msisdn=' OR '1'='1"
```

---

## Objectif 2 — Compléter le pipeline CI (30 min)

Ouvrez `.github/workflows/security.yml`.

Le fichier contient **5 jobs vides avec des TODO**. Complétez-les :

| Job | Outil | Ce qu'il détecte |
|-----|-------|-----------------|
| `gitleaks` | [Gitleaks](https://github.com/gitleaks/gitleaks-action) | Secrets dans le code |
| `trufflehog` | [TruffleHog](https://github.com/trufflesecurity/trufflehog) | Secrets dans l'historique git |
| `semgrep` | [Semgrep](https://semgrep.dev) | SQL injection, debug=True |
| `pip-audit` | [pip-audit](https://pypi.org/project/pip-audit/) | CVE dans les dépendances |
| `trivy` | [Trivy](https://github.com/aquasecurity/trivy-action) | CVE dans l'image Docker |

Pushez et observez les résultats sur : **https://github.com/RomdhaniYacine/Lab1/actions**

> **Gitleaks** détecte les patterns connus (regex sur AWS, GitHub tokens, etc.)
> **TruffleHog** analyse l'entropie + tout l'historique git — il trouve les secrets supprimés.

---

## Objectif 3 — Corriger les failles (40 min)

Les corrections sont dans `app.py` aux lignes 104–213 (routes API).

**Fix 1 — Remplacer les secrets hardcodés par des variables d'environnement**
```python
# Avant
JWT_SECRET = "fm-jwt-s1gn1ng-k3y-pr0d-2024!"

# Après
import os
JWT_SECRET = os.environ.get("JWT_SECRET", "")
```

**Fix 2 — Corriger la SQL injection (ligne ~110)**
```python
# Avant — vulnérable
query = "SELECT ... WHERE msisdn = '" + msisdn + "'"
conn.execute(query)

# Après — requête paramétrée
conn.execute("SELECT ... WHERE msisdn = ?", (msisdn,))
```

**Fix 3 — Supprimer ou protéger les endpoints dangereux**
- `/internal/config` → supprimer ou ajouter une authentification
- `/cdr/storage` → supprimer, ne jamais exposer des credentials AWS
- `/health` → retourner uniquement `{"status": "ok"}`, sans données abonné

**Fix 4 — Désactiver le mode debug**
```python
# Avant
app.run(host="0.0.0.0", port=5000, debug=True)

# Après
app.run(host="0.0.0.0", port=5000, debug=False)
```

**Fix 5 — Mettre à jour les dépendances vulnérables**
```
flask>=3.0.0
requests>=2.31.0
PyYAML>=6.0.1
Werkzeug>=3.0.0
```

---

## Démonstration TruffleHog — la suppression ne suffit pas

```bash
# 1. Ajouter un faux token dans le code
echo 'TEMP_TOKEN = "ghp_fakeGitHubToken1234567890abc"' >> app.py
git add app.py && git commit -m "test: token temporaire"

# 2. Le supprimer dans le commit suivant
git revert HEAD --no-edit && git push
```

TruffleHog trouve le token dans l'historique git malgré sa suppression.
**Règle** : un secret committé doit être **révoqué**, pas juste supprimé.

---

## Structure du projet

```
Lab1/
├── app.py                     ← API vulnérable — commencer ici
├── requirements.txt           ← Dépendances avec CVE connues
├── Dockerfile                 ← Image Docker (scannée par Trivy dans le CI)
├── .github/workflows/
│   └── security.yml           ← Pipeline CI à compléter (5 TODO)
└── solution/
    ├── app.py                 ← Code corrigé
    └── requirements.txt       ← Dépendances à jour
```

En cas de blocage, les corrections sont dans `solution/`.
