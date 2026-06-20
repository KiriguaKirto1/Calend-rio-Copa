from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

TEAM_CODES: dict[str, tuple[str, str]] = {
    "México": ("MEX", "MX"),
    "África do Sul": ("RSA", "ZA"),
    "Coreia do Sul": ("KOR", "KR"),
    "Tchéquia": ("CZE", "CZ"),
    "Canadá": ("CAN", "CA"),
    "Bósnia e Herzegovina": ("BIH", "BA"),
    "Catar": ("QAT", "QA"),
    "Suíça": ("SUI", "CH"),
    "Brasil": ("BRA", "BR"),
    "Marrocos": ("MAR", "MA"),
    "Haiti": ("HAI", "HT"),
    "Escócia": ("SCO", "GB-SCT"),
    "Estados Unidos": ("USA", "US"),
    "EUA": ("USA", "US"),
    "Paraguai": ("PAR", "PY"),
    "Austrália": ("AUS", "AU"),
    "Turquia": ("TUR", "TR"),
    "Alemanha": ("GER", "DE"),
    "Curaçao": ("CUW", "CW"),
    "Costa do Marfim": ("CIV", "CI"),
    "Equador": ("ECU", "EC"),
    "Países Baixos": ("NED", "NL"),
    "Holanda": ("NED", "NL"),
    "Japão": ("JPN", "JP"),
    "Suécia": ("SWE", "SE"),
    "Tunísia": ("TUN", "TN"),
    "Bélgica": ("BEL", "BE"),
    "Egito": ("EGY", "EG"),
    "Irã": ("IRN", "IR"),
    "Nova Zelândia": ("NZL", "NZ"),
    "Espanha": ("ESP", "ES"),
    "Cabo Verde": ("CPV", "CV"),
    "Arábia Saudita": ("KSA", "SA"),
    "Uruguai": ("URU", "UY"),
    "França": ("FRA", "FR"),
    "Senegal": ("SEN", "SN"),
    "Iraque": ("IRQ", "IQ"),
    "Noruega": ("NOR", "NO"),
    "Argentina": ("ARG", "AR"),
    "Argélia": ("ALG", "DZ"),
    "Áustria": ("AUT", "AT"),
    "Jordânia": ("JOR", "JO"),
    "Portugal": ("POR", "PT"),
    "RD Congo": ("COD", "CD"),
    "Uzbequistão": ("UZB", "UZ"),
    "Colômbia": ("COL", "CO"),
    "Inglaterra": ("ENG", "GB-ENG"),
    "Croácia": ("CRO", "HR"),
    "Gana": ("GHA", "GH"),
    "Panamá": ("PAN", "PA"),
}

COUNTRY_ALIAS: dict[str, str] = {
    "BRA": "BR", "FRA": "FR", "ARG": "AR", "MEX": "MX", "NED": "NL",
    "GER": "DE", "ESP": "ES", "ITA": "IT", "USA": "US", "CAN": "CA",
    "POR": "PT", "URU": "UY", "JPN": "JP", "SWE": "SE", "TUR": "TR",
    "PAR": "PY", "CIV": "CI", "CZE": "CZ", "SUI": "CH", "KOR": "KR",
    "MAR": "MA", "SEN": "SN", "ECU": "EC", "QAT": "QA", "BIH": "BA",
    "AUS": "AU", "SCO": "GB-SCT", "ENG": "GB-ENG", "BEL": "BE", "EGY": "EG",
    "IRN": "IR", "NZL": "NZ", "CPV": "CV", "KSA": "SA", "IRQ": "IQ",
    "NOR": "NO", "ALG": "DZ", "AUT": "AT", "JOR": "JO", "COD": "CD",
    "UZB": "UZ", "COL": "CO", "CRO": "HR", "GHA": "GH", "PAN": "PA",
    "HAI": "HT", "RSA": "ZA", "CUW": "CW", "TUN": "TN"
}


def normalize_country_code(code: str, sigla: str = "") -> str:
    raw = (code or "").strip().upper()
    if not raw and sigla:
        raw = (sigla or "").strip().upper()
    return COUNTRY_ALIAS.get(raw, raw)


def team_code(name: str) -> tuple[str, str]:
    if not name:
        return "TBD", ""
    if name in TEAM_CODES:
        return TEAM_CODES[name]
    if "Vencedor" in name:
        return "VNC", ""
    if "Perdedor" in name:
        return "PRD", ""
    if "Grupo" in name or "melhor" in name or "3º" in name or "2º" in name or "1º" in name:
        return "TBD", ""
    return name[:3].upper(), ""


@dataclass
class Match:
    id: str
    data: str
    hora: str
    time_a: str
    time_b: str
    grupo: str
    fase: str
    estadio: str
    cidade: str
    pais: str = ""
    status: str = "agendado"
    placar: str = ""
    alerta: bool = False
    favorito: bool = False
    destaque: str = ""
    sigla_a: str = ""
    sigla_b: str = ""
    pais_a: str = ""
    pais_b: str = ""
    capacidade: str = ""
    inauguracao: str = ""
    gramado: str = "Natural"
    stadium_image: str = ""
    numero: int = 0
    timezone: str = "America/Sao_Paulo"
    horario_exibido: str = "Brasília (UTC-03)"
    pais_sede: str = ""
    placar_a: int | None = None
    placar_b: int | None = None
    fonte: str = ""
    tipo_dado: str = "demonstrativo"

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Match":
        data = dict(raw)
        sigla_a, pais_a = team_code(data.get("time_a", ""))
        sigla_b, pais_b = team_code(data.get("time_b", ""))
        if not data.get("sigla_a"):
            data["sigla_a"] = sigla_a
        if not data.get("sigla_b"):
            data["sigla_b"] = sigla_b
        data["pais_a"] = normalize_country_code(data.get("pais_a", ""), data.get("sigla_a", pais_a))
        data["pais_b"] = normalize_country_code(data.get("pais_b", ""), data.get("sigla_b", pais_b))
        data.setdefault("pais", "")
        data.setdefault("pais_sede", data.get("pais", ""))
        data.setdefault("status", "agendado")
        data.setdefault("placar", "")
        data.setdefault("alerta", False)
        data.setdefault("favorito", False)
        data.setdefault("destaque", "")
        data.setdefault("capacidade", "")
        data.setdefault("inauguracao", "")
        data.setdefault("gramado", "Natural")
        data.setdefault("stadium_image", "")
        data.setdefault("numero", 0)
        data.setdefault("timezone", "America/Sao_Paulo")
        data.setdefault("horario_exibido", "Brasília (UTC-03)")
        data.setdefault("placar_a", None)
        data.setdefault("placar_b", None)
        data.setdefault("fonte", "")
        data.setdefault("tipo_dado", "demonstrativo")
        if not data.get("placar") and data.get("placar_a") is not None and data.get("placar_b") is not None:
            data["placar"] = f"{data['placar_a']}-{data['placar_b']}"
        valid = {field.name for field in cls.__dataclass_fields__.values()}
        cleaned = {k: v for k, v in data.items() if k in valid}
        return cls(**cleaned)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @property
    def kickoff(self) -> datetime:
        return datetime.strptime(f"{self.data} {self.hora}", "%Y-%m-%d %H:%M")

    @property
    def date_br(self) -> str:
        return self.kickoff.strftime("%d/%m/%Y")

    @property
    def short_date(self) -> str:
        return self.kickoff.strftime("%d/%m")


    def display_kickoff(self, fuso_horario: str = "") -> datetime:
        """Retorna data/hora ajustada para uma preferência simples de fuso.

        A base do projeto está em horário de Brasília. O ajuste abaixo é intencionalmente
        conservador e documentado: ele evita fingir conversão completa de timezone com DST.
        """
        label = fuso_horario or self.horario_exibido
        offsets = {
            "(GMT-03:00) Brasília": 0,
            "Brasília (UTC-03)": 0,
            "(GMT-04:00) Nova York": -1,
            "(GMT-06:00) Cidade do México": -3,
        }
        return self.kickoff + timedelta(hours=offsets.get(label, 0))

    def display_time(self, fuso_horario: str = "") -> str:
        return self.display_kickoff(fuso_horario).strftime("%H:%M")

    def display_date_br(self, fuso_horario: str = "") -> str:
        return self.display_kickoff(fuso_horario).strftime("%d/%m/%Y")

    def display_short_date(self, fuso_horario: str = "") -> str:
        return self.display_kickoff(fuso_horario).strftime("%d/%m")

    @property
    def city_country(self) -> str:
        if self.pais and self.pais not in self.cidade:
            return f"{self.cidade}, {self.pais}"
        return self.cidade

    @property
    def score_text(self) -> str:
        if self.placar:
            return self.placar.replace("-", " x ")
        if self.placar_a is not None and self.placar_b is not None:
            return f"{self.placar_a} x {self.placar_b}"
        return "x"

    @property
    def is_placeholder(self) -> bool:
        return "placeholder" in self.tipo_dado or not self.pais_a or not self.pais_b

    def searchable_text(self) -> str:
        return " ".join([
            self.time_a, self.time_b, self.grupo, self.fase,
            self.estadio, self.cidade, self.pais, self.status,
            self.sigla_a, self.sigla_b, self.tipo_dado,
        ]).lower()
