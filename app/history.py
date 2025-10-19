from __future__ import annotations
from pathlib import Path
from typing import List
import os
import pandas as pd

from app.Calculation import Calculation
from app.calculator_config import CalculatorConfig


class HistoryManager:
    """Manage calculator history stored in a CSV file.

    The CSV columns are taken from Calculation.to_dict(): operation, operands,
    result, timestamp.
    """

    def __init__(self, config: CalculatorConfig):
        self.config = config
        # Ensure history directory exists
        os.makedirs(self.config.history_dir, exist_ok=True)
        self.path: Path = self.config.history_file

    def load_history(self) -> List[Calculation]:
        """Load history from CSV and return a list of Calculation objects.

        If the file does not exist, returns an empty list.
        """
        if not self.path.exists():
            return []

        try:
            df = pd.read_csv(self.path)
        except Exception as e:
            # If reading fails, return empty history to avoid crashing the app
            raise e

        history: List[Calculation] = []
        for _, row in df.iterrows():
            # row should contain keys operation, operands, result, timestamp
            op = row.get("operation")
            raw_operands = row.get("operands", "{}")
            # operands stored as stringified dict by Calculation.to_dict(); guard eval
            try:
                operands = eval(raw_operands) if raw_operands is not None else {}
            except Exception:
                operands = {}

            data = {
                "operation": op,
                "operands": operands,
                "result": row.get("result"),
                "timestamp": row.get("timestamp"),
            }

            try:
                history.append(Calculation.from_dict(data))
            except Exception:
                # skip malformed rows
                continue

        return history

    def save_history(self, calculations: List[Calculation]) -> None:
        """Save a list of Calculation objects to the history CSV file."""
        rows = [c.to_dict() for c in calculations]
        if not rows:
            # Create empty dataframe with expected columns
            df = pd.DataFrame(columns=["operation", "operands", "result", "timestamp"])
        else:
            df = pd.DataFrame(rows)

        # Ensure parent dir exists
        self.path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.path, index=False)

    def append(self, calculation: Calculation, max_size: int) -> None:
        """Append a calculation to the CSV-backed history, trimming to max_size."""
        history = self.load_history()
        history.append(calculation)
        # Trim oldest entries if necessary
        if max_size is not None and len(history) > max_size:
            history = history[-max_size:]

        self.save_history(history)
