import pytest
from decimal import Decimal

from app.operations import (
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Power,
    Root,
    Modulus,
    Integer_Division,
    Percent_Calculation,
    Absolute_Difference,
)


def d(x):
    return Decimal(str(x))


def test_addition():
    op = Addition()
    assert op.execute(d(1), d(2)) == d(3)


def test_subtraction():
    op = Subtraction()
    assert op.execute(d(5), d(3)) == d(2)


def test_multiplication():
    op = Multiplication()
    assert op.execute(d(4), d(2.5)) == d(10)


def test_division():
    op = Division()
    assert op.execute(d(10), d(2)) == d(5)


def test_power():
    op = Power()
    assert op.execute(d(2), d(3)) == d(8)


def test_root():
    op = Root()
    # square root of 9 is 3
    assert op.execute(d(9), d(2)) == d(3)


def test_modulus():
    op = Modulus()
    assert op.execute(d(10), d(3)) == d(1)


def test_integer_division():
    op = Integer_Division()
    assert op.execute(7, 2) == 3


def test_percent_calculation():
    op = Percent_Calculation()
    assert op.execute(d(50), d(200)) == d(25)


def test_absolute_difference():
    op = Absolute_Difference()
    assert op.execute(d(5), d(8)) == d(3)


def test_invalid_operand_type_raises_typeerror():
    op = Addition()
    with pytest.raises(TypeError):
        op.execute("a", d(2))


def test_division_by_zero_raises():
    op = Division()
    with pytest.raises(ZeroDivisionError):
        op.execute(d(1), d(0))


def test_power_negative_exponent_raises():
    op = Power()
    with pytest.raises(ValueError):
        op.execute(d(2), d(-1))


def test_root_non_positive_degree_raises():
    op = Root()
    with pytest.raises(ValueError):
        op.execute(d(9), d(0))


def test_integer_division_type_and_zero_checks():
    op = Integer_Division()
    # non-integer operands
    with pytest.raises(TypeError):
        op.execute(7.0, 2)
    # division by zero
    with pytest.raises(ZeroDivisionError):
        op.execute(7, 0)


def test_percent_zero_denominator_raises():
    op = Percent_Calculation()
    with pytest.raises(ZeroDivisionError):
        op.execute(d(50), d(0))


def test_str_returns_class_name():
    op = Addition()
    assert str(op) == "Addition"
