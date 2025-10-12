from app.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from app.calculator_config import CalculatorConfig
from typing import Any
from dataclasses import dataclass

@dataclass
class InputValidator:

    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        """Validates that the input is a number and within the allowed range."""
        try:
            num = Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValidationError(f"Invalid number: {value}")

        if abs(num) > config.max_input_value:
            raise ValidationError(f"Input {num} exceeds maximum allowed value of {config.max_input_value}")

        return num