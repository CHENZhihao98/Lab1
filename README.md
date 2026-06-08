# Lab 1 — Détection de secrets avec Gitleaks

**Durée :** 1h &nbsp;|&nbsp; **Stack :** Python &nbsp;|&nbsp; **Outil :** Gitleaks

## Objectifs

1. Détecter des secrets hardcodés dans le code avec Gitleaks
2. Corriger le code en utilisant les variables d'environnement
3. Créer un pipeline CI qui automatise la détection à chaque push

---

## Prérequis

- `git` — `git --version`
- `python3` — `python3 --version`
- `gitleaks` :
  - macOS : `brew install gitleaks`
  - Linux : télécharger depuis [github.com/gitleaks/gitleaks/releases](https://github.com/gitleaks/gitleaks/releases)
  - Vérifier : `gitleaks version`

---

## Étape 1 — Lancer l'application

```bash
git clone https://github.com/RomdhaniYacine/Lab1.git
cd Lab1
pip3 install -r requirements.txt
python3 app.py
```

Ouvrez `app.py`. Des secrets sont écrits en dur dans les premières lignes.

---

## Étape 2 — Scanner avec Gitleaks

```bash
gitleaks detect --source . --verbose
echo $?
```

`echo $?` retourne `1` si un secret est trouvé, `0` si rien.

**Questions :**
- Quels secrets Gitleaks a-t-il détectés ?
- Dans quel fichier et quel commit ?

---

## Étape 3 — Corriger le code

Remplacez les secrets hardcodés par des variables d'environnement :

```python
import os

API_TOKEN             = os.environ.get("API_TOKEN")
JWT_SECRET            = os.environ.get("JWT_SECRET")
DB_PASSWORD           = os.environ.get("DB_PASSWORD")
AWS_ACCESS_KEY_ID     = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
```

```bash
git add app.py
git commit -m "fix: secrets déplacés en variables d'environnement"
```

Relancez Gitleaks — il trouve encore les secrets dans l'historique git.

**Question :** Comment l'expliquez-vous ?

> **Règle :** un secret committé doit être **révoqué**, pas juste supprimé du code.

---

## Étape 4 — Créer le pipeline CI

Ouvrez `.github/workflows/security.yml`.  
Remplacez le `# TODO` par l'action Gitleaks :

```yaml
- uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

```bash
git add .github/workflows/security.yml
git commit -m "ci: ajout job gitleaks"
git push
```

Observez le pipeline sur **https://github.com/RomdhaniYacine/Lab1/actions**

---

## Solution

Le code corrigé et le pipeline complet sont dans `solution/`.
