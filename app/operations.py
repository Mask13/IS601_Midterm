from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


"""Operations module

This module defines an abstract base class `Operations` and several concrete
arithmetic operation classes. Each concrete class implements `execute` and
uses `validate_operands` to ensure inputs are appropriate for the operation.
"""


class Operations(ABC):
    """Abstract base class for arithmetic operations.

    Methods
    -------
    execute(a, b)
        Perform the operation and return the result. Must be implemented by
        concrete subclasses.

    validate_operands(a, b)
        Default validation that checks operand types. Subclasses should call
        `super().validate_operands(a, b)` and then perform operation-specific
        checks (for example, non-zero divisor for division).
    """

    @abstractmethod
    def execute(self, a: Any, b: Any) -> Any:
        """Execute the operation and return the computed value.

        Parameters
        ----------
        a, b : numeric
            Operands for the operation. Concrete implementations should accept
            Decimal or native numeric types and return the appropriate type.
        """

    def validate_operands(self, a: Any, b: Any) -> None:
        """Default validation for operands.

        Checks that both operands are instances of int, float, or Decimal.
        Subclasses can call this method and then add further restrictions.
        Raises a TypeError if validation fails.
        """
        allowed = (int, float, Decimal)
        if not isinstance(a, allowed) or not isinstance(b, allowed):
            raise TypeError("Operands must be numeric types (int, float, Decimal)")

    def __str__(self) -> str:
        """Return the human-friendly name of the operation class."""
        return self.__class__.__name__


class Addition(Operations):
    """Perform addition (a + b)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return the sum of `a` and `b` after validating operands."""
        self.validate_operands(a, b)
        return a + b


class Subtraction(Operations):
    """Perform subtraction (a - b)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return the result of subtracting `b` from `a`."""
        self.validate_operands(a, b)
        return a - b


class Multiplication(Operations):
    """Perform multiplication (a * b)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return the product of `a` and `b`."""
        self.validate_operands(a, b)
        return a * b


class Division(Operations):
    """Perform division (a / b).

    The `validate_operands` method ensures that `b` is not zero in addition
    to the default type checks from the base class.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Ensure operands are numeric and divisor is not zero."""
        super().validate_operands(a, b)
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return the division result of `a` by `b`."""
        self.validate_operands(a, b)
        return a / b


class Power(Operations):
    """Perform exponentiation (a ** b)."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Check base/exponent types and that exponent is non-negative."""
        super().validate_operands(a, b)
        if b < 0:
            raise ValueError("Exponent must be non-negative.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return `a` raised to the power `b`."""
        self.validate_operands(a, b)
        return a ** b


class Root(Operations):
    """Compute the b-th root of a (a ** (1 / b))."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Ensure degree is positive and operands are numeric."""
        super().validate_operands(a, b)
        if b <= 0:
            raise ValueError("Root degree must be positive and non-zero.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return the b-th root of a."""
        self.validate_operands(a, b)
        return a ** (1 / b)


class Modulus(Operations):
    """Compute the modulus (a % b)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return the remainder of `a` divided by `b`."""
        self.validate_operands(a, b)
        return a % b


class Integer_Division(Operations):
    """Perform integer division (a // b). Only accepts integers."""

    def validate_operands(self, a: Any, b: Any) -> None:
        """Require integer operands and non-zero divisor."""
        if not isinstance(a, int) or not isinstance(b, int):
            raise TypeError("Integer_Division requires integer operands")
        if b == 0:
            raise ZeroDivisionError("Cannot perform integer division by zero.")

    def execute(self, a: int, b: int) -> int:
        """Return integer division result of `a // b`."""
        self.validate_operands(a, b)
        return a // b


class Percent_Calculation(Operations):
    """Calculate percentage (a / b * 100)."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Ensure operands are numeric and denominator is not zero."""
        super().validate_operands(a, b)
        if b == 0:
            raise ZeroDivisionError("Cannot calculate percentage with a base of zero.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return the percentage value of a relative to b (a / b * 100)."""
        self.validate_operands(a, b)
        return (a / b) * 100


class Absolute_Difference(Operations):
    """Compute absolute difference between `a` and `b`."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Return absolute value of (a - b)."""
        self.validate_operands(a, b)
        return abs(a - b)