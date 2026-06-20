from __future__ import annotations

from datetime import datetime
from typing import Any

REQUIRED_MATCH_FIELDS = {
    "id", "numero", "data", "hora", "fase", "grupo", "time_a", "time_b",
    "estadio", "cidade", "pais", "status", "tipo_dado"
}

VALID_STATUS = {"agendado", "encerrado", "ao vivo", "adiado", "cancelado"}


def validate_match_dict(raw: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_MATCH_FIELDS - set(raw))
    if missing:
        errors.append(f"campos obrigatórios ausentes: {', '.join(missing)}")
    if "data" in raw and "hora" in raw:
        try:
            datetime.strptime(f"{raw['data']} {raw['hora']}", "%Y-%m-%d %H:%M")
        except ValueError:
            errors.append("data/hora inválida; esperado YYYY-MM-DD e HH:MM")
    status = str(raw.get("status", "agendado")).lower()
    if status not in VALID_STATUS:
        errors.append(f"status inválido: {raw.get('status')}")
    if raw.get("placar_a") is not None and not isinstance(raw.get("placar_a"), int):
        errors.append("placar_a deve ser inteiro ou null")
    if raw.get("placar_b") is not None and not isinstance(raw.get("placar_b"), int):
        errors.append("placar_b deve ser inteiro ou null")
    return errors


def validate_matches_payload(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    partidas = payload.get("partidas")
    if not isinstance(partidas, list):
        return False, ["campo 'partidas' deve ser uma lista"]
    ids: set[str] = set()
    nums: set[int] = set()
    for index, raw in enumerate(partidas, start=1):
        if not isinstance(raw, dict):
            errors.append(f"partida #{index}: item não é objeto JSON")
            continue
        mid = str(raw.get("id", f"#{index}"))
        num = raw.get("numero")
        if mid in ids:
            errors.append(f"partida {mid}: id duplicado")
        ids.add(mid)
        if isinstance(num, int):
            if num in nums:
                errors.append(f"partida {mid}: número duplicado {num}")
            nums.add(num)
        for err in validate_match_dict(raw):
            errors.append(f"partida {mid}: {err}")
    return not errors, errors
