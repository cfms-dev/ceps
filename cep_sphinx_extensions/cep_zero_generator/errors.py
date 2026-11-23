from __future__ import annotations

from pathlib import Path


class CEPError(Exception):
    def __init__(self, error: str, cep_file: Path, cep_number: int | None = None):
        super().__init__(error)
        self.filename = cep_file
        self.number = cep_number

    def __str__(self):
        error_msg = super().__str__()
        error_msg = f"({self.filename}): {error_msg}"
        cep_str = f"CEP {self.number}"
        return f"{cep_str} {error_msg}" if self.number is not None else error_msg
