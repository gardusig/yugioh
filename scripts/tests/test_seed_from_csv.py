"""Tests for seed_from_csv module."""
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from unittest.mock import patch

import pytest

from src import seed_from_csv


class StubCursor:
    def __init__(self, fetchone_values: Optional[List] = None) -> None:
        self.statements: List[Tuple[str, Optional[Tuple]]] = []
        self.fetchone_values = list(fetchone_values or [])

    def execute(self, query, params=None):
        self.statements.append((str(query), params))

    def fetchone(self):
        if not self.fetchone_values:
            raise AssertionError("fetchone called with no values left")
        return (self.fetchone_values.pop(0),)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class StubConnection:
    def __init__(self, cursor: StubCursor) -> None:
        self.cursor_obj = cursor

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        pass

    def close(self):
        pass


def test_get_data_dir():
    """get_data_dir returns a path ending in data (project_root/data)."""
    result = seed_from_csv.get_data_dir()
    assert result.name == "data"
    # Path is .../something/data; in repo it's .../yugioh/data, in Docker .../app/data
    assert len(result.parts) >= 2
    assert result.parts[-1] == "data"


def test_get_connection_success(monkeypatch):
    """get_connection returns connection on success."""
    mock_conn = StubConnection(StubCursor())
    monkeypatch.setattr("psycopg2.connect", lambda **kwargs: mock_conn)
    conn = seed_from_csv.get_connection()
    assert conn is mock_conn


def test_get_connection_error(monkeypatch, capsys):
    """get_connection exits on psycopg2 error."""
    import psycopg2

    def fake_connect(**kwargs):
        raise psycopg2.Error("Connection failed")

    monkeypatch.setattr("psycopg2.connect", fake_connect)
    with pytest.raises(SystemExit):
        seed_from_csv.get_connection()
    captured = capsys.readouterr()
    assert "Cannot connect" in captured.err


def test_seed_cards_inserts_rows(tmp_path, monkeypatch):
    """seed_cards reads CSV and executes INSERTs."""
    cards_csv = tmp_path / "cards.csv"
    cards_csv.write_text(
        "id,name,type,attribute,race,level,attack_points,defense_points,cost,rarity,description,image\n"
        "1,Test Card,Normal Monster,LIGHT,Dragon,4,1500,1200,4,Common,,"
    )
    cursor = StubCursor()
    conn = StubConnection(cursor)
    conn.cursor_obj = cursor

    count = seed_from_csv.seed_cards(conn, tmp_path)
    assert count == 1
    inserts = [s for s, _ in cursor.statements if "INSERT INTO cards" in s]
    assert len(inserts) == 1
    assert "Test Card" in str(cursor.statements)


def test_seed_cards_missing_file(tmp_path, capsys):
    """seed_cards exits when cards.csv missing."""
    cursor = StubCursor()
    conn = StubConnection(cursor)
    with pytest.raises(SystemExit):
        seed_from_csv.seed_cards(conn, tmp_path)
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_seed_decks_returns_name_to_id(tmp_path, monkeypatch):
    """seed_decks inserts decks and returns name->id mapping."""
    decks_csv = tmp_path / "decks.csv"
    decks_csv.write_text(
        "name,description,character_name,archetype,max_cost,is_preset\n"
        "Test Deck,A deck,,Dragon,250,true"
    )
    cursor = StubCursor(fetchone_values=[101])
    conn = StubConnection(cursor)

    result = seed_from_csv.seed_decks(conn, tmp_path)
    assert result == {"Test Deck": 101}
    inserts = [s for s, _ in cursor.statements if "INSERT INTO decks" in s]
    assert len(inserts) == 1


def test_seed_decks_missing_returns_empty(tmp_path, capsys):
    """seed_decks returns {} when decks.csv missing."""
    cursor = StubCursor()
    conn = StubConnection(cursor)
    result = seed_from_csv.seed_decks(conn, tmp_path)
    assert result == {}
    captured = capsys.readouterr()
    assert "not found" in captured.err or "Skipping" in captured.err


def test_seed_deck_cards_inserts(tmp_path, monkeypatch):
    """seed_deck_cards inserts deck_cards rows."""
    dc_csv = tmp_path / "deck_cards.csv"
    dc_csv.write_text("deck_name,card_id,position\nTest Deck,1,1\nTest Deck,2,2")
    cursor = StubCursor()
    conn = StubConnection(cursor)
    name_to_id = {"Test Deck": 10}

    count = seed_from_csv.seed_deck_cards(conn, tmp_path, name_to_id)
    assert count == 2
    inserts = [s for s, _ in cursor.statements if "INSERT INTO deck_cards" in s]
    assert len(inserts) == 2


def test_seed_deck_cards_skips_unknown_deck(tmp_path, capsys):
    """seed_deck_cards skips rows with unknown deck_name."""
    dc_csv = tmp_path / "deck_cards.csv"
    dc_csv.write_text("deck_name,card_id,position\nUnknown Deck,1,1")
    cursor = StubCursor()
    conn = StubConnection(cursor)
    name_to_id = {"Other Deck": 10}

    count = seed_from_csv.seed_deck_cards(conn, tmp_path, name_to_id)
    assert count == 0
    captured = capsys.readouterr()
    assert "Unknown deck" in captured.err


def test_seed_deck_cards_missing_returns_zero(tmp_path):
    """seed_deck_cards returns 0 when file missing."""
    cursor = StubCursor()
    conn = StubConnection(cursor)
    count = seed_from_csv.seed_deck_cards(conn, tmp_path, {"Deck": 1})
    assert count == 0


def test_seed_deck_cards_empty_name_to_id(tmp_path, capsys):
    """seed_deck_cards returns 0 when name_to_id empty."""
    dc_csv = tmp_path / "deck_cards.csv"
    dc_csv.write_text("deck_name,card_id,position\nDeck,1,1")
    cursor = StubCursor()
    conn = StubConnection(cursor)
    count = seed_from_csv.seed_deck_cards(conn, tmp_path, {})
    assert count == 0


def test_main_success(tmp_path, monkeypatch, capsys):
    """main seeds and prints success."""
    (tmp_path / "cards.csv").write_text(
        "id,name,type,attribute,race,level,attack_points,defense_points,cost,rarity,description,image\n"
        "1,Card,Normal Monster,LIGHT,Dragon,4,0,0,4,,,"
    )
    (tmp_path / "decks.csv").write_text(
        "name,description,character_name,archetype,max_cost,is_preset\n"
        "Deck1,,,Dragon,250,true"
    )
    (tmp_path / "deck_cards.csv").write_text("deck_name,card_id,position\nDeck1,1,1")

    cursor = StubCursor(fetchone_values=[1])  # deck id for INSERT RETURNING
    conn = StubConnection(cursor)

    def fake_connect(**kwargs):
        return conn

    monkeypatch.setattr("psycopg2.connect", fake_connect)
    monkeypatch.setattr(sys, "argv", ["seed_from_csv.py", "--data-dir", str(tmp_path)])

    seed_from_csv.main()
    captured = capsys.readouterr()
    assert "OK" in captured.out
    assert "cards" in captured.out
    assert "decks" in captured.out


def test_main_data_dir_not_found(monkeypatch, capsys):
    """main exits when data dir does not exist."""
    monkeypatch.setattr(sys, "argv", ["seed_from_csv.py", "--data-dir", "/nonexistent/path"])
    with pytest.raises(SystemExit):
        seed_from_csv.main()
    captured = capsys.readouterr()
    assert "not found" in captured.err
