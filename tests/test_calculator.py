#Aaron Samuel
import datetime
from pathlib import Path
import pandas as pd
import pytest
import logging
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator, get_project_root
from app.calculatorUI import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError, ConfigurationError, CalculatorError
from app.Calculation import Calculation
from app.operations import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

def test_get_project_root():
    """Test the get_project_root utility function."""
    root = get_project_root()
    assert isinstance(root, Path)
    assert (root / 'pytest.ini').exists()
# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator._undo_stack == []
    assert calculator._redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

@patch('app.history.HistoryManager.load_history', side_effect=Exception("File read error"))
def test_calculator_init_load_history_failure_with_caplog(_mock_load_history, caplog):
    # Avoid reconfiguring global logging in the SUT so caplog stays connected
    with patch.object(Calculator, '_setup_logging', return_value=None):
        with caplog.at_level(logging.WARNING):
            Calculator()
            assert "Could not load existing history: File read error" in caplog.text
#used chatgpt to add the above test. Kinda undertand the logging behavior.

def test_setup_logging_failure(capsys, tmp_path):
    """
    Call Calculator._setup_logging directly while making os.makedirs raise,
    so the method's except block prints the error and re-raises.
    """
    # Create a minimal config object expected by _setup_logging
    class DummyConfig:
        # these should be Path-like
        log_dir = tmp_path / "logs"
        log_file = tmp_path / "logs" / "calculator.log"

    # Build an instance without running __init__
    calc = object.__new__(Calculator)
    calc.config = DummyConfig()

    # Patch os.makedirs used inside _setup_logging to raise
    with patch('app.calculator.os.makedirs', side_effect=OSError("Permission denied")):
        with pytest.raises(OSError, match="Permission denied"):
            calc._setup_logging()

    # capture printed output
    captured = capsys.readouterr()
    assert "Error setting up logging: Permission denied" in captured.out

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)


def test_perform_operation_unexpected_exception(calculator, caplog):
    """
    Test that a generic exception during operation execution is caught and wrapped.
    This specifically tests the final `except Exception` block in `perform_operation`.
    """
    # Arrange: Set an operation and patch its execute method to raise a generic Exception.
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    error_message = "An unexpected error occurred"

    with patch.object(operation, 'execute', side_effect=Exception(error_message)):
        # Act & Assert: Expect an OperationError and check the log message.
        with pytest.raises(OperationError, match=f"Operation failed: {error_message}"):
            calculator.perform_operation(5, 3)
        assert f"Operation failed: {error_message}" in caplog.text

def test_perform_operation_save_failure(calculator, caplog):
    """Test that a failure to save history during an operation is logged."""
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    error_message = "Cannot write to history file"

    with patch.object(calculator, 'save_history', side_effect=Exception(error_message)):
        with caplog.at_level(logging.WARNING):
            calculator.perform_operation(1, 2)
            assert f"Failed to persist calculation to history: {error_message}" in caplog.text


# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1


def test_history_size_limit():
    """Test that the calculation history does not exceed the configured max size."""
    # Arrange: Create a calculator with a small history size limit.
    with TemporaryDirectory() as temp_dir:
        config = CalculatorConfig(base_dir=Path(temp_dir), max_history_size=2)

        # Ensure any pre-existing history file in the temp dir is removed so
        # the Calculator does not load stale history from disk.
        try:
            if config.history_file.exists():
                config.history_file.unlink()
        except Exception:
            # If we cannot remove it for some reason, continue — the test
            # will still validate behavior but it is best-effort cleanup.
            pass

        calculator = Calculator(config=config)
        operation = OperationFactory.create_operation('add')
        calculator.set_operation(operation)

        # Act: Perform more operations than the history limit.
        # First calculation, should be removed later.
        calculator.perform_operation(1, 1)
        # Second calculation.
        calculator.perform_operation(2, 2)
        # Third calculation, which should trigger the history limit.
        calculator.perform_operation(3, 3)

        # Assert: The history size is capped and the oldest entry is gone.
        assert len(calculator.history) == 2
        # The first item in history should now be the second calculation (2+2).
        assert calculator.history[0].operands['a'] == Decimal('2')



# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    # Manually add a calculation to history to avoid perform_operation's automatic save
    calculation = Calculation(
        operation="Addition", operands={"a": Decimal('2'), "b": Decimal('3')}, result=Decimal('5')
    )
    calculator.history.append(calculation)
    calculator.save_history()
    mock_to_csv.assert_called_once_with(calculator.config.history_file, index=False)


def test_save_history_failure(calculator, caplog):
    """
    Test that an exception during save_history is caught, logged, and re-raised as OperationError.
    This specifically tests the `except Exception` block in `save_history`.
    """
    # Arrange: Add some history to the calculator.
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(1, 2)
    error_message = "Disk is full"

    # Act & Assert: Patch to_csv to raise an exception and verify the handling.
    with patch('app.calculator.pd.DataFrame.to_csv', side_effect=IOError(error_message)):
        with pytest.raises(OperationError, match=f"Failed to save history to disk: {error_message}"):
            calculator.save_history()
        assert any(f"Failed to save history to disk: {error_message}" in record.message for record in caplog.records)

def test_load_history_failure(calculator, caplog):
    """
    Test that an exception during load_history is caught, logged, and re-raised as OperationError.
    This specifically tests the `except Exception` block in `load_history`.
    """
    # Arrange: Ensure the history file exists to trigger the loading logic.
    calculator.config.history_file.parent.mkdir(parents=True, exist_ok=True)
    calculator.config.history_file.write_text("invalid,csv,content")
    error_message = "Error parsing CSV"

    # Act & Assert: Patch pd.read_csv to raise an exception and verify the handling.
    with patch('app.calculator.pd.read_csv', side_effect=ValueError(error_message)):
        with pytest.raises(OperationError, match=f"Failed to load history from disk: {error_message}"):
            calculator.load_history()
        assert any(f"Failed to load history from disk: {error_message}" in record.message for record in caplog.records)


def test_show_history(calculator):
    """Test the show_history method for both empty and populated history."""
    # 1. Test with an empty history
    assert calculator.show_history() == [], "Should return an empty list for empty history"

    # 2. Test with a populated history
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(10, 5)
    
    history_list = calculator.show_history()
    assert len(history_list) == 1
    assert history_list[0].result == Decimal('15')

            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert not calculator.history

def test_clear_history_persist_failure(calculator, caplog):
    """Test that an exception during persisted clear_history is handled."""
    error_message = "Permission denied"
    with patch.object(calculator.history_manager, 'save_history', side_effect=Exception(error_message)):
        with pytest.raises(OperationError, match=f"Failed to clear persisted history: {error_message}"):
            calculator.clear_history(persist=True)
        assert f"Failed to clear persisted history: {error_message}" in caplog.text

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit_save_failure(mock_print, mock_input):
    """Test the exit command when saving history fails."""
    # Arrange: Patch save_history to raise an exception
    error_message = "Permission denied"
    with patch('app.calculator.Calculator.save_history', side_effect=Exception(error_message)):
        # Act: Run the REPL
        calculator_repl()

@patch('builtins.input', side_effect=['add', '10', '5', 'clear', 'history', 'exit'])
@patch('builtins.print')
def test_calculator_repl_clear(mock_print, mock_input):
    """Test the 'clear' command in the REPL."""
    calculator_repl()
    mock_print.assert_any_call("History cleared")
    mock_print.assert_any_call("No calculations in history")

@patch('builtins.input', side_effect=['undo', 'redo', 'add', '5', '5', 'undo', 'redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo_redo(mock_print, mock_input):
    """Test the 'undo' and 'redo' commands in the REPL."""
    with patch('app.calculator.Calculator.save_history'):
        calculator_repl()
        mock_print.assert_any_call("Last operation undone.")
        mock_print.assert_any_call("Last undone operation redone.")


@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save_success(mock_print, mock_input):
    """Test the 'save' command in the REPL succeeds."""
    with patch('app.calculator.Calculator.save_history') as mock_save:
        calculator_repl()
        mock_save.assert_called()
        mock_print.assert_any_call("History saved successfully")


@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save_failure(mock_print, mock_input):
    """Test the 'save' command in the REPL fails gracefully."""
    error_message = "Cannot write to disk"
    with patch('app.calculator.Calculator.save_history', side_effect=Exception(error_message)):
        calculator_repl()
        mock_print.assert_any_call(f"Error saving history: {error_message}")


@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load_success(mock_print, mock_input):
    """Test the 'load' command in the REPL succeeds."""
    with patch('app.calculator.Calculator.load_history') as mock_load:
        calculator_repl()
        mock_load.assert_called_once()
        mock_print.assert_any_call("History loaded successfully")


@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load_failure(mock_print, mock_input):
    """Test the 'load' command in the REPL fails gracefully."""
    error_message = "File not found or corrupted"
    with patch('app.calculator.Calculator.load_history', side_effect=Exception(error_message)):
        calculator_repl()
        mock_print.assert_any_call(f"Error loading history: {error_message}")

@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_at_first_operand(mock_print, mock_input):
    """Test that the user can cancel an operation at the first operand prompt."""
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")

@patch('builtins.input', side_effect=['add', '10', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_at_second_operand(mock_print, mock_input):
    """Test that the user can cancel an operation at the second operand prompt."""
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")

@patch('builtins.input', side_effect=['add', 'abc', '5', 'exit'])
@patch('builtins.print')
def test_calculator_repl_handles_validation_error(mock_print, mock_input):
    """Test that the REPL handles a ValidationError from invalid input."""
    calculator_repl()
    mock_print.assert_any_call("Error: Invalid number format: abc")


@patch('builtins.input', side_effect=['add', '1', '2', 'exit'])
@patch('builtins.print')
def test_calculator_repl_handles_unexpected_exception(mock_print, mock_input):
    """Test that the REPL handles an unexpected generic Exception during calculation."""
    error_message = "Something went very wrong"
    # Patch the perform_operation method to raise a generic exception
    with patch('app.calculator.Calculator.perform_operation', side_effect=Exception(error_message)):
        calculator_repl()
        # Verify that the 'Unexpected error' message is printed
        mock_print.assert_any_call(f"Unexpected error: {error_message}")

@patch('builtins.input', side_effect=KeyboardInterrupt)
@patch('builtins.print')
def test_calculator_repl_keyboard_interrupt(mock_print, mock_input):
    """Test that a KeyboardInterrupt is handled gracefully in the main loop."""
    # The side_effect will raise KeyboardInterrupt, then the loop will try to
    # get input again, which will raise it again, creating an infinite loop in the test.
    # We can limit the number of calls to input to break out.
    mock_input.side_effect = [KeyboardInterrupt, EOFError] # Use EOFError to break the loop
    calculator_repl()
    mock_print.assert_any_call("\nOperation cancelled")

@patch('builtins.input', side_effect=EOFError)
@patch('builtins.print')
def test_calculator_repl_eof_error(mock_print, mock_input):
    """Test that an EOFError is handled gracefully, causing an exit."""
    calculator_repl()
    mock_print.assert_any_call("\nInput terminated. Exiting...")

@patch('builtins.input', side_effect=[Exception("Generic loop error"), 'exit'])
@patch('builtins.print')
def test_calculator_repl_generic_exception_in_loop(mock_print, mock_input):
    """Test that a generic Exception in the main loop is handled."""
    calculator_repl()
    mock_print.assert_any_call("Error: Generic loop error")
