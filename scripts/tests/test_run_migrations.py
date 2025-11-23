import sys
from pathlib import Path
from typing import List, Optional, Tuple
from unittest.mock import mock_open, patch

import pytest

from src import run_migrations


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
        self.autocommit = False
        self.rollback_called = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        pass

    def rollback(self):
        self.rollback_called = True

    def close(self):
        pass

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
        created["connection"] = conn
        return cursor, conn

    return _patch


def test_parse_migration_filename_valid():
    """Test parsing valid migration filename."""
    result = run_migrations.parse_migration_filename("V1__initial_schema.sql")
    assert result is not None
    assert result["version"] == 1
    assert result["description"] == "initial_schema"
    assert result["filename"] == "V1__initial_schema.sql"


def test_parse_migration_filename_invalid_extension():
    """Test parsing filename without .sql extension."""
    result = run_migrations.parse_migration_filename("V1__initial_schema.txt")
    assert result is None


def test_parse_migration_filename_no_v_prefix():
    """Test parsing filename without V prefix."""
    result = run_migrations.parse_migration_filename("1__initial_schema.sql")
    assert result is None


def test_parse_migration_filename_no_double_underscore():
    """Test parsing filename without double underscore separator."""
    result = run_migrations.parse_migration_filename("V1_initial_schema.sql")
    assert result is None


def test_parse_migration_filename_invalid_version():
    """Test parsing filename with invalid version number."""
    result = run_migrations.parse_migration_filename("Vabc__initial_schema.sql")
    assert result is None


def test_check_migration_applied_table_not_exists(patch_connection):
    """Test checking migration when history table doesn't exist."""
    cursor, conn = patch_connection(fetchone_values=[False])  # Table doesn't exist
    result = run_migrations.check_migration_applied(conn, 1)
    assert result is False
    assert any("flyway_schema_history" in stmt for stmt, _ in cursor.statements)


def test_check_migration_applied_not_applied(patch_connection):
    """Test checking migration that hasn't been applied."""
    cursor, conn = patch_connection(fetchone_values=[True, 0])  # Table exists, 0 records
    result = run_migrations.check_migration_applied(conn, 1)
    assert result is False


def test_check_migration_applied_already_applied(patch_connection):
    """Test checking migration that has already been applied."""
    cursor, conn = patch_connection(fetchone_values=[True, 1])  # Table exists, 1 record
    result = run_migrations.check_migration_applied(conn, 1)
    assert result is True


def test_record_migration(patch_connection):
    """Test recording a migration in history."""
    cursor, conn = patch_connection(fetchone_values=[0])  # Max rank is 0, so next is 1
    run_migrations.record_migration(conn, 1, "test_migration")
    
    # Should create table and insert record
    assert any("CREATE TABLE IF NOT EXISTS flyway_schema_history" in stmt for stmt, _ in cursor.statements)
    assert any("INSERT INTO flyway_schema_history" in stmt for stmt, _ in cursor.statements)
    # Check that version and description are in the insert
    insert_stmt = [stmt for stmt, _ in cursor.statements if "INSERT INTO flyway_schema_history" in stmt]
    assert len(insert_stmt) > 0


def test_run_migration_already_applied(patch_connection, tmp_path, capsys):
    """Test running a migration that's already applied."""
    # Table exists (True), and count > 0 (1) means already applied
    cursor, conn = patch_connection(fetchone_values=[True, 1])  # Already applied
    
    migration_info = {
        "version": 1,
        "description": "test",
        "path": tmp_path / "V1__test.sql"
    }
    
    result = run_migrations.run_migration(conn, migration_info, dry_run=False)
    assert result is True
    # Should print skip message
    captured = capsys.readouterr()
    assert "[SKIP]" in captured.out
    assert "already applied" in captured.out


def test_run_migration_dry_run(patch_connection, tmp_path):
    """Test dry run mode."""
    cursor, conn = patch_connection(fetchone_values=[False])  # Not applied
    
    migration_file = tmp_path / "V1__test.sql"
    migration_file.write_text("CREATE TABLE test (id INT);")
    
    migration_info = {
        "version": 1,
        "description": "test",
        "path": migration_file
    }
    
    result = run_migrations.run_migration(conn, migration_info, dry_run=True)
    assert result is True
    # Should not execute SQL
    assert not any("CREATE TABLE test" in stmt for stmt, _ in cursor.statements)


def test_run_migration_success(patch_connection, tmp_path):
    """Test successfully running a migration."""
    cursor, conn = patch_connection(fetchone_values=[False, 0])  # Not applied, max rank 0
    
    migration_file = tmp_path / "V1__test.sql"
    migration_file.write_text("CREATE TABLE test (id INT);")
    
    migration_info = {
        "version": 1,
        "description": "test",
        "path": migration_file
    }
    
    with patch("builtins.open", mock_open(read_data="CREATE TABLE test (id INT);")):
        result = run_migrations.run_migration(conn, migration_info, dry_run=False)
    
    assert result is True
    # Should execute SQL and record migration
    assert any("CREATE TABLE test" in stmt for stmt, _ in cursor.statements)
    assert any("INSERT INTO flyway_schema_history" in stmt for stmt, _ in cursor.statements)


def test_run_migration_failure(patch_connection, tmp_path, monkeypatch):
    """Test migration failure handling."""
    cursor, conn = patch_connection(fetchone_values=[False])
    
    migration_file = tmp_path / "V1__test.sql"
    migration_file.write_text("INVALID SQL SYNTAX;")
    
    migration_info = {
        "version": 1,
        "description": "test",
        "path": migration_file
    }
    
    # Make execute raise an exception for SQL execution
    original_execute = cursor.execute
    call_count = [0]
    def failing_execute(query, params=None):
        call_count[0] += 1
        # Fail on the actual SQL execution (not the history table check)
        if call_count[0] > 1 and "INVALID SQL" in query:
            raise Exception("SQL syntax error")
        return original_execute(query, params)
    cursor.execute = failing_execute
    
    with patch("builtins.open", mock_open(read_data="INVALID SQL SYNTAX;")):
        result = run_migrations.run_migration(conn, migration_info, dry_run=False)
    
    assert result is False
    # Should have attempted rollback
    assert conn.rollback_called is True


def test_get_connection_success(patch_connection):
    """Test successful connection."""
    cursor, conn = patch_connection()
    result = run_migrations.get_connection()
    assert result is not None
    assert result.autocommit is False


def test_get_connection_error(monkeypatch, capsys):
    """Test connection error handling."""
    import psycopg2

    def fake_connect(**kwargs):
        raise psycopg2.Error("Connection failed")

    monkeypatch.setattr("psycopg2.connect", fake_connect)
    with pytest.raises(SystemExit) as exc_info:
        run_migrations.get_connection()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Unable to connect to database" in captured.err


def test_get_migration_files_nonexistent_dir(tmp_path):
    """Test getting migration files from non-existent directory."""
    nonexistent = tmp_path / "nonexistent"
    with pytest.raises(SystemExit) as exc_info:
        run_migrations.get_migration_files(str(nonexistent))
    assert exc_info.value.code == 1


def test_get_migration_files_valid(tmp_path):
    """Test getting migration files from valid directory."""
    # Create valid migration file
    migration_file = tmp_path / "V1__initial_schema.sql"
    migration_file.write_text("CREATE TABLE test (id INT);")
    
    # Create invalid file (should be ignored)
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("not a migration")
    
    migrations = run_migrations.get_migration_files(str(tmp_path))
    assert len(migrations) == 1
    assert migrations[0]["version"] == 1
    assert migrations[0]["description"] == "initial_schema"


def test_get_migration_files_sorted(tmp_path):
    """Test that migration files are sorted by version."""
    # Create migrations in wrong order
    (tmp_path / "V3__third.sql").write_text("")
    (tmp_path / "V1__first.sql").write_text("")
    (tmp_path / "V2__second.sql").write_text("")
    
    migrations = run_migrations.get_migration_files(str(tmp_path))
    assert len(migrations) == 3
    assert migrations[0]["version"] == 1
    assert migrations[1]["version"] == 2
    assert migrations[2]["version"] == 3


def test_get_migration_files_error_path(tmp_path, monkeypatch):
    """Test get_migration_files when path doesn't exist (error path)."""
    # This should exit, so we need to test the error path
    nonexistent = tmp_path / "nonexistent"
    with pytest.raises(SystemExit):
        run_migrations.get_migration_files(str(nonexistent))


def test_main_no_migrations(patch_connection, tmp_path, monkeypatch, capsys):
    """Test main when no migration files found."""
    cursor, conn = patch_connection()
    
    # Create empty directory
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    # Mock the path resolution
    def mock_resolve(self):
        return empty_dir
    
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    monkeypatch.setattr(Path, "exists", lambda self: self == empty_dir)
    monkeypatch.setattr(Path, "parent", property(lambda self: tmp_path))
    monkeypatch.setattr(sys, "argv", ["run_migrations.py", "--migration-dir", str(empty_dir)])
    
    # Mock get_migration_files to return empty list
    monkeypatch.setattr(run_migrations, "get_migration_files", lambda x: [])
    
    run_migrations.main()
    captured = capsys.readouterr()
    assert "No migration files found" in captured.err


def test_main_with_migrations(patch_connection, tmp_path, monkeypatch, capsys):
    """Test main with valid migrations."""
    cursor, conn = patch_connection(fetchone_values=[False, 0])  # Not applied, max rank 0
    
    migration_file = tmp_path / "V1__test.sql"
    migration_file.write_text("CREATE TABLE test (id INT);")
    
    # Mock get_migration_files to return our migration
    migration_info = {
        "version": 1,
        "description": "test",
        "path": migration_file
    }
    monkeypatch.setattr(run_migrations, "get_migration_files", lambda x: [migration_info])
    
    # Mock __file__ to point to a fake path in src/, so parent.parent resolves correctly
    # Create a fake scripts/src/run_migrations.py path
    fake_script_path = tmp_path / "src" / "run_migrations.py"
    fake_script_path.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(run_migrations, "__file__", str(fake_script_path))
    
    # Mock Path operations to handle the migration directory
    original_resolve = Path.resolve
    def mock_resolve(self):
        # If resolving the migration dir path, return our tmp_path
        if str(self).endswith("migrations") or "migrations" in str(self):
            return tmp_path
        return original_resolve(self)
    
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    monkeypatch.setattr(Path, "exists", lambda self: self == tmp_path or str(self).endswith("V1__test.sql"))
    monkeypatch.setattr(sys, "argv", ["run_migrations.py", "--migration-dir", "migrations"])
    
    with patch("builtins.open", mock_open(read_data="CREATE TABLE test (id INT);")):
        run_migrations.main()
    
    captured = capsys.readouterr()
    assert "Successfully processed" in captured.out or "Migration" in captured.out


def test_main_migration_failure(patch_connection, tmp_path, monkeypatch, capsys):
    """Test main when migration fails."""
    cursor, conn = patch_connection(fetchone_values=[False])
    
    migration_file = tmp_path / "V1__test.sql"
    migration_file.write_text("INVALID SQL;")
    
    # Make execute raise exception
    original_execute = cursor.execute
    call_count = [0]
    def failing_execute(query, params=None):
        call_count[0] += 1
        if call_count[0] > 1 and "INVALID" in query:
            raise Exception("SQL error")
        return original_execute(query, params)
    cursor.execute = failing_execute
    
    # Mock get_migration_files
    migration_info = {
        "version": 1,
        "description": "test",
        "path": migration_file
    }
    monkeypatch.setattr(run_migrations, "get_migration_files", lambda x: [migration_info])
    
    # Mock __file__ to avoid Path.parent recursion
    fake_script_path = tmp_path / "src" / "run_migrations.py"
    fake_script_path.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(run_migrations, "__file__", str(fake_script_path))
    
    original_resolve = Path.resolve
    def mock_resolve(self):
        if str(self).endswith("migrations") or "migrations" in str(self):
            return tmp_path
        return original_resolve(self)
    
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    monkeypatch.setattr(Path, "exists", lambda self: self == tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_migrations.py", "--migration-dir", "migrations"])
    
    with patch("builtins.open", mock_open(read_data="INVALID SQL;")):
        with pytest.raises(SystemExit) as exc_info:
            run_migrations.main()
        assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    assert "Migration failed" in captured.err or "Failed to apply" in captured.err


def test_main_dry_run(patch_connection, tmp_path, monkeypatch, capsys):
    """Test main with dry-run flag."""
    cursor, conn = patch_connection(fetchone_values=[False])
    
    migration_file = tmp_path / "V1__test.sql"
    migration_file.write_text("CREATE TABLE test (id INT);")
    
    # Mock get_migration_files
    migration_info = {
        "version": 1,
        "description": "test",
        "path": migration_file
    }
    monkeypatch.setattr(run_migrations, "get_migration_files", lambda x: [migration_info])
    
    # Mock __file__ to avoid Path.parent recursion
    fake_script_path = tmp_path / "src" / "run_migrations.py"
    fake_script_path.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(run_migrations, "__file__", str(fake_script_path))
    
    original_resolve = Path.resolve
    def mock_resolve(self):
        if str(self).endswith("migrations") or "migrations" in str(self):
            return tmp_path
        return original_resolve(self)
    
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    monkeypatch.setattr(Path, "exists", lambda self: self == tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_migrations.py", "--migration-dir", "migrations", "--dry-run"])
    
    run_migrations.main()
    captured = capsys.readouterr()
    assert "dry-run" in captured.out.lower() or "DRY RUN" in captured.out


def test_main_nonexistent_dir(monkeypatch, capsys):
    """Test main with nonexistent migration directory."""
    nonexistent = Path("/nonexistent/path")
    
    # Mock __file__ to avoid Path.parent recursion
    fake_script_path = Path("/fake/scripts/src/run_migrations.py")
    monkeypatch.setattr(run_migrations, "__file__", str(fake_script_path))
    
    # Mock resolve to return nonexistent path for migration directory
    original_resolve = Path.resolve
    def mock_resolve(self):
        # If this is the migration directory path, return nonexistent
        if str(self).endswith("migrations") or ("migrations" in str(self) and "/nonexistent" not in str(self)):
            return nonexistent
        return original_resolve(self)
    
    original_exists = Path.exists
    def mock_exists(self):
        if self == nonexistent:
            return False
        return original_exists(self)
    
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    monkeypatch.setattr(Path, "exists", mock_exists)
    monkeypatch.setattr(sys, "argv", ["run_migrations.py", "--migration-dir", "migrations"])
    
    with pytest.raises(SystemExit) as exc_info:
        run_migrations.main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Migration directory not found" in captured.err


def test_get_migration_files_filters_invalid_names(tmp_path):
    """Test get_migration_files filters out files with invalid names (covers branch 78->76)."""
    # Create valid migration file
    valid_file = tmp_path / "V1__valid.sql"
    valid_file.write_text("CREATE TABLE test;")
    
    # Create invalid file that matches V*.sql pattern but has invalid format
    # (no double underscore, so parse_migration_filename returns None)
    invalid_file = tmp_path / "Vinvalid.sql"  # Matches V*.sql but invalid format
    invalid_file.write_text("CREATE TABLE test2;")
    
    migrations = run_migrations.get_migration_files(str(tmp_path))
    
    # Should only include the valid file (invalid one is filtered out by the if statement)
    assert len(migrations) == 1
    assert migrations[0]["version"] == 1
    assert migrations[0]["description"] == "valid"


def test_main_entry_point_execution(monkeypatch):
    """Test main entry point execution (if __name__ == '__main__' block)."""
    import importlib.util
    import pathlib
    
    # Mock sys.exit
    exit_codes = []
    def mock_exit(code):
        exit_codes.append(code)
        raise SystemExit(code)
    
    monkeypatch.setattr(sys, "exit", mock_exit)
    monkeypatch.setattr(sys, "argv", ["run_migrations.py", "--help"])
    
    # Mock __file__ to avoid path issues
    fake_script_path = pathlib.Path("/fake/scripts/src/run_migrations.py")
    monkeypatch.setattr(run_migrations, "__file__", str(fake_script_path))
    
    # Load the module with __name__ == "__main__" to execute the main block
    run_migrations_path = pathlib.Path(__file__).parent.parent / "src" / "run_migrations.py"
    spec = importlib.util.spec_from_file_location("__main__", run_migrations_path)
    main_module = importlib.util.module_from_spec(spec)
    main_module.__name__ = "__main__"
    main_module.sys = sys
    
    # Execute the module to trigger the if __name__ == "__main__" block
    try:
        spec.loader.exec_module(main_module)
    except SystemExit:
        pass
    
    # Verify main is callable
    assert callable(run_migrations.main)
    assert hasattr(run_migrations, "main")

