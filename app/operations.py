from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict

class Operations:
    """Class to perform basic arithmetic operations."""

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the given operation with the provided operands."""
        pass
    
    @abstractmethod
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validates that the operands are what is required for the operation."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Returns the name of the operation."""
        return self.__class__.__name__


class Addition:
    """Class to perform addition operations."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the addition operation."""
        self.validate_operands(a, b)
        return a+b

class Subtraction:
    """Class to perform subtraction operations."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the subtraction operation."""
        self.validate_operands(a, b)
        return a-b

class Multiplication:
    """Class to perform multiplication operations."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the multiplication operation."""
        self.validate_operands(a, b)
        return a*b

class Division:
    """Class to perform division operations."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validates that the divisor is not zero."""
        super().validate_operands(a, b)
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the division operation."""
        self.validate_operands(a, b)
        return a/b

class Power:
    """Class to perform power operations."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validates that the exponent is not negative."""
        super().validate_operands(a, b)
        if b < 0:
            raise ValueError("Exponent must be non-negative.")
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the power operation."""
        self.validate_operands(a, b)
        return a**b

class Root:
    """Class to perform root operations."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validates that the root degree is positive and non-zero."""
        super().validate_operands(a, b)
        if b <= 0:
            raise ValueError("Root degree must be positive and non-zero.")
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the root operation."""
        self.validate_operands(a, b)
        return a**(1/b)

class Modulus:
    """Class to perform modulus operations."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the modulus operation."""
        self.validate_operands(a, b)
        return a%b

class Integer_Division:
    """Class to perform integer division operations."""
    def validate_operands(self, a: int, b: int) -> None:
        """Validates that the divisor is not zero."""
        if b == 0:
            raise ZeroDivisionError("Cannot perform integer division by zero.")
    
    def execute(self, a: int, b: int) -> int:
        """Executes the integer division operation."""
        self.validate_operands(a, b)
        return a//b
    
class Percent_Calculation:
    """Class to perform percentage calculations."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validates that the base is not zero."""
        super().validate_operands(a, b)
        if b == 0:
            raise ZeroDivisionError("Cannot calculate percentage with a base of zero.")
    
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the percentage calculation."""
        self.validate_operands(a, b)
        return (a / b) * 100
    
class Absolute_Difference:
    """Class to perform absolute difference calculations."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Executes the absolute difference calculation."""
        return abs(a - b)