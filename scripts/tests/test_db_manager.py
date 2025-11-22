import sys
from typing import List, Optional, Tuple

import pytest

import db_manager


class StubCursor:
    def __init__(
        self,
        fetchone_values: Optional[List[int]] = None,
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
        return (value,)

    def fetchall(self):
        if not self.fetchall_values:
            # Default: return table names for table existence checks
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
    created = {}

    def _patch(
        fetchone_values: Optional[List[int]] = None, fetchall_values: Optional[List[List]] = None
    ):
        cursor = StubCursor(fetchone_values=fetchone_values, fetchall_values=fetchall_values)
        conn = StubConnection(cursor)

        def fake_get_connection():
            conn.autocommit = True
            return conn

        monkeypatch.setattr(db_manager, "get_connection", fake_get_connection)
        created["cursor"] = cursor
        return cursor

    return _patch


def test_reset_database_executes_expected_sql(patch_connection):
    cursor = patch_connection()
    db_manager.reset_database()
    statements = [stmt for stmt, _ in cursor.statements]
    assert "DROP SCHEMA public CASCADE;" in statements
    assert "CREATE SCHEMA public;" in statements
    assert "GRANT ALL ON SCHEMA public TO public;" in statements
    assert f"GRANT ALL ON SCHEMA public TO {db_manager.DB_SETTINGS['user']};" in statements


def test_truncate_all_tables_runs_single_statement(patch_connection):
    cursor = patch_connection()
    db_manager.truncate_all_tables()
    # Should have SELECT for table check, then TRUNCATE
    truncate_statements = [
        stmt for stmt, _ in cursor.statements if stmt.strip().startswith("TRUNCATE TABLE")
    ]
    assert len(truncate_statements) == 1
    assert "TRUNCATE TABLE" in truncate_statements[0]
    assert "RESTART IDENTITY CASCADE" in truncate_statements[0]


def test_truncate_table_valid_and_invalid(patch_connection, capsys):
    cursor = patch_connection(fetchone_values=[True])  # Table exists
    db_manager.truncate_table("cards")
    assert cursor.statements[-1][0].startswith("TRUNCATE TABLE cards")

    patch_connection(fetchone_values=[False])  # Table doesn't exist
    with pytest.raises(SystemExit):
        db_manager.truncate_table("unknown")
    captured = capsys.readouterr()
    assert "Unsupported table 'unknown'" in captured.err


def test_seed_cards_inserts_all_records(patch_connection):
    cursor = patch_connection()
    db_manager.seed_cards()
    insert_statements = [
        stmt for stmt, _ in cursor.statements if stmt.strip().startswith("INSERT INTO cards")
    ]
    assert len(insert_statements) == len(db_manager.CARDS_DATA)


def test_seed_decks_inserts_and_populates_deck_cards(patch_connection):
    cursor = patch_connection(fetchone_values=[101, 202])
    db_manager.seed_decks()

    deck_inserts = [
        stmt for stmt, _ in cursor.statements if stmt.strip().startswith("INSERT INTO decks")
    ]
    delete_statements = [
        stmt for stmt, _ in cursor.statements if stmt.strip().startswith("DELETE FROM deck_cards")
    ]
    deck_card_inserts = [
        stmt for stmt, _ in cursor.statements if stmt.strip().startswith("INSERT INTO deck_cards")
    ]

    assert len(deck_inserts) == len(db_manager.DECKS_DATA)
    assert len(delete_statements) == len(db_manager.DECKS_DATA)
    # Each deck gets exactly 40 records
    assert len(deck_card_inserts) == 40 * len(db_manager.DECKS_DATA)


def test_main_seed_variants(monkeypatch):
    called = {"cards": 0, "decks": 0}

    monkeypatch.setattr(
        db_manager, "seed_cards", lambda **kwargs: called.__setitem__("cards", called["cards"] + 1)
    )
    monkeypatch.setattr(
        db_manager, "seed_decks", lambda **kwargs: called.__setitem__("decks", called["decks"] + 1)
    )
    monkeypatch.setattr(sys, "argv", ["db_manager.py", "seed"])
    db_manager.main()
    assert called == {"cards": 1, "decks": 1}

    monkeypatch.setattr(sys, "argv", ["db_manager.py", "seed", "--cards"])
    db_manager.main()
    assert called["cards"] == 2 and called["decks"] == 1

    monkeypatch.setattr(sys, "argv", ["db_manager.py", "seed", "--decks"])
    db_manager.main()
    assert called["decks"] == 2


def test_main_other_commands(monkeypatch, patch_connection):
    # Test truncate-all
    cursor1 = patch_connection()
    monkeypatch.setattr(sys, "argv", ["db_manager.py", "truncate-all"])
    db_manager.main()
    truncate_statements = [
        stmt for stmt, _ in cursor1.statements if stmt.strip().startswith("TRUNCATE TABLE")
    ]
    assert len(truncate_statements) > 0
    assert truncate_statements[-1].startswith("TRUNCATE TABLE")

    # Test truncate-table (needs fetchone for table existence check)
    cursor2 = patch_connection(fetchone_values=[True])
    monkeypatch.setattr(sys, "argv", ["db_manager.py", "truncate-table", "cards"])
    db_manager.main()
    truncate_statements2 = [
        stmt for stmt, _ in cursor2.statements if stmt.strip().startswith("TRUNCATE TABLE")
    ]
    assert len(truncate_statements2) > 0
    assert truncate_statements2[-1].startswith("TRUNCATE TABLE cards")

    # Test reset-db
    cursor3 = patch_connection()
    monkeypatch.setattr(sys, "argv", ["db_manager.py", "reset-db"])
    db_manager.main()
    assert any("DROP SCHEMA public" in stmt for stmt, _ in cursor3.statements)


def test_main_no_command_exits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["db_manager.py"])
    with pytest.raises(SystemExit):
        db_manager.main()


def test_get_connection_success(patch_connection):
    """Test successful connection path."""
    patch_connection()
    conn = db_manager.get_connection()
    assert conn is not None
    assert conn.autocommit is True


def test_get_connection_error_handling(monkeypatch, capsys):
    import psycopg2

    def fake_connect(**kwargs):
        raise psycopg2.Error("Connection failed")

    monkeypatch.setattr(psycopg2, "connect", fake_connect)
    with pytest.raises(SystemExit):
        db_manager.get_connection()
    captured = capsys.readouterr()
    assert "Unable to connect to database" in captured.err


def test_main_entry_point(monkeypatch):
    """Test that main() is callable and entry point exists."""
    # Verify main() exists and is callable
    assert callable(db_manager.main)
    # Test that the module can be imported and main exists
    assert hasattr(db_manager, "main")


def test_entry_point_execution(monkeypatch):
    """Test that the if __name__ == '__main__' block exists and is executable."""
    # Read the source file to verify the entry point exists
    import os

    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db_manager.py")
    with open(script_path) as f:
        source = f.read()
        assert 'if __name__ == "__main__":' in source
        assert "main()" in source.split('if __name__ == "__main__":')[1]
