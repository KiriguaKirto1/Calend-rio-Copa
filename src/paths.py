from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
EXPORT_DIR = ROOT_DIR / "exports"
CACHE_DIR = ROOT_DIR / "cache"
FLAGS_CACHE_DIR = CACHE_DIR / "flags"
STADIUMS_CACHE_DIR = CACHE_DIR / "stadiums"

MATCHES_FILE = DATA_DIR / "dados_copa.json"
STATE_FILE = DATA_DIR / "favoritos.json"
PREFERENCES_FILE = DATA_DIR / "preferencias.json"
ICS_EXPORT_FILE = EXPORT_DIR / "calendario_copa_2026.ics"
CSV_EXPORT_FILE = EXPORT_DIR / "calendario_copa_2026.csv"

for folder in (DATA_DIR, EXPORT_DIR, CACHE_DIR, FLAGS_CACHE_DIR, STADIUMS_CACHE_DIR):
    folder.mkdir(parents=True, exist_ok=True)
