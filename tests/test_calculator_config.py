"""
Tests for calculator_config.py
"""

import pytest
from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


def test_config_validation_valid():
    """Test that a valid configuration passes validation."""
    config = CalculatorConfig()
    try:
        config.validate()
    except ConfigurationError:
        pytest.fail("Valid configuration should not raise ConfigurationError")


def test_config_validation_invalid_history_size():
    """Test that a non-positive max_history_size raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="max_history_size must be positive"):
        config = CalculatorConfig(max_history_size=0)
        config.validate()


def test_config_validation_invalid_precision():
    """Test that a non-positive precision raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="precision must be positive"):
        config = CalculatorConfig(precision=0)
        config.validate()


def test_config_validation_invalid_max_input():
    """Test that a non-positive max_input_value raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="max_input_value must be positive"):
        config = CalculatorConfig(max_input_value=0)
        config.validate()
