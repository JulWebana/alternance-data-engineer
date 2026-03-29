# 🤖 Scraper Alternance Data Engineer

Scraper automatique qui récupère toutes les offres d'alternance **Data Engineer** depuis :
- ✅ France Travail (API officielle)
- ✅ Welcome to the Jungle
- ✅ JobTeaser
- ✅ Indeed
- ✅ HelloWork

Et les classe dans un fichier **Excel** mis à jour automatiquement.

---

## 🚀 Installation rapide (sur ton PC)

```bash
# 1. Clone ce repo
git clone https://github.com/TON_USERNAME/alternance-data-engineer.git
cd alternance-data-engineer

# 2. Installe les dépendances
pip install -r requirements.txt

# 3. Lance le scraper
python job_scraper.py
```

→ Le fichier `offres_alternance_data_engineer.xlsx` est créé automatiquement.

---

## ⚙️ Déploiement automatique sur GitHub Actions (GRATUIT)

> **C'est la méthode recommandée** : ça tourne 24h/24 même quand ton PC est éteint.

### Étape 1 — Crée un repo GitHub

1. Va sur [github.com/new](https://github.com/new)
2. Nomme-le `alternance-data-engineer`
3. Laisse-le **Public** (GitHub Actions est gratuit sur les repos publics)

### Étape 2 — Push le code

```bash
git init
git add .
git commit -m "🚀 Initial commit"
git branch -M main
git remote add origin https://github.com/TON_USERNAME/alternance-data-engineer.git
git push -u origin main
```

### Étape 3 — Active GitHub Actions

1. Va dans ton repo → onglet **Actions**
2. Clique sur **"I understand my workflows, go ahead and enable them"**
3. C'est tout ! Le scraper se lance automatiquement toutes les 30 minutes.

### Étape 4 (optionnel) — Ajouter l'API France Travail

L'API France Travail est **officielle et gratuite**, elle donne accès à plus d'offres.

1. Crée un compte sur [francetravail.io](https://francetravail.io/data/api/offres-emploi)
2. Récupère ton `Client ID` et `Client Secret`
3. Dans ton repo GitHub : **Settings → Secrets → Actions → New repository secret**
   - `FRANCE_TRAVAIL_ID` = ton Client ID
   - `FRANCE_TRAVAIL_SECRET` = ton Client Secret

---

## 📊 Le fichier Excel généré

| Colonne | Contenu |
|---------|---------|
| # | Numéro d'offre |
| Titre du poste | Intitulé exact |
| Entreprise | Nom de l'entreprise |
| Lieu | Ville / région |
| Date publication | Date de mise en ligne |
| Type contrat | Alternance / Apprentissage |
| Lien | Lien direct cliquable vers l'offre |
| Source | Site d'origine |
| Récupéré le | Date/heure de collecte |
| Description | Début de la description |

**Onglet Statistiques** : tableau de bord avec nombre d'offres par source.

---

## 🔔 Aller plus loin : notifications Telegram

Pour recevoir une alerte sur ton téléphone dès qu'une nouvelle offre apparaît :

1. Crée un bot Telegram via [@BotFather](https://t.me/BotFather)
2. Récupère ton `TELEGRAM_TOKEN` et ton `CHAT_ID`
3. Ajoute dans `job_scraper.py` :

```python
import requests

def notify_telegram(token: str, chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

# Après avoir trouvé de nouvelles offres :
for offre in nouvelles_offres:
    notify_telegram(
        token=os.getenv("TELEGRAM_TOKEN"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        message=f"🆕 <b>{offre['titre']}</b>\n🏢 {offre['entreprise']}\n📍 {offre['lieu']}\n🔗 {offre['lien']}"
    )
```

---

## ❓ FAQ

**Q : LinkedIn n'est pas inclus, pourquoi ?**
LinkedIn bloque très agressivement les scrapers et peut bannir ton compte. Les autres sources couvrent 90%+ des offres du marché.

**Q : Le scraper peut-il tourner en permanence ?**
GitHub Actions permet **2000 minutes gratuites/mois**. À 30 min d'intervalle, ça représente ~1440 min/mois → largement suffisant.

**Q : Les offres s'accumulent ou sont remplacées ?**
Les offres s'**accumulent** sans duplication. Le script détecte les doublons par lien URL.
