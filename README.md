# vuln-shop 🛒 (atelier DevSecOps)

Mini-boutique d'exemple, **volontairement vulnérable**, pour l'atelier DevSecOps.

## Lancer l'app dans un conteneur

```bash
git clone <URL_DU_REPO>
cd vuln-shop
docker compose up --build
```

L'API tourne sur http://localhost:5000

| Endpoint | Exemple |
|----------|---------|
| Liste un produit | http://localhost:5000/product?id=1 |
| Healthcheck | http://localhost:5000/health |

## Votre mission

1. **Code review** : ouvrez `app.py`, `requirements.txt` et `Dockerfile`. Repérez les failles.
2. **Pipeline** : observez l'onglet **Actions** — la CI passe au rouge. Comprenez pourquoi.
3. **Correction** : patchez, repushez, faites repasser la CI au **vert**.

> ⚠️ Ce code contient des failles **intentionnelles**. Ne le déployez jamais en production.

## Tester l'injection SQL (pour comprendre la faille #2)

```
http://localhost:5000/product?id=1 OR 1=1
```
→ renvoie **tous** les produits au lieu d'un seul. C'est la preuve que l'entrée n'est pas filtrée.
