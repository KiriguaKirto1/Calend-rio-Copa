from __future__ import annotations

import csv
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import Match
from .paths import CSV_EXPORT_FILE, ICS_EXPORT_FILE

# A base do projeto está salva em horário de Brasília (UTC-03).
# Para o .ics ficar mais previsível entre Google Calendar, Outlook e Windows,
# exportamos os horários em UTC com sufixo Z.
BRASILIA_TO_UTC = timedelta(hours=3)


def _safe_filename(value: str, max_len: int = 80) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", normalized).strip("_")
    return (cleaned or "partida")[:max_len]


def _escape_ics(value: str) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\r\n", r"\n")
        .replace("\n", r"\n")
    )


def _fold_line(line: str) -> list[str]:
    """Dobra linhas longas conforme prática comum do iCalendar."""
    if len(line) <= 73:
        return [line]
    parts: list[str] = []
    current = line
    while len(current) > 73:
        parts.append(current[:73])
        current = " " + current[73:]
    parts.append(current)
    return parts


def _ics_datetime(match: Match) -> tuple[str, str]:
    start_utc = match.kickoff + BRASILIA_TO_UTC
    end_utc = start_utc + timedelta(hours=2)
    return start_utc.strftime("%Y%m%dT%H%M%SZ"), end_utc.strftime("%Y%m%dT%H%M%SZ")


def _dtstamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _description(match: Match) -> str:
    parts = [
        f"Partida {match.numero}",
        f"Fase: {match.fase}",
        f"Grupo/chave: {match.grupo}",
        f"Status: {match.status}",
        f"Horário base do app: {match.hora} Brasília (UTC-03)",
        f"Fonte: {match.fonte or 'dados locais do projeto'}",
        f"Tipo de dado: {match.tipo_dado}",
    ]
    if match.score_text != "x":
        parts.append(f"Placar: {match.score_text}")
    if match.destaque:
        parts.append(match.destaque)
    return " | ".join(parts)


def _event_lines(match: Match, dtstamp: str) -> list[str]:
    start, end = _ics_datetime(match)
    status = "CONFIRMED" if match.status.lower() in {"agendado", "encerrado"} else "TENTATIVE"
    lines = [
        "BEGIN:VEVENT",
        f"UID:{_escape_ics(match.id)}@calendario-copa-2026.local",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{start}",
        f"DTEND:{end}",
        f"SUMMARY:{_escape_ics(f'Jogo {match.numero}: {match.time_a} x {match.time_b} - Copa 2026')}",
        f"LOCATION:{_escape_ics(f'{match.estadio}, {match.city_country}')}",
        f"DESCRIPTION:{_escape_ics(_description(match))}",
        f"STATUS:{status}",
        "END:VEVENT",
    ]
    folded: list[str] = []
    for line in lines:
        folded.extend(_fold_line(line))
    return folded


def _calendar_lines() -> list[str]:
    return [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Calendario Copa 2026//PT-BR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Calendário da Copa 2026",
        "X-WR-TIMEZONE:UTC",
    ]


def _write_ics(path: Path, lines: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    # CRLF melhora compatibilidade com clientes de calendário.
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    return path


def export_match_ics(match: Match, path: Path | None = None) -> Path:
    filename = _safe_filename(f"{match.id}_{match.time_a}_x_{match.time_b}") + ".ics"
    output = path or ICS_EXPORT_FILE.with_name(filename)
    lines = _calendar_lines()
    lines.extend(_event_lines(match, _dtstamp()))
    lines.append("END:VCALENDAR")
    return _write_ics(output, lines)


def export_all_ics(matches: list[Match], path: Path = ICS_EXPORT_FILE) -> Path:
    stamp = _dtstamp()
    lines = _calendar_lines()
    for match in matches:
        lines.extend(_event_lines(match, stamp))
    lines.append("END:VCALENDAR")
    return _write_ics(path, lines)


def export_csv(matches: list[Match], path: Path = CSV_EXPORT_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Nº", "Data", "Hora", "Time A", "Time B", "Placar", "Grupo/Chave", "Fase",
            "Estádio", "Cidade", "País-sede", "Status", "Tipo de dado", "Fonte"
        ])
        for m in matches:
            writer.writerow([
                m.numero, m.date_br, m.hora, m.time_a, m.time_b, m.score_text if m.score_text != "x" else "",
                m.grupo, m.fase, m.estadio, m.cidade, m.pais, m.status, m.tipo_dado, m.fonte,
            ])
    return path
