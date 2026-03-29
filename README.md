# 🔍 Alternance Data Engineer - Veille automatique des offres

Outil de veille automatique qui collecte, déduplique et classe les offres d'alternance liées au métier de **Data Engineer** en France depuis plusieurs jobboards et les exporte dans un fichier Excel mis à jour en continu.

---

## 📋 Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Sources surveillées](#sources-surveillées)
3. [Mots-clés couverts](#mots-clés-couverts)
4. [Prérequis](#prérequis)
5. [Installation locale](#installation-locale)
6. [Déploiement automatique sur GitHub Actions](#déploiement-automatique-sur-github-actions)
7. [Configuration de l'API France Travail](#configuration-de-lapi-france-travail)
8. [Structure du fichier Excel](#structure-du-fichier-excel)
9. [Foire aux questions](#foire-aux-questions)

---

## Fonctionnalités

- Collecte automatique des offres d'alternance sur plusieurs plateformes
- Couverture large grâce à **25 mots-clés** couvrant tous les intitulés du métier
- Déduplication automatique : une même offre vue sur plusieurs sites n'est ajoutée qu'une seule fois
- Classement des offres **du plus récent au plus ancien**
- Export dans un fichier **Excel structuré** avec un onglet de statistiques
- Exécution automatique **toutes les heures** via GitHub Actions, même PC éteint

---

## Sources surveillées

| Plateforme | Méthode | Fiabilité |
|---|---|---|
| France Travail | API officielle | ✅ Très fiable |
| Welcome to the Jungle | Scraping | ✅ Stable |
| JobTeaser | Scraping | ✅ Stable |
| Indeed | Scraping | ⚠️ Variable |
| HelloWork | Scraping | ⚠️ Variable |

> **Note :** LinkedIn n'est pas inclus car la plateforme bloque activement les scrapers et peut bannir les comptes qui tentent de contourner cette protection. Les sources ci-dessus couvrent la grande majorité des offres du marché français.

---

## Mots-clés couverts

Le scraper recherche toutes les variantes du métier pour maximiser le nombre d'offres récupérées :

**Intitulés français**
- Ingénieur Data / Ingénieur Big Data / Ingénieur Données
- Ingénieur DataOps / Ingénieur MLOps
- Ingénieur Plateforme Data
- Architecte Data
- Développeur Data

**Intitulés anglais**
- Data Engineer / Big Data Engineer / Cloud Data Engineer
- DataOps Engineer / MLOps Engineer
- Analytics Engineer / Data Platform Engineer
- ETL Engineer / Data Pipeline Engineer
- Data Architect

**Variantes technologiques**
- Data Engineer Azure / AWS / GCP
- Data Engineer Spark
- Consultant Data Engineer

---

## Prérequis

- Python 3.9 ou supérieur
- Git installé sur votre machine
- Un compte GitHub (gratuit)

---

## Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/TON_USERNAME/alternance-data-engineer.git
cd alternance-data-engineer
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer le scraper

```bash
python job_scraper.py
```

Le fichier `offres_alternance_data_engineer.xlsx` est généré automatiquement dans le dossier courant.

---

## Déploiement automatique sur GitHub Actions

GitHub Actions permet d'exécuter le scraper automatiquement toutes les heures, sans avoir besoin que votre ordinateur soit allumé. C'est **gratuit** sur les dépôts publics.

### Étape 1 — Créer un dépôt GitHub

1. Se connecter sur [github.com](https://github.com)
2. Cliquer sur **"New repository"**
3. Nommer le dépôt `alternance-data-engineer`
4. Choisir **Public** (obligatoire pour GitHub Actions gratuit illimité)
5. Ne cocher aucune option (pas de README, pas de .gitignore)
6. Cliquer **"Create repository"**

### Étape 2 — Préparer les fichiers en local

S'assurer que le dossier contient bien ces fichiers :

```
alternance-data-engineer/
├── .github/
│   └── workflows/
│       └── scraper.yml
├── job_scraper.py
├── requirements.txt
└── README.md
```

### Étape 3 — Pousser le code sur GitHub

Dans Git Bash ou un terminal, depuis le dossier du projet :

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TON_USERNAME/alternance-data-engineer.git
git push -u origin main
```

> Remplacer `TON_USERNAME` par votre nom d'utilisateur GitHub.

### Étape 4 — Activer GitHub Actions

1. Aller sur le dépôt GitHub → onglet **Actions**
2. Cliquer sur **"I understand my workflows, go ahead and enable them"** si le message apparaît
3. Le workflow se déclenche automatiquement à chaque push et toutes les heures

### Étape 5 — Vérifier les permissions

1. Aller dans **Settings** → **Actions** → **General**
2. Descendre jusqu'à **"Workflow permissions"**
3. Sélectionner **"Read and write permissions"**
4. Cliquer **Save**

### Étape 6 — Lancer manuellement pour tester

1. Aller dans **Actions** → cliquer sur **"Scraper Alternance Data Engineer"**
2. Cliquer sur **"Run workflow"** → **"Run workflow"**
3. Vérifier que le statut passe au vert ✅

---

## Configuration de l'API France Travail

L'API France Travail est **officielle et gratuite**. Elle donne accès à un volume important d'offres supplémentaires. Son activation est fortement recommandée.

### Obtenir les clés API

1. Créer un compte sur [francetravail.io](https://francetravail.io/data/api/offres-emploi)
2. Créer une application et souscrire à l'API **"Offres d'emploi v2"**
3. Récupérer le `Client ID` et le `Client Secret`

### Ajouter les clés dans GitHub

1. Aller dans **Settings** → **Secrets and variables** → **Actions**
2. Cliquer sur **"New repository secret"** et ajouter :
   - Nom : `FRANCE_TRAVAIL_ID` — Valeur : votre Client ID
   - Nom : `FRANCE_TRAVAIL_SECRET` — Valeur : votre Client Secret

Les clés sont utilisées automatiquement par le workflow à chaque exécution.

---

## Structure du fichier Excel

### Onglet "Offres Alternance"

| Colonne | Contenu |
|---------|---------|
| # | Numéro de ligne |
| Titre du poste | Intitulé exact de l'offre |
| Entreprise | Nom de l'entreprise |
| Lieu | Ville / région |
| Date publication | Date de mise en ligne de l'offre |
| Type contrat | Alternance / Apprentissage |
| Lien | Lien cliquable direct vers l'offre |
| Source | Plateforme d'origine |
| Récupéré le | Date et heure de collecte |
| Description | Extrait de la description du poste |

Les offres sont **triées automatiquement du plus récent au plus ancien** à chaque mise à jour.

### Onglet "Statistiques"

Tableau de bord récapitulatif indiquant le nombre d'offres collectées par source et la date de dernière mise à jour.

---

## Foire aux questions

**a) Les offres s'accumulent-elles ou sont-elles remplacées ?**

Les offres s'accumulent sans duplication. Le script détecte les doublons par URL et par combinaison titre + entreprise.

**b) Le scraper peut-il tourner en permanence ?**

GitHub Actions offre 2 000 minutes gratuites par mois sur les dépôts publics. À raison d'une exécution par heure, cela représente environ 720 minutes mensuelles, bien en dessous de la limite.

**c) Que faire si le workflow échoue ?**

Vérifier les logs dans l'onglet Actions en cliquant sur le run concerné, puis sur le job "scrape". L'erreur est indiquée à la ligne en rouge.

**d) Comment récupérer le fichier Excel mis à jour ?**

Se rendre sur le dépôt GitHub → cliquer sur le fichier `offres_alternance_data_engineer.xlsx` → bouton **Download**.

**e) Peut-on ajouter d'autres sources ?**

Oui. Chaque source correspond à une fonction dans `job_scraper.py`. Il suffit d'ajouter une nouvelle fonction suivant le même modèle et de l'appeler dans la fonction `run_scraper`.
