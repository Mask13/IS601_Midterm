from decimal import Decimal
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from app.operations import Operations
from app.exceptions import ValidationError, OperationError
from app.calculator_config import CalculatorConfig
from app.InputValidator import InputValidator
from app.Calculation import Calculation
from app.history import HistoryManager

# Type aliases for better readability (I have never seen this before this class and this is so nice)
Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]


def get_project_root() -> Path:
    """
    Returns the root directory path of the project.
    """
    current_file = Path(__file__)
    return current_file.parent.parent


class Calculator:
    """A class that changes based on the configuration file.
    It performs calculations based on the operations defined in `app.operations`.
    It calls the loggers to log the operations and results.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None):
        if config is None:
            config = CalculatorConfig()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.config.validate()
        # operations are provided via set_operation
        self.operations = None

        # Logging setup
        os.makedirs(self.config.log_dir, exist_ok=True)
        self._setup_logging()

        # History setup (in-memory + CSV-backed manager)
        os.makedirs(self.config.history_dir, exist_ok=True)
        self.history: List[Calculation] = []
        self.history_manager = HistoryManager(self.config)
        self.operation_strategy: Optional[Operations] = None
        self._undo_stack: List[List[Calculation]] = []
        self._redo_stack: List[List[Calculation]] = []

        # Load existing history from disk into memory
        try:
            self.history = self.history_manager.load_history()
        except Exception as e:
            logging.warning(f"Could not load existing history: {e}")

        logging.info("Calculator initialized with configuration")

    def _setup_logging(self) -> None:
        """
        Configure the logging system.
        """
        try:
            # Ensure the log directory exists
            os.makedirs(self.config.log_dir, exist_ok=True)
            log_file = self.config.log_file.resolve()

            # Configure the basic logging settings
            logging.basicConfig(
                filename=str(log_file),
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                force=True  # Overwrite any existing logging configuration
            )
            logging.info(f"Logging initialized at: {log_file}")
        except Exception as e:
            # Print an error message and re-raise the exception if logging setup fails
            print(f"Error setting up logging: {e}")
            raise

    def set_operation(self, operation: Operations) -> None:
        self.operation_strategy = operation
        logging.info(f"Set operation: {operation}")

    def _save_to_undo_stack(self):
        """Saves a copy of the current history to the undo stack (Memento pattern)."""
        self._undo_stack.append(self.history[:])

    def undo(self) -> bool:
        """Reverts the last state change from the undo stack."""
        if not self._undo_stack:
            return False  # Nothing to undo

        # Save current state for redo
        self._redo_stack.append(self.history[:])

        # Restore previous state from undo stack
        last_state = self._undo_stack.pop()
        self.history = last_state
        logging.info("Undo operation performed.")
        return True

    def redo(self) -> bool:
        """Re-applies the last undone state change from the redo stack."""
        if not self._redo_stack:
            return False  # Nothing to redo

        # Save current state for undo
        self._undo_stack.append(self.history[:])

        # Restore next state from redo stack
        next_state = self._redo_stack.pop()
        self.history = next_state
        logging.info("Redo operation performed.")
        return True

    def perform_operation(
        self,
        a: Union[str, Number],
        b: Union[str, Number]
    ) -> CalculationResult:
        """
        Perform calculation with the current operation. By calling the operations class
        """
        if not self.operation_strategy:
            raise OperationError("No operation set")

        try:
            # Validate and convert inputs to Decimal
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            # Execute the operation strategy
            result = self.operation_strategy.execute(validated_a, validated_b)

            # Create a new Calculation instance with the operation details so that we can use it for the observer pattern and for undo/redo
            # Calculation expects operation, operands dict, result
            calculation = Calculation(
                operation=str(self.operation_strategy),
                operands={"a": validated_a, "b": validated_b},
                result=result
            )

            # Memento: Save state before modification and clear redo stack
            self._save_to_undo_stack()
            self._redo_stack.clear()

            # Append the new calculation to the in-memory history
            self.history.append(calculation)

            # Persist the new calculation to CSV, trimming to max size
            try:
                self.history_manager.append(calculation, self.config.max_history_size)
            except Exception as e:
                logging.warning(f"Failed to persist calculation to history: {e}")

            # TODO - Notify all observers about the new calculation

            return result

        except ValidationError as e:
            # Log and re-raise validation errors
            logging.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            # Log and raise operation errors for any other exceptions
            logging.error(f"Operation failed: {str(e)}")
            raise OperationError(f"Operation failed: {str(e)}")

    def clear_history(self, persist: Optional[bool] = None) -> None:
        """
        Clear the in-memory calculation history.

        By default this clears only the in-memory history. If `persist=True` the
        persisted history file will also be cleared (overwritten with an empty
        history). This prevents accidental loss of saved history when calling
        clear interactively.
        """
        # Memento: Save state before clearing
        self._save_to_undo_stack()
        self._redo_stack.clear()

        self.history = []
        # If persist not provided, use configuration default
        if persist is None:
            persist = bool(self.config.clear_persist_by_default)

        if persist:
            try:
                self.history_manager.save_history(self.history)
                logging.info("Calculation history cleared and persisted to disk")
                # Provide immediate user feedback when used interactively
                print("Calculation history cleared and persisted to disk")
            except Exception as e:
                logging.error(f"Failed to clear persisted history: {e}")
                raise OperationError(f"Failed to clear persisted history: {e}")
        else:
            logging.info("In-memory calculation history cleared (not persisted)")
            print("In-memory calculation history cleared (not persisted)")
    
    def load_history(self) -> None:
        """
        Load calculation history from the CSV file into memory.
        """
        # Memento: Save state before loading new history
        self._save_to_undo_stack()
        self._redo_stack.clear()

        try:
            self.history = self.history_manager.load_history()
            logging.info("Calculation history loaded from disk")
        except Exception as e:
            logging.error(f"Failed to load history from disk: {e}")
            raise OperationError(f"Failed to load history from disk: {e}")
    
    def save_history(self) -> None:
        """
        Save the in-memory calculation history to the CSV file.
        """
        try:
            self.history_manager.save_history(self.history)
            logging.info("Calculation history saved to disk")
        except Exception as e:
            logging.error(f"Failed to save history to disk: {e}")
            raise OperationError(f"Failed to save history to disk: {e}")
    
    def show_history(self) -> List[Calculation]:
        """
        Return the in-memory calculation history.
        """
        return self.history
    
