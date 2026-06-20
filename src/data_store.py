from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .default_data import DEFAULT_MATCHES, DEFAULT_PREFERENCES, STADIUM_INFO
from .models import Match
from .paths import MATCHES_FILE, PREFERENCES_FILE, STATE_FILE
from .validators import validate_matches_payload

DEFAULT_METADATA = {
    "projeto": "Calendário da Copa 2026",
    "nome_competicao": "Copa do Mundo FIFA 2026",
    "versao": "3.0-dados-completos",
    "total_partidas": 104,
    "tipo_base": "base completa com jogos oficiais e placeholders de mata-mata",
    "fonte_principal": "FIFA",
    "ultima_atualizacao": "2026-06-20",
    "timezone_exibicao": "America/Sao_Paulo",
    "observacao": "Horários exibidos em Brasília. Mata-mata usa placeholders até definição dos classificados.",
    "assets": "O app não depende de assets manuais; bandeiras, ícones, estádios e fundo possuem fallback visual.",
}


class DataStore:
    """Persistência local em JSON com validação mínima.

    A camada aceita uma base grande de partidas sem depender de assets. Se o
    arquivo local estiver ausente ou inválido, o app usa DEFAULT_MATCHES para
    evitar quebra na entrega.
    """

    def __init__(self) -> None:
        self.metadata: dict[str, Any] = dict(DEFAULT_METADATA)
        self.validation_errors: list[str] = []
        self.ensure_files()
        self.matches: list[Match] = []
        self.state: dict[str, Any] = {"favoritos": [], "alertas": []}
        self.preferences: dict[str, Any] = dict(DEFAULT_PREFERENCES)
        self.load()

    def ensure_files(self) -> None:
        if not MATCHES_FILE.exists():
            self._write_json(MATCHES_FILE, {"metadata": DEFAULT_METADATA, "partidas": DEFAULT_MATCHES})
        if not STATE_FILE.exists():
            self._write_json(STATE_FILE, {"favoritos": [], "alertas": []})
        if not PREFERENCES_FILE.exists():
            self._write_json(PREFERENCES_FILE, DEFAULT_PREFERENCES)

    def load(self) -> None:
        raw_matches = self._read_json(MATCHES_FILE, {"metadata": DEFAULT_METADATA, "partidas": DEFAULT_MATCHES})
        self.state = self._read_json(STATE_FILE, {"favoritos": [], "alertas": []})
        self.preferences = self._read_json(PREFERENCES_FILE, DEFAULT_PREFERENCES)

        if not isinstance(raw_matches, dict):
            raw_matches = {"metadata": DEFAULT_METADATA, "partidas": raw_matches if isinstance(raw_matches, list) else DEFAULT_MATCHES}
        ok, errors = validate_matches_payload(raw_matches)
        self.validation_errors = errors
        if not ok:
            # Não quebra a execução do app. Usa fallback e deixa erro acessível.
            raw_matches = {"metadata": DEFAULT_METADATA | {"tipo_base": "fallback interno por erro de JSON"}, "partidas": DEFAULT_MATCHES}

        self.metadata = dict(DEFAULT_METADATA | raw_matches.get("metadata", {}))
        matches_data = raw_matches.get("partidas", DEFAULT_MATCHES)
        favorites = set(self.state.get("favoritos", []))
        alerts = set(self.state.get("alertas", []))
        self.matches = []
        for item in matches_data:
            m = Match.from_dict(item)
            info = STADIUM_INFO.get(m.estadio, {})
            if not m.capacidade:
                m.capacidade = info.get("capacidade", "A definir")
            if not m.inauguracao:
                m.inauguracao = info.get("inauguracao", "A definir")
            if not m.gramado:
                m.gramado = info.get("gramado", "Natural")
            m.favorito = m.id in favorites or bool(m.favorito)
            m.alerta = m.id in alerts or bool(m.alerta)
            self.matches.append(m)
        self.matches.sort(key=lambda x: x.kickoff)

    def save_matches(self) -> None:
        self._write_json(MATCHES_FILE, {"metadata": self.metadata, "partidas": [m.to_dict() for m in self.matches]})

    def save_state(self) -> None:
        self.state = {
            "favoritos": [m.id for m in self.matches if m.favorito],
            "alertas": [m.id for m in self.matches if m.alerta],
        }
        self._write_json(STATE_FILE, self.state)

    def save_preferences(self) -> None:
        self._write_json(PREFERENCES_FILE, self.preferences)

    def set_preference(self, key: str, value: Any) -> None:
        self.preferences[key] = value
        self.save_preferences()

    def toggle_favorite(self, match_id: str) -> bool:
        match = self.by_id(match_id)
        match.favorito = not match.favorito
        self.save_state()
        return match.favorito

    def toggle_alert(self, match_id: str) -> bool:
        match = self.by_id(match_id)
        match.alerta = not match.alerta
        self.save_state()
        return match.alerta

    def by_id(self, match_id: str) -> Match:
        for match in self.matches:
            if match.id == match_id:
                return match
        raise KeyError(f"Partida não encontrada: {match_id}")

    def next_match(self) -> Match:
        upcoming = [m for m in self.matches if m.status.lower() != "encerrado"]
        return upcoming[0] if upcoming else self.matches[-1]

    def favorites(self) -> list[Match]:
        return [m for m in self.matches if m.favorito]

    def alerts(self) -> list[Match]:
        return [m for m in self.matches if m.alerta]

    @staticmethod
    def _read_json(path: Path, fallback: Any) -> Any:
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return fallback

    @staticmethod
    def _write_json(path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
