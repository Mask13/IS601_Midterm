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
            if isinstance(value, str):
                value = value.strip()
            number = Decimal(str(value))
            if abs(number) > config.max_input_value:
                raise ValidationError(f"Value exceeds maximum allowed: {config.max_input_value}")
            return number.normalize()
        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}") from e