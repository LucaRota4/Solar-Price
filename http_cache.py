"""Requêtes HTTP JSON avec cache disque (dossier cache/, ignoré par git).

Les données utilisées sont historiques (cadastre solaire, météo passée) : une fois
téléchargées, elles ne changent pas, donc le cache n'expire pas.
"""
import hashlib
import json
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parent / "cache"
TIMEOUT = 60


class ApiError(RuntimeError):
    """Une API externe est indisponible ou a refusé la requête."""

    def __init__(self, source: str, detail: str):
        super().__init__(f"{source}: {detail}")
        self.source, self.detail = source, detail


def get_json(url: str, params: dict | None = None, source: str = "API") -> dict | list:
    key = hashlib.sha1(json.dumps([url, sorted((params or {}).items())], default=str).encode()).hexdigest()
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise ApiError(source, type(e).__name__) from e
    if not r.ok:
        try:
            detail = r.json().get("message") or r.json().get("reason") or r.text[:200]
        except ValueError:
            detail = r.text[:200]
        raise ApiError(source, f"{r.status_code} {detail}")

    data = r.json()
    CACHE_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return data
