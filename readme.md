# Python Command-Line Calculator

Author: Aaron Samuel

A robust and feature-rich command-line calculator application built with Python. This project provides an interactive REPL (Read-Eval-Print Loop) for performing arithmetic calculations with high precision, history management, and extensible operations.

## Features

- **Interactive REPL Interface**: A user-friendly command-line for performing calculations and managing the calculator.
- **High-Precision Arithmetic**: Utilizes Python's `Decimal` type for accurate calculations, avoiding common floating-point errors.
- **Extensible Operations**: A factory pattern allows for easy addition of new arithmetic operations. Currently supported operations include:
  - `add`, `subtract`, `multiply`, `divide`
  - `power`, `root`, `modulus`, `integer-division`, `percent`, `absolute-difference`
- **Calculation History**:
  - Automatically saves calculation history.
  - Load, show, and clear history.
  - History is persisted to a CSV file (`history/calculator_history.csv`).
- **Undo/Redo Functionality**:
  - `undo` the last calculation or `clear` command.
  - `redo` the last undone action.
- **Robust Input Validation**: Ensures all user inputs are valid numbers and within configurable limits before processing.
- **Configuration via Environment**: Application settings can be managed using a `.env` file or environment variables.
- **Logging**: Detailed logging of operations and errors to `logs/calculator.log` for diagnostics and debugging.
- **Comprehensive Test Suite**: Includes an extensive suite of tests using `pytest` and `pytest-cov` to ensure reliability and code quality.
- **CI/CD Pipeline**: Integrated with GitHub Actions for continuous integration and testing.

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
├── tests/                # Test suite
│   ├── test_calculator.py
│   ├── test_calculator_ui.py
│   ├── test_history.py      
│   ├── test_operations.py   
│   └── test_validators.py   
├── .github/              # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml
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

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2.  Navigate to the project directory:
    ```bash
    cd IS601_Midterm
    ```
3.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application can be configured using a `.env` file in the project root. Create a file named `.env` and add the following environment variables as needed:

```
# Base directory for the calculator
CALCULATOR_BASE_DIR=/path/to/your/project

# Maximum number of history entries to store
CALCULATOR_MAX_HISTORY_SIZE=1000

# Automatically save history after each operation (true/false)
CALCULATOR_AUTO_SAVE=true

# Precision for Decimal calculations
CALCULATOR_PRECISION=10

# Maximum value for input numbers
CALCULATOR_MAX_INPUT_VALUE=1e999

# Default encoding for file operations
CALCULATOR_DEFAULT_ENCODING=utf-8

# Whether to persist history clearing by default (true/false)
CALCULATOR_CLEAR_PERSIST=false

# Directory for log files
CALCULATOR_LOG_DIR=logs

# Directory for history files
CALCULATOR_HISTORY_DIR=history
```

## Usage

To start the calculator's interactive REPL, run the `main.py` script from the project's root directory:

```bash
python main.py
```

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
-   **Save history to file**:
    ```
    Enter command: save
    ```
-   **Load history from file**:
    ```
    Enter command: load
    ```
-   **Exit the calculator**:
    ```
    Enter command: exit
    ```

## Testing

The project uses `pytest` for testing. To run the test suite and generate a coverage report, execute the following command from the root directory:

```bash
pytest
```

This will run all tests and display a coverage report in the terminal. To view the detailed HTML coverage report, open the `htmlcov/index.html` file in your web browser:

```bash
open htmlcov/index.html
```

## CI/CD

This project uses GitHub Actions for Continuous Integration. The workflow is defined in `.github/workflows/ci.yml`. The CI pipeline is triggered on every push and pull request to the `master` branch.

The workflow performs the following steps:
1.  Checks out the repository.
2.  Sets up multiple Python versions to test against.
3.  Caches dependencies for faster builds.
4.  Installs project dependencies from `requirements.txt`.
5.  Runs the `pytest` test suite.

This ensures that all tests pass and the code quality is maintained before merging any changes.

## Code Documentation

The code is documented using docstrings and comments to improve readability and maintainability. The docstrings provide an overview of the module, class, or function, while comments explain specific parts of the code.

## Logging

The application uses Python's built-in `logging` module to log important information, warnings, and errors. By default, logs are written to `logs/calculator.log`. The logging behavior can be configured in `app/calculator.py`.
