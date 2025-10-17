from decimal import Decimal
import pytest
from pathlib import Path
import os

from app.calculator_config import CalculatorConfig
from app.history import HistoryManager
from app.Calculation import Calculation
from app.calculator import Calculator
from app.operations import Addition


def d(x):
    return Decimal(str(x))


def test_history_manager_load_empty(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    hm = HistoryManager(cfg)
    # ensure no history file exists yet
    if cfg.history_file.exists():
        cfg.history_file.unlink()
    history = hm.load_history()
    assert isinstance(history, list)
    assert len(history) == 0


def test_history_manager_append_and_load(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    hm = HistoryManager(cfg)

    calc = Calculation(operation="Addition", operands={"a": d(1), "b": d(2)}, result=d(3))
    hm.append(calc, max_size=10)

    # file should exist
    assert cfg.history_file.exists()

    loaded = hm.load_history()
    assert len(loaded) == 1
    assert loaded[0].operation == "Addition"
    assert loaded[0].result == d(3)


def test_history_trimming(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    hm = HistoryManager(cfg)

    # append 5 items with max_size=3
    for i in range(5):
        calc = Calculation(operation=f"Op{i}", operands={"a": d(i), "b": d(i)}, result=d(i + i))
        hm.append(calc, max_size=3)

    loaded = hm.load_history()
    assert len(loaded) == 3
    assert [c.operation for c in loaded] == ["Op2", "Op3", "Op4"]


def test_calculator_appends_history(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    # Create a calculator and set operation
    calc = Calculator(config=cfg)
    calc.set_operation(Addition())

    # ensure history empty
    if cfg.history_file.exists():
        cfg.history_file.unlink()

    result = calc.perform_operation('2', '3')
    assert result == d(5)

    # history should be updated in-memory
    assert len(calc.history) == 1

    # and persisted
    hm = HistoryManager(cfg)
    loaded = hm.load_history()
    assert len(loaded) == 1
    assert loaded[0].result == d(5)


def test_load_history_read_failure(tmp_path: Path, monkeypatch):
    cfg = CalculatorConfig(base_dir=tmp_path)
    hm = HistoryManager(cfg)

    # Create a file that will cause pandas to raise when reading
    cfg.history_file.write_text("not,a,valid,csv")

    # Monkeypatch pd.read_csv to raise
    import pandas as pd
    original_read_csv = pd.read_csv

    def fake_read_csv(*args, **kwargs):
        raise ValueError("bad csv")

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    try:
        loaded = hm.load_history()
        assert loaded == []
    finally:
        monkeypatch.setattr(pd, "read_csv", original_read_csv)


def test_skip_malformed_rows(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    hm = HistoryManager(cfg)

    # Create a CSV with one good row and one malformed row
    good = Calculation(operation="Good", operands={"a": d(1), "b": d(2)}, result=d(3)).to_dict()
    # malformed operands field
    bad = {"operation": "Bad", "operands": "{not:valid}", "result": "x", "timestamp": "not-a-date"}

    import pandas as pd
    df = pd.DataFrame([good, bad])
    df.to_csv(cfg.history_file, index=False)

    loaded = hm.load_history()
    # should only load the good row
    assert len(loaded) == 1
    assert loaded[0].operation == "Good"


def test_save_empty_history_creates_file(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    hm = HistoryManager(cfg)

    # Save empty list
    hm.save_history([])
    assert cfg.history_file.exists()
    # file should contain headers
    text = cfg.history_file.read_text()
    assert "operation" in text and "operands" in text


def test_append_with_no_max_size_keeps_all(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    hm = HistoryManager(cfg)

    # append 5 items with max_size=None (no trimming)
    for i in range(5):
        calc = Calculation(operation=f"Op{i}", operands={"a": d(i), "b": d(i)}, result=d(i + i))
        hm.append(calc, max_size=None)

    loaded = hm.load_history()
    assert len(loaded) == 5


def test_append_non_calculation_raises(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    hm = HistoryManager(cfg)

    with pytest.raises(Exception):
        hm.append("not-a-calculation", max_size=10)


def test_save_history_parent_is_file_raises(tmp_path: Path):
    cfg = CalculatorConfig(base_dir=tmp_path)
    # create a file where the history directory should be BEFORE creating the manager
    history_dir = cfg.history_dir
    # ensure parent exists
    history_dir.parent.mkdir(parents=True, exist_ok=True)
    # create a file with the same name as the intended directory
    history_dir.write_text("I am a file, not a directory")

    calc = Calculation(operation="X", operands={"a": d(1), "b": d(2)}, result=d(3))

    # Either HistoryManager initialization will fail (because os.makedirs can't make a dir where a file exists),
    # or initialization may succeed but save_history will raise when attempting to write. Accept either.
    try:
        hm = HistoryManager(cfg)
    except Exception:
        # expected — cannot create history manager when path is a file
        return

    # If we got here, manager was created; saving should fail
    with pytest.raises(Exception):
        hm.save_history([calc])
