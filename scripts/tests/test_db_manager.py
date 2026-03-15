import sys
from typing import List, Optional, Tuple
from unittest.mock import patch

import pytest

from src import db_manager


class StubCursor:
    def __init__(
        self,
        fetchone_values: Optional[List] = None,
        fetchall_values: Optional[List[List]] = None,
    ) -> None:
        self.statements: List[Tuple[str, Optional[Tuple]]] = []
        self.fetchone_values = list(fetchone_values or [])
        self.fetchall_values = list(fetchall_values or [])

    def execute(self, query, params=None):
        self.statements.append((str(query), params))

    def fetchone(self):
        if not self.fetchone_values:
            raise AssertionError("fetchone called with no values left")
        value = self.fetchone_values.pop(0)
        return value if isinstance(value, tuple) else (value,)

    def fetchall(self):
        if not self.fetchall_values:
            if any("information_schema.tables" in stmt for stmt, _ in self.statements):
                return [("cards",), ("decks",), ("deck_cards",)]
            return []
        return self.fetchall_values.pop(0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class StubConnection:
    def __init__(self, cursor: StubCursor) -> None:
        self.cursor_obj = cursor
        self.autocommit = False

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
def patch_connection(monkeypatch):
    def _patch(fetchone_values=None, fetchall_values=None):
        cursor = StubCursor(fetchone_values=fetchone_values, fetchall_values=fetchall_values)
        conn = StubConnection(cursor)

        def fake_get_connection():
            conn.autocommit = True
            return conn

        monkeypatch.setattr(db_manager, "get_connection", fake_get_connection)
        return cursor

    return _patch


def test_reset_database_executes_expected_sql(patch_connection):
    cursor = patch_connection()
    db_manager.reset_database()
    statements = [stmt for stmt, _ in cursor.statements]
    assert "DROP SCHEMA public CASCADE;" in statements
    assert "CREATE SCHEMA public;" in statements
    assert f"GRANT ALL ON SCHEMA public TO {db_manager.DB_SETTINGS['user']};" in statements


def test_clear_all_tables_runs_truncate(patch_connection):
    cursor = patch_connection()
    db_manager.clear_all_tables()
    truncate = [s for s, _ in cursor.statements if "TRUNCATE TABLE" in s]
    assert len(truncate) == 1
    assert "RESTART IDENTITY CASCADE" in truncate[0]


def test_clear_table_valid_and_invalid(patch_connection, capsys):
    patch_connection(fetchone_values=[True])
    db_manager.clear_table("cards")

    patch_connection(fetchone_values=[False])
    with pytest.raises(SystemExit):
        db_manager.clear_table("unknown")
    captured = capsys.readouterr()
    assert "Unsupported table" in captured.err


def test_seed_calls_seed_from_csv(monkeypatch):
    with patch("subprocess.run") as mock_run:
        db_manager.seed()
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "seed_from_csv.py" in str(call_args[1])


def test_migrate_calls_run_migrations(monkeypatch):
    with patch("subprocess.run") as mock_run:
        db_manager.migrate()
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "run_migrations.py" in str(call_args[1])


def test_main_seed(monkeypatch):
    with patch("subprocess.run"):
        monkeypatch.setattr(sys, "argv", ["db_manager.py", "seed"])
        db_manager.main()


def test_main_migrate(monkeypatch):
    with patch("subprocess.run"):
        monkeypatch.setattr(sys, "argv", ["db_manager.py", "migrate"])
        db_manager.main()


def test_main_other_commands(monkeypatch, patch_connection):
    patch_connection()
    monkeypatch.setattr(sys, "argv", ["db_manager.py", "clear-all"])
    db_manager.main()

    patch_connection(fetchone_values=[True])
    monkeypatch.setattr(sys, "argv", ["db_manager.py", "clear-table", "cards"])
    db_manager.main()

    patch_connection()
    monkeypatch.setattr(sys, "argv", ["db_manager.py", "reset-db"])
    db_manager.main()


def test_main_no_command_exits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["db_manager.py"])
    with pytest.raises(SystemExit):
        db_manager.main()


def test_get_connection_success(monkeypatch):
    import psycopg2

    mock_conn = StubConnection(StubCursor())
    monkeypatch.setattr(psycopg2, "connect", lambda **kwargs: mock_conn)
    conn = db_manager.get_connection()
    assert conn is not None


def test_get_connection_error(monkeypatch, capsys):
    import psycopg2

    def fake_connect(**kwargs):
        raise psycopg2.Error("Connection failed")

    monkeypatch.setattr(psycopg2, "connect", fake_connect)
    with pytest.raises(SystemExit):
        db_manager.get_connection()
    captured = capsys.readouterr()
    assert "Unable to connect" in captured.err


def test_clear_all_tables_no_tables(patch_connection, capsys):
    patch_connection(fetchall_values=[[]])
    with pytest.raises(SystemExit):
        db_manager.clear_all_tables()
    captured = capsys.readouterr()
    assert "Tables do not exist" in captured.err


def test_clear_table_not_exists(patch_connection, capsys):
    patch_connection(fetchone_values=[False])
    with pytest.raises(SystemExit):
        db_manager.clear_table("cards")
    captured = capsys.readouterr()
    assert "does not exist" in captured.err


def test_show_status_no_tables(patch_connection, capsys):
    patch_connection(fetchall_values=[[]])
    db_manager.show_status()
    captured = capsys.readouterr()
    assert "Tables do not exist" in captured.out


def test_show_status_with_data(patch_connection, capsys):
    patch_connection(
        fetchall_values=[[("cards",), ("decks",), ("deck_cards",)]],
        fetchone_values=[(10,), (2,), (20,), (1, 900)],
    )
    db_manager.show_status()
    captured = capsys.readouterr()
    assert "Database Status" in captured.out
    assert "Card ID range" in captured.out


def test_main_status_command(monkeypatch, patch_connection):
    patch_connection(
        fetchall_values=[[("cards",), ("decks",)]],
        fetchone_values=[5, 2, (1, 900)],
    )
    monkeypatch.setattr(sys, "argv", ["db_manager.py", "status"])
    db_manager.main()
