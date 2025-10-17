# Python Command-Line Calculator

Author: Aaron Samuel

A robust and feature-rich command-line calculator application built with Python. This project provides an interactive REPL (Read-Eval-Print Loop) for performing arithmetic calculations with high precision, history management, and extensible operations.

## Features

- **Interactive REPL Interface**: A user-friendly command-line for performing calculations and managing the calculator.
- **High-Precision Arithmetic**: Utilizes Python's `Decimal` type for accurate calculations, avoiding common floating-point errors.
- **Extensible Operations**: A factory pattern allows for easy addition of new arithmetic operations. Currently supported operations include:
  - `add`, `subtract`, `multiply`, `divide`
  - `power`, `root`, `modulus`
  - `integer-division`, `percent`, `absolute-difference`
- **Calculation History**:
  - Automatically saves calculation history.
  - Load, show, and clear history.
  - History is persisted to a CSV file (`history/calculator_history.csv`).
- **Robust Input Validation**: Ensures all user inputs are valid numbers and within configurable limits before processing.
- **Configuration via Environment**: Application settings can be managed using a `.env` file or environment variables (e.g., `MAX_HISTORY_SIZE`, `PRECISION`).
- **Logging**: Detailed logging of operations and errors to `logs/calculator.log` for diagnostics and debugging.
- **Comprehensive Test Suite**: Includes an extensive suite of tests using `pytest` and `pytest-cov` to ensure reliability and code quality.

## Project Structure

```
.
├── app/                  # Core application source code
│   ├── Calculation.py
│   ├── calculator.py
│   ├── calculator_config.py
│   ├── calculatorUI.py
│   ├── exceptions.py
│   ├── history.py
│   ├── InputValidator.py
│   └── operations.py
├── tests/                # Test suite for the application
│   ├── test_history.py
│   ├── test_operations.py
│   └── test_validators.py
├── .gitignore
├── main.py               # Main entry point for the application
├── pytest.ini            # Configuration for pytest
├── readme.md             # Project documentation
└── requirements.txt      # Python dependencies
```

## Getting Started

### Requirements

- Python 3.8+

### Installation

1.  Clone the repository (if you haven't already).
2.  Navigate to the project directory.
3.  It is recommended to create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Calculator

To start the calculator's interactive REPL, run the `main.py` script from the project's root directory:

```bash
python main.py
```

## Usage

Once the calculator is running, you can enter commands at the prompt. Type `help` to see a list of available commands.

### Example Commands

-   **Perform a calculation**:
    ```
    Enter command: add
    Enter numbers (or 'cancel' to abort):
    First number: 10
    Second number: 5

    Result: 15
    ```
-   **View history**:
    ```
    Enter command: history
    ```
-   **Clear history**:
    ```
    Enter command: clear
    ```
-   **Exit the calculator**:
    ```
    Enter command: exit
    ```

## Running Tests

The project uses `pytest` for testing. To run the test suite and generate a coverage report, execute the following command from the root directory:

```bash
pytest
```