from dataclasses import dataclass, field
import datetime
from decimal import Decimal
from typing import Any, Dict


@dataclass
class Calculation:
    """Class to represent a single Calculation."""
    operation: str
    operands: Dict[str, Decimal]
    result: Decimal
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the calculation to a dictionary."""
        return {
            "operation": self.operation,
            "operands": {k: str(v) for k, v in self.operands.items()},
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat()
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Calculation':
        """Create a Calculation instance from a dictionary."""
        return Calculation(
            operation=data["operation"],
            operands={k: Decimal(v) for k, v in data["operands"].items()},
            result=Decimal(data["result"]),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"])
        )

    def to_string(self) -> str:
        """Return a user-friendly string representation of the calculation."""
        op_map = {
            "Addition": "+",
            "Subtraction": "-",
            "Multiplication": "*",
            "Division": "/",
            "Power": "**",
            "Root": "root"
        }
        op_symbol = op_map.get(self.operation, self.operation)
        
        # Format Decimals to avoid scientific notation for integers
        def format_decimal(d):
            # Use fixed-point notation to avoid scientific E notation
            s = f"{d:f}"
            # Remove trailing zeros and the decimal point if it's a whole number
            return s.rstrip('0').rstrip('.') if '.' in s else s

        operands_str = f" {op_symbol} ".join(map(format_decimal, self.operands.values()))
        return f"{operands_str} = {format_decimal(self.result)}"
