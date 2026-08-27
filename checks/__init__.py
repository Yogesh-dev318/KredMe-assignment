"""Check modules. Each exposes run(cards, ctx) -> list[Finding]."""
from dataclasses import dataclass


@dataclass
class Finding:
    level: str      # "error" | "warn" | "note"
    check: str      # e.g. "L4"
    card: str
    rule: str
    message: str

    def __str__(self) -> str:
        where = self.card if not self.rule else f"{self.card} :: {self.rule}"
        return f"[{self.level.upper():5}] {self.check}  {where}\n         {self.message}"
