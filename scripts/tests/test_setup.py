"""Tests for setup module."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src import setup


def test_main_db_empty_runs_migrations_and_seed(monkeypatch, tmp_path):
    """When db_state=0, runs migrations and seed."""
    calls = []

    def mock_run(cmd, *args, **kwargs):
        calls.append(cmd)
        if "check_db" in str(cmd):
            return type("R", (), {"returncode": 0})()
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_run)
    monkeypatch.setattr(setup, "CARDS_CSV", tmp_path / "cards.csv")
    (tmp_path / "cards.csv").touch()

    setup.main()

    assert any("check_db" in str(c) for c in calls)
    assert any("run_migrations" in str(c) for c in calls)
    assert any("seed_from_csv" in str(c) for c in calls)


def test_main_db_needs_seed_runs_seed(monkeypatch, tmp_path):
    """When db_state=1, runs seed only."""
    calls = []

    def mock_run(cmd, *args, **kwargs):
        calls.append(cmd)
        if "check_db" in str(cmd):
            return type("R", (), {"returncode": 1})()
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_run)
    monkeypatch.setattr(setup, "CARDS_CSV", tmp_path / "cards.csv")
    (tmp_path / "cards.csv").touch()

    setup.main()

    assert any("seed_from_csv" in str(c) for c in calls)
    assert not any("run_migrations" in str(c) for c in calls)


def test_main_db_populated_skips(monkeypatch, capsys):
    """When db_state=2, skips setup."""
    def mock_run(cmd, *args, **kwargs):
        if "check_db" in str(cmd):
            return type("R", (), {"returncode": 2})()
        return None

    monkeypatch.setattr("subprocess.run", mock_run)
    setup.main()
    captured = capsys.readouterr()
    assert "already populated" in captured.out


def test_main_db_connection_error(monkeypatch, capsys):
    """When db_state=3, exits with error."""
    def mock_run(cmd, *args, **kwargs):
        if "check_db" in str(cmd):
            return type("R", (), {"returncode": 3})()
        return None

    monkeypatch.setattr("subprocess.run", mock_run)
    with pytest.raises(SystemExit):
        setup.main()
    captured = capsys.readouterr()
    assert "Cannot connect" in captured.err


def test_main_db_check_error(monkeypatch, capsys):
    """When db_state=4, exits with error."""
    def mock_run(cmd, *args, **kwargs):
        if "check_db" in str(cmd):
            return type("R", (), {"returncode": 4})()
        return None

    monkeypatch.setattr("subprocess.run", mock_run)
    with pytest.raises(SystemExit):
        setup.main()
    captured = capsys.readouterr()
    assert "Failed to check" in captured.err


def test_main_generates_cards_csv_when_missing(monkeypatch, tmp_path):
    """When cards.csv missing and db_state=0, runs generate_cards_csv."""
    (tmp_path / "data").mkdir()
    card_list = tmp_path / "data" / "card_list.csv"
    card_list.write_text("id,name\n1,Test")
    cards_csv = tmp_path / "data" / "cards.csv"

    calls = []

    def mock_run(cmd, *args, **kwargs):
        calls.append(cmd)
        if "check_db" in str(cmd):
            return type("R", (), {"returncode": 0})()
        if "generate_cards_csv" in str(cmd):
            cards_csv.write_text("id,name,type,attribute,race,level,attack_points,defense_points,cost,rarity,description,image\n1,Test,,,,0,0,0,,,,")
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_run)
    monkeypatch.setattr(setup, "CARDS_CSV", cards_csv)
    monkeypatch.setattr(setup, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(setup, "SCRIPT_DIR", Path(__file__).parent.parent / "src")
    monkeypatch.setattr("src.generate_cards_csv.CARD_LIST", card_list)
    monkeypatch.setattr("src.generate_cards_csv.CARDS_OUT", cards_csv)

    setup.main()

    assert any("generate_cards_csv" in str(c) for c in calls)
