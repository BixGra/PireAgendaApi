from datetime import datetime
import re
import pandas as pd


def convert_google_sheet_url(url):
    pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?"
    return re.sub(
        pattern,
        lambda m: f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?"
        + (f"gid={m.group(3)}&" if m.group(3) else "")
        + "format=csv",
        url,
    )


def check_first_category(category) -> str:
    return category if isinstance(category, str) else "sans_categorie"


def check_value(value) -> str:
    return value if isinstance(value, str) else None


def format_date(date: str) -> datetime:
    # 2024 to handle february 29th
    return datetime.strptime(f"{date}/2024", "%d/%m/%Y")


def get_google_sheet_data(google_sheet_url: str) -> list[dict]:
    url = convert_google_sheet_url(google_sheet_url)
    df = pd.read_csv(url).dropna(subset=["id", "date", "nom", "description"])
    return [
        {
            "id": int(row["id"]),
            "date": format_date(row["date"]),
            "title": row["nom"],
            "description": row["description"],
            "category1": check_first_category(row["categorie1"]),
            "category2": check_value(row["categorie2"]),
            "category3": check_value(row["categorie3"]),
            "link": check_value(row["lien"]),
            "link_title": check_value(row["titre_lien"]),
        }
        for row in df.iloc
    ]
