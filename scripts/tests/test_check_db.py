import sys
from typing import List, Optional, Tuple

import pytest

from src import check_db


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
        # Return as tuple if not already
        if isinstance(value, tuple):
            return value
        return (value,)

    def fetchall(self):
        if not self.fetchall_values:
            return []
        return self.fetchall_values.pop(0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class StubConnection:
    def __init__(self, cursor: StubCursor) -> None:
        self.cursor_obj = cursor

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
def patch_connection(monkeypatch):
    created = {}

    def _patch(fetchone_values: Optional[List] = None):
        cursor = StubCursor(fetchone_values=fetchone_values)
        conn = StubConnection(cursor)

        def fake_connect(**kwargs):
            return conn

        monkeypatch.setattr("psycopg2.connect", fake_connect)
        created["cursor"] = cursor
        return cursor

    return _patch


def test_check_database_empty(patch_connection):
    """Test when database is empty (no cards table)."""
    cursor = patch_connection(fetchone_values=[False])  # Table doesn't exist
    result = check_db.check_database()
    assert result == 0
    # Should check for cards table existence
    assert any("information_schema.tables" in stmt for stmt, _ in cursor.statements)
    assert any("table_name = 'cards'" in stmt for stmt, _ in cursor.statements)


def test_check_database_no_cards(patch_connection):
    """Test when database has tables but no cards."""
    cursor = patch_connection(fetchone_values=[True, 0])  # Table exists, 0 cards
    result = check_db.check_database()
    assert result == 1
    # Should check table existence and count
    assert any("SELECT COUNT(*) FROM cards" in stmt for stmt, _ in cursor.statements)


def test_check_database_populated(patch_connection):
    """Test when database is populated."""
    cursor = patch_connection(fetchone_values=[True, 10])  # Table exists, 10 cards
    result = check_db.check_database()
    assert result == 2


def test_check_database_operational_error(monkeypatch, capsys):
    """Test handling of OperationalError (connection failure)."""
    import psycopg2

    def fake_connect(**kwargs):
        raise psycopg2.OperationalError("Connection failed")

    monkeypatch.setattr("psycopg2.connect", fake_connect)
    with pytest.raises(SystemExit) as exc_info:
        check_db.check_database()
    assert exc_info.value.code == 3
    captured = capsys.readouterr()
    assert "Database connection error" in captured.err


def test_check_database_general_error(monkeypatch, capsys):
    """Test handling of general exceptions."""
    def fake_connect(**kwargs):
        raise ValueError("Unexpected error")

    monkeypatch.setattr("psycopg2.connect", fake_connect)
    with pytest.raises(SystemExit) as exc_info:
        check_db.check_database()
    assert exc_info.value.code == 4
    captured = capsys.readouterr()
    assert "Error checking database" in captured.err


def test_main_entry_point(monkeypatch):
    """Test that main() is callable and entry point exists."""
    # Verify check_database exists and is callable
    assert callable(check_db.check_database)
    assert hasattr(check_db, "check_database")


def test_main_execution(patch_connection, monkeypatch):
    """Test main entry point execution (if __name__ == '__main__' block)."""
    cursor = patch_connection(fetchone_values=[True, 10])
    
    # Mock sys.exit to capture the exit code
    exit_codes = []
    def mock_exit(code):
        exit_codes.append(code)
        raise SystemExit(code)
    
    monkeypatch.setattr(sys, "exit", mock_exit)
    
    # Execute the main block code directly
    # The main block does: status = check_database(); sys.exit(status)
    try:
        status = check_db.check_database()
        sys.exit(status)
    except SystemExit:
        pass
    
    # Should have called sys.exit with status 2 (populated)
    assert len(exit_codes) > 0
    assert exit_codes[0] == 2


def test_main_entry_point_block(monkeypatch):
    """Test the if __name__ == '__main__' block execution."""
    import importlib.util
    import pathlib
    
    # Mock sys.exit
    exit_codes = []
    def mock_exit(code):
        exit_codes.append(code)
        raise SystemExit(code)
    
    monkeypatch.setattr(sys, "exit", mock_exit)
    
    # Patch get_connection for check_database to work
    import psycopg2
    mock_conn = StubConnection(StubCursor(fetchone_values=[True, 10]))
    def fake_connect(**kwargs):
        return mock_conn
    
    monkeypatch.setattr(psycopg2, "connect", fake_connect)
    
    # Load the module with __name__ == "__main__" to execute the main block
    check_db_path = pathlib.Path(__file__).parent.parent / "src" / "check_db.py"
    spec = importlib.util.spec_from_file_location("__main__", check_db_path)
    main_module = importlib.util.module_from_spec(spec)
    main_module.__name__ = "__main__"
    main_module.sys = sys
    
    # Execute the module to trigger the if __name__ == "__main__" block
    try:
        spec.loader.exec_module(main_module)
    except SystemExit:
        pass
    
    assert len(exit_codes) > 0

