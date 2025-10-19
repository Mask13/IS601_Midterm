"""
Tests for the calculator's command-line REPL in calculatorUI.py.
"""
import pytest
from unittest.mock import MagicMock, call
from app import calculatorUI


def test_repl_exit_command(monkeypatch, capsys):
    """Test that the REPL exits cleanly with the 'exit' command."""
    # Simulate user typing 'exit'
    inputs = iter(['exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    # Mock the Calculator class to prevent actual file I/O
    mock_calculator = MagicMock()
    monkeypatch.setattr('app.calculatorUI.Calculator', mock_calculator)

    calculatorUI.calculator_repl()

    # Check that the goodbye message is printed
    captured = capsys.readouterr()
    assert "Goodbye!" in captured.out
    # Verify that save_history was called upon exit
    mock_calculator.return_value.save_history.assert_called_once()


def test_repl_addition_command(monkeypatch, capsys):
    """Test a simple addition operation through the REPL."""
    # Simulate user inputs for an addition operation, then exit
    inputs = iter(['add', '10', '5', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    # Use a real calculator instance to check the calculation logic
    # We need to mock the save_history on exit to avoid file system side effects
    monkeypatch.setattr('app.calculator.Calculator.save_history', MagicMock())

    calculatorUI.calculator_repl()

    captured = capsys.readouterr()
    # Check if the result is printed correctly
    assert "Result: 15" in captured.out


def test_repl_unknown_command(monkeypatch, capsys):
    """Test how the REPL handles an unknown command."""
    inputs = iter(['foo', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr('app.calculator.Calculator.save_history', MagicMock())

    calculatorUI.calculator_repl()

    captured = capsys.readouterr()
    assert "Unknown command: 'foo'" in captured.out


def test_repl_help_command(monkeypatch, capsys):
    """Test the 'help' command output."""
    inputs = iter(['help', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr('app.calculator.Calculator.save_history', MagicMock())

    calculatorUI.calculator_repl()

    captured = capsys.readouterr()
    assert "Available commands:" in captured.out
    assert "add" in captured.out
    assert "subtract" in captured.out
    assert "multiply" in captured.out
    assert "history - Show calculation history" in captured.out


def test_repl_help_command_op_factory_fails(monkeypatch, capsys):
    """Test the 'help' command's fallback when OperationFactory fails."""
    inputs = iter(['help', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr('app.calculator.Calculator.save_history', MagicMock())

    # Patch the OperationFactory to raise an exception
    monkeypatch.setattr('app.calculatorUI.OperationFactory.list_operations', MagicMock(side_effect=Exception("Factory error")))

    calculatorUI.calculator_repl()

    captured = capsys.readouterr()
    # Check that the fallback help text is displayed
    assert "add, subtract, multiply, divide, power, root" in captured.out


def test_repl_history_command(monkeypatch, capsys):
    """Test the 'history' command."""
    # Simulate an addition, then request history
    inputs = iter(['add', '20', '22', 'history', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs, 'exit'))

    # To ensure test isolation, we must mock the Calculator class *before* it's instantiated.
    # We create a real Calculator instance here so the logic is tested,
    # but we control its creation to ensure it starts with an empty history.
    from app.calculator import Calculator
    isolated_calc = Calculator()
    isolated_calc.clear_history(persist=True) # Ensure it's empty

    monkeypatch.setattr('app.calculatorUI.Calculator', lambda: isolated_calc)

    calculatorUI.calculator_repl()

    captured = capsys.readouterr()
    # Check that the history output contains the calculation
    assert "Calculation History:" in captured.out
    assert "1. 20 + 22 = 42" in captured.out


def test_repl_clear_command(monkeypatch, capsys):
    """Test the 'clear' command."""
    inputs = iter(['add', '5', '5', 'clear', 'history', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr('app.calculator.Calculator.save_history', MagicMock())

    calculatorUI.calculator_repl()

    captured = capsys.readouterr()
    assert "History cleared" in captured.out
    assert "No calculations in history" in captured.out


def test_repl_eof_error(monkeypatch, capsys):
    """Test that the REPL handles EOFError (Ctrl+D) gracefully."""
    # Simulate an EOFError on input
    monkeypatch.setattr('builtins.input', lambda _: (_ for _ in ()).throw(EOFError))

    calculatorUI.calculator_repl()

    captured = capsys.readouterr()
    assert "Input terminated. Exiting..." in captured.out


def test_repl_undo_redo_command(monkeypatch, capsys):
    """Test the 'undo' and 'redo' commands."""
    # Sequence: add, check history, undo, check history, redo, check history
    inputs = iter([
        'add', '10', '10',
        'history',
        'undo',
        'history',
        'redo',
        'history',
        'exit'
    ])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs, 'exit'))

    # Isolate the test by creating a clean calculator instance
    from contextlib import redirect_stdout
    import io
    from app.calculator import Calculator
    isolated_calc = Calculator()
    # Suppress output from clear_history during test setup to keep captured output clean
    with redirect_stdout(io.StringIO()):
        isolated_calc.clear_history(persist=True)
    monkeypatch.setattr('app.calculatorUI.Calculator', lambda: isolated_calc)

    calculatorUI.calculator_repl()

    captured = capsys.readouterr()
    output = captured.out

    # Check initial state after addition
    assert "Result: 20" in output
    assert "1. 10 + 10 = 20" in output

    # Check state after undo
    assert "Last operation undone." in output
    assert "No calculations in history" in output

    # Check state after redo
    assert "Last undone operation redone." in output
    # The history will show the same calculation again, but that's expected
    assert output.count("1. 10 + 10 = 20") >= 2