"""
Scraper automatique d'offres d'alternance Data Engineer
Sources : France Travail API, Welcome to the Jungle, JobTeaser, Indeed, HelloWork
"""

import requests
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import time
import os
import json
import re

# ───────────────────────────────────────────────
# CONFIG
# ───────────────────────────────────────────────
KEYWORDS = ["data engineer", "ingénieur data", "ingenieur data", "data engineering"]
CONTRACT_TYPE = "alternance"
OUTPUT_FILE = "offres_alternance_data_engineer.xlsx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xhtml;q=0.9,*/*;q=0.8",
}

# ───────────────────────────────────────────────
# FRANCE TRAVAIL API
# ───────────────────────────────────────────────
def get_france_travail_token(client_id: str, client_secret: str) -> str:
    """Récupère le token OAuth2 France Travail."""
    url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
    params = {"realm": "/partenaire"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "api_offresdemploiv2 o2dsoffre",
    }
    r = requests.post(url, params=params, data=data, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def scrape_france_travail(client_id: str = None, client_secret: str = None) -> list:
    """
    Scrape les offres via l'API officielle France Travail.
    Si pas de clés API → retourne liste vide avec instruction.
    """
    if not client_id or not client_secret:
        print("⚠️  France Travail : clés API manquantes (voir README)")
        return []

    try:
        token = get_france_travail_token(client_id, client_secret)
        url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
        headers = {"Authorization": f"Bearer {token}", **HEADERS}
        params = {
            "motsCles": "data engineer",
            "typeContrat": "CA",  # CA = Contrat d'apprentissage / alternance
            "range": "0-149",
        }
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        offres_raw = r.json().get("resultats", [])

        offres = []
        for o in offres_raw:
            offres.append({
                "titre": o.get("intitule", ""),
                "entreprise": o.get("entreprise", {}).get("nom", "N/A"),
                "lieu": o.get("lieuTravail", {}).get("libelle", ""),
                "date_publication": o.get("dateCreation", "")[:10] if o.get("dateCreation") else "",
                "contrat": "Alternance",
                "source": "France Travail",
                "lien": f"https://candidat.francetravail.fr/offres/recherche/detail/{o.get('id', '')}",
                "description": o.get("description", "")[:300],
            })
        print(f"✅ France Travail : {len(offres)} offres récupérées")
        return offres

    except Exception as e:
        print(f"❌ France Travail erreur : {e}")
        return []


# ───────────────────────────────────────────────
# WELCOME TO THE JUNGLE
# ───────────────────────────────────────────────
def scrape_wttj() -> list:
    """Scrape Welcome to the Jungle via leur API publique."""
    offres = []
    try:
        url = "https://www.welcometothejungle.com/api/v1/jobs"
        params = {
            "query": "data engineer",
            "contract_type[]": "apprenticeship",
            "page": 1,
            "per_page": 30,
        }
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)

        # Si l'API JSON ne répond pas, on scrape le HTML
        if r.status_code != 200 or "application/json" not in r.headers.get("Content-Type", ""):
            return scrape_wttj_html()

        data = r.json()
        jobs = data.get("jobs", data.get("results", []))

        for j in jobs:
            offres.append({
                "titre": j.get("name", j.get("title", "")),
                "entreprise": j.get("company", {}).get("name", "N/A") if isinstance(j.get("company"), dict) else j.get("company", "N/A"),
                "lieu": j.get("location", {}).get("city", "") if isinstance(j.get("location"), dict) else "",
                "date_publication": j.get("published_at", j.get("created_at", ""))[:10] if j.get("published_at") or j.get("created_at") else "",
                "contrat": "Alternance",
                "source": "Welcome to the Jungle",
                "lien": f"https://www.welcometothejungle.com/fr/jobs/{j.get('slug', '')}",
                "description": j.get("description", "")[:300] if isinstance(j.get("description"), str) else "",
            })

        print(f"✅ Welcome to the Jungle (API) : {len(offres)} offres")
        return offres

    except Exception as e:
        print(f"⚠️  WTTJ API : {e} → tentative HTML")
        return scrape_wttj_html()


def scrape_wttj_html() -> list:
    """Fallback : scrape HTML Welcome to the Jungle."""
    offres = []
    try:
        url = "https://www.welcometothejungle.com/fr/jobs?query=data+engineer&contract_type%5B%5D=apprenticeship"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.find_all("li", {"data-testid": re.compile("job-card")})
        if not cards:
            cards = soup.find_all("article")

        for card in cards[:30]:
            titre_el = card.find(["h3", "h2", "a"])
            entreprise_el = card.find(attrs={"data-testid": re.compile("company")})
            lieu_el = card.find(attrs={"data-testid": re.compile("location")})
            lien_el = card.find("a", href=True)

            offres.append({
                "titre": titre_el.get_text(strip=True) if titre_el else "N/A",
                "entreprise": entreprise_el.get_text(strip=True) if entreprise_el else "N/A",
                "lieu": lieu_el.get_text(strip=True) if lieu_el else "N/A",
                "date_publication": datetime.now().strftime("%Y-%m-%d"),
                "contrat": "Alternance",
                "source": "Welcome to the Jungle",
                "lien": "https://www.welcometothejungle.com" + lien_el["href"] if lien_el else "N/A",
                "description": "",
            })

        print(f"✅ Welcome to the Jungle (HTML) : {len(offres)} offres")
        return offres

    except Exception as e:
        print(f"❌ WTTJ HTML erreur : {e}")
        return []


# ───────────────────────────────────────────────
# JOBTEASER
# ───────────────────────────────────────────────
def scrape_jobteaser() -> list:
    """Scrape JobTeaser pour les offres d'alternance data engineer."""
    offres = []
    try:
        url = "https://www.jobteaser.com/fr/job-offers"
        params = {
            "q": "data engineer",
            "contract_types[]": "apprenticeship",
            "locale": "fr",
        }
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # Cherche les cartes d'offres
        cards = soup.find_all("article") or soup.find_all("div", class_=re.compile("job|offer|card", re.I))

        for card in cards[:30]:
            titre_el = card.find(["h2", "h3", "h4"]) or card.find("a")
            entreprise_el = card.find(class_=re.compile("company|employer", re.I))
            lieu_el = card.find(class_=re.compile("location|city|lieu", re.I))
            date_el = card.find(["time", "span"], class_=re.compile("date|time|published", re.I))
            lien_el = card.find("a", href=True)

            titre = titre_el.get_text(strip=True) if titre_el else ""
            if not titre or not any(k in titre.lower() for k in ["data", "engineer", "ingénieur"]):
                continue

            offres.append({
                "titre": titre,
                "entreprise": entreprise_el.get_text(strip=True) if entreprise_el else "N/A",
                "lieu": lieu_el.get_text(strip=True) if lieu_el else "France",
                "date_publication": date_el.get("datetime", datetime.now().strftime("%Y-%m-%d"))[:10] if date_el else datetime.now().strftime("%Y-%m-%d"),
                "contrat": "Alternance",
                "source": "JobTeaser",
                "lien": "https://www.jobteaser.com" + lien_el["href"] if lien_el and lien_el["href"].startswith("/") else (lien_el["href"] if lien_el else "N/A"),
                "description": "",
            })

        print(f"✅ JobTeaser : {len(offres)} offres")
        return offres

    except Exception as e:
        print(f"❌ JobTeaser erreur : {e}")
        return []


# ───────────────────────────────────────────────
# INDEED
# ───────────────────────────────────────────────
def scrape_indeed() -> list:
    """Scrape Indeed France pour alternance data engineer."""
    offres = []
    try:
        url = "https://fr.indeed.com/jobs"
        params = {
            "q": "data engineer alternance",
            "l": "France",
            "sc": "0kf:jt(apprenticeship);",
            "sort": "date",
        }
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.find_all("div", class_=re.compile("job_seen_beacon|jobCard|result", re.I))

        for card in cards[:30]:
            titre_el = card.find("h2", class_=re.compile("jobTitle|title", re.I))
            entreprise_el = card.find("span", class_=re.compile("company|employer", re.I))
            lieu_el = card.find("div", class_=re.compile("location|companyLocation", re.I))
            date_el = card.find("span", class_=re.compile("date|posted", re.I))
            lien_el = card.find("a", href=True)

            titre = titre_el.get_text(strip=True) if titre_el else ""
            if not titre:
                continue

            lien = ""
            if lien_el:
                href = lien_el.get("href", "")
                lien = "https://fr.indeed.com" + href if href.startswith("/") else href

            offres.append({
                "titre": titre,
                "entreprise": entreprise_el.get_text(strip=True) if entreprise_el else "N/A",
                "lieu": lieu_el.get_text(strip=True) if lieu_el else "France",
                "date_publication": date_el.get_text(strip=True) if date_el else datetime.now().strftime("%Y-%m-%d"),
                "contrat": "Alternance",
                "source": "Indeed",
                "lien": lien or "N/A",
                "description": "",
            })

        print(f"✅ Indeed : {len(offres)} offres")
        return offres

    except Exception as e:
        print(f"❌ Indeed erreur : {e}")
        return []


# ───────────────────────────────────────────────
# HELLOWORK
# ───────────────────────────────────────────────
def scrape_hellowork() -> list:
    """Scrape HelloWork pour alternance data engineer."""
    offres = []
    try:
        url = "https://www.hellowork.com/fr-fr/emploi/recherche.html"
        params = {
            "k": "data engineer",
            "c": "alternance",
            "s": "date",
        }
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.find_all("article") or soup.find_all("li", class_=re.compile("job|offer", re.I))

        for card in cards[:30]:
            titre_el = card.find(["h2", "h3"])
            entreprise_el = card.find(class_=re.compile("company|employer|entreprise", re.I))
            lieu_el = card.find(class_=re.compile("location|localisation|city", re.I))
            date_el = card.find(["time"])
            lien_el = card.find("a", href=True)

            titre = titre_el.get_text(strip=True) if titre_el else ""
            if not titre:
                continue

            offres.append({
                "titre": titre,
                "entreprise": entreprise_el.get_text(strip=True) if entreprise_el else "N/A",
                "lieu": lieu_el.get_text(strip=True) if lieu_el else "France",
                "date_publication": date_el.get("datetime", datetime.now().strftime("%Y-%m-%d"))[:10] if date_el else datetime.now().strftime("%Y-%m-%d"),
                "contrat": "Alternance",
                "source": "HelloWork",
                "lien": lien_el["href"] if lien_el else "N/A",
                "description": "",
            })

        print(f"✅ HelloWork : {len(offres)} offres")
        return offres

    except Exception as e:
        print(f"❌ HelloWork erreur : {e}")
        return []


# ───────────────────────────────────────────────
# DÉDUPLICATION
# ───────────────────────────────────────────────
def deduplicate(offres: list) -> list:
    """Supprime les doublons basé sur titre + entreprise."""
    seen = set()
    unique = []
    for o in offres:
        key = (o["titre"].lower().strip(), o["entreprise"].lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(o)
    return unique


# ───────────────────────────────────────────────
# EXCEL
# ───────────────────────────────────────────────
def save_to_excel(offres: list, filepath: str):
    """Crée ou met à jour le fichier Excel avec les offres."""
    existing_liens = set()

    # Charge les offres existantes pour ne pas dupliquer
    if os.path.exists(filepath):
        wb_exist = openpyxl.load_workbook(filepath)
        ws_exist = wb_exist.active
        for row in ws_exist.iter_rows(min_row=2, values_only=True):
            if row and row[6]:
                existing_liens.add(row[6])
        wb_exist.close()

    # Filtre les nouvelles offres uniquement
    nouvelles = [o for o in offres if o["lien"] not in existing_liens]
    print(f"\n📊 {len(nouvelles)} nouvelles offres à ajouter (sur {len(offres)} trouvées)")

    if not nouvelles and os.path.exists(filepath):
        print("ℹ️  Aucune nouvelle offre. Fichier inchangé.")
        return

    # Ouvre ou crée le workbook
    if os.path.exists(filepath):
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Offres Alternance"
        _create_header(ws)

    # Couleurs par source
    source_colors = {
        "France Travail": "E8F5E9",
        "Welcome to the Jungle": "E3F2FD",
        "JobTeaser": "FFF3E0",
        "Indeed": "F3E5F5",
        "HelloWork": "FCE4EC",
    }

    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for o in nouvelles:
        row_idx = ws.max_row + 1
        color = source_colors.get(o["source"], "FFFFFF")
        fill = PatternFill("solid", start_color=color, end_color=color)

        values = [
            row_idx - 1,
            o["titre"],
            o["entreprise"],
            o["lieu"],
            o["date_publication"],
            o["contrat"],
            o["lien"],
            o["source"],
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            o.get("description", ""),
        ]

        for col_idx, val in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.fill = fill
            cell.border = border
            cell.alignment = Alignment(vertical="center", wrap_text=(col_idx == 10))
            cell.font = Font(name="Arial", size=10)

        # Lien cliquable
        if o["lien"] and o["lien"] != "N/A":
            ws.cell(row=row_idx, column=7).hyperlink = o["lien"]
            ws.cell(row=row_idx, column=7).font = Font(name="Arial", size=10, color="0563C1", underline="single")

    # Mise à jour du compteur dans l'onglet Stats
    _update_stats_sheet(wb, offres)

    # Freeze panes + filtre auto
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    wb.save(filepath)
    print(f"✅ Fichier sauvegardé : {filepath}")


def _create_header(ws):
    """Crée la ligne d'en-tête stylisée."""
    headers = ["#", "Titre du poste", "Entreprise", "Lieu", "Date publication",
               "Type contrat", "Lien", "Source", "Récupéré le", "Description"]

    header_fill = PatternFill("solid", start_color="1565C0", end_color="1565C0")
    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    col_widths = [5, 40, 25, 20, 18, 15, 50, 20, 18, 60]

    for col_idx, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font = Font(name="Arial", bold=True, color="FFFFFF", size=11)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
        ws.column_dimensions[get_column_letter(col_idx)].width = w

    ws.row_dimensions[1].height = 30


def _update_stats_sheet(wb, offres):
    """Met à jour ou crée l'onglet Statistiques."""
    if "Statistiques" in wb.sheetnames:
        ws_stats = wb["Statistiques"]
        ws_stats.delete_rows(1, ws_stats.max_row)
    else:
        ws_stats = wb.create_sheet("Statistiques")

    header_fill = PatternFill("solid", start_color="1565C0", end_color="1565C0")

    ws_stats["A1"] = "📊 Tableau de bord — Alternances Data Engineer"
    ws_stats["A1"].font = Font(name="Arial", bold=True, size=14, color="1565C0")
    ws_stats["A3"] = "Dernière mise à jour :"
    ws_stats["B3"] = datetime.now().strftime("%d/%m/%Y à %H:%M")
    ws_stats["A3"].font = Font(bold=True, name="Arial")
    ws_stats["B3"].font = Font(name="Arial")

    ws_stats["A5"] = "Source"
    ws_stats["B5"] = "Nb offres"
    for cell in [ws_stats["A5"], ws_stats["B5"]]:
        cell.fill = header_fill
        cell.font = Font(bold=True, color="FFFFFF", name="Arial")
        cell.alignment = Alignment(horizontal="center")

    from collections import Counter
    counts = Counter(o["source"] for o in offres)
    row = 6
    for source, count in sorted(counts.items()):
        ws_stats.cell(row=row, column=1, value=source).font = Font(name="Arial")
        ws_stats.cell(row=row, column=2, value=count).font = Font(name="Arial")
        ws_stats.cell(row=row, column=2).alignment = Alignment(horizontal="center")
        row += 1

    ws_stats.cell(row=row, column=1, value="TOTAL").font = Font(bold=True, name="Arial")
    ws_stats.cell(row=row, column=2, value=f"=SUM(B6:B{row-1})").font = Font(bold=True, name="Arial")

    ws_stats.column_dimensions["A"].width = 25
    ws_stats.column_dimensions["B"].width = 12


# ───────────────────────────────────────────────
# MAIN
# ───────────────────────────────────────────────
def run_scraper(
    france_travail_id: str = None,
    france_travail_secret: str = None,
    output_file: str = OUTPUT_FILE,
):
    print(f"\n{'='*50}")
    print(f"🚀 Démarrage scraping — {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*50}\n")

    all_offres = []

    # Lance chaque scraper
    all_offres += scrape_france_travail(france_travail_id, france_travail_secret)
    time.sleep(2)
    all_offres += scrape_wttj()
    time.sleep(2)
    all_offres += scrape_jobteaser()
    time.sleep(2)
    all_offres += scrape_indeed()
    time.sleep(2)
    all_offres += scrape_hellowork()

    # Déduplique
    all_offres = deduplicate(all_offres)
    print(f"\n📋 Total après déduplication : {len(all_offres)} offres")

    # Sauvegarde Excel
    save_to_excel(all_offres, output_file)

    return len(all_offres)


if __name__ == "__main__":
    # ⚠️ Remplace par tes vraies clés France Travail (optionnel)
    FT_CLIENT_ID = os.getenv("FRANCE_TRAVAIL_ID", "")
    FT_CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_SECRET", "")

    run_scraper(
        france_travail_id=FT_CLIENT_ID,
        france_travail_secret=FT_CLIENT_SECRET,
    )
