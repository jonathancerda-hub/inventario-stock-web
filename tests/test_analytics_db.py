# tests/test_analytics_db.py
"""
Tests para AnalyticsDB usando SQLite en memoria.
No requiere conexión a PostgreSQL ni archivo en disco: usa una BD temporal.
"""

import pytest
import sqlite3
import os
from unittest.mock import patch
from datetime import datetime


# ---------------------------------------------------------------------------
# Fixture: AnalyticsDB con SQLite en memoria
# ---------------------------------------------------------------------------

@pytest.fixture
def analytics_db_memory(tmp_path):
    """
    Instancia de AnalyticsDB con SQLite usando un archivo temporal.
    Evita contaminación entre tests y no deja archivos residuales.
    """
    db_file = str(tmp_path / 'test_analytics.db')
    with patch.dict('os.environ', {'DATABASE_URL': ''}, clear=False):
        from analytics_db import AnalyticsDB
        db = AnalyticsDB.__new__(AnalyticsDB)
        db.db_type = 'sqlite'
        db.db_path = db_file
        db.table_prefix = ''
        import pytz
        db.local_tz = pytz.timezone('America/Lima')
        db.peru_tz = db.local_tz
        db._create_tables()
        return db


# ---------------------------------------------------------------------------
# _create_tables: verifica que la tabla se crea correctamente
# ---------------------------------------------------------------------------

class TestCreateTables:
    def test_table_exists_after_init(self, analytics_db_memory):
        with sqlite3.connect(analytics_db_memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='page_visits'"
            )
            row = cursor.fetchone()
        assert row is not None, "La tabla page_visits debe existir"

    def test_table_has_expected_columns(self, analytics_db_memory):
        with sqlite3.connect(analytics_db_memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(page_visits)")
            columns = {row[1] for row in cursor.fetchall()}
        expected = {'id', 'user_email', 'user_name', 'page_url', 'visit_timestamp'}
        assert expected.issubset(columns)


# ---------------------------------------------------------------------------
# log_visit
# ---------------------------------------------------------------------------

class TestLogVisit:
    def test_log_visit_inserts_row(self, analytics_db_memory):
        analytics_db_memory.log_visit(
            user_email='test@agrovetmarket.com',
            user_name='Test User',
            page_url='/inventory',
            page_title='inventory',
        )
        with sqlite3.connect(analytics_db_memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM page_visits")
            count = cursor.fetchone()[0]
        assert count == 1

    def test_log_visit_stores_correct_email(self, analytics_db_memory):
        analytics_db_memory.log_visit(
            user_email='maria@agrovetmarket.com',
            user_name='María',
            page_url='/dashboard',
        )
        with sqlite3.connect(analytics_db_memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_email FROM page_visits")
            row = cursor.fetchone()
        assert row[0] == 'maria@agrovetmarket.com'

    def test_log_visit_multiple_rows(self, analytics_db_memory):
        for i in range(5):
            analytics_db_memory.log_visit(
                user_email=f'user{i}@agrovetmarket.com',
                user_name=f'User {i}',
                page_url='/inventory',
            )
        with sqlite3.connect(analytics_db_memory.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM page_visits")
            count = cursor.fetchone()[0]
        assert count == 5


# ---------------------------------------------------------------------------
# get_total_visits
# ---------------------------------------------------------------------------

class TestGetTotalVisits:
    def test_returns_zero_on_empty_db(self, analytics_db_memory):
        result = analytics_db_memory.get_total_visits()
        assert result == 0

    def test_returns_correct_count_after_inserts(self, analytics_db_memory):
        analytics_db_memory.log_visit('a@test.com', 'A', '/inventory')
        analytics_db_memory.log_visit('b@test.com', 'B', '/dashboard')
        result = analytics_db_memory.get_total_visits(days=30)
        assert result == 2

    def test_returns_int(self, analytics_db_memory):
        result = analytics_db_memory.get_total_visits()
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# get_unique_users
# ---------------------------------------------------------------------------

class TestGetUniqueUsers:
    def test_returns_zero_on_empty_db(self, analytics_db_memory):
        result = analytics_db_memory.get_unique_users()
        assert result == 0

    def test_counts_each_user_once(self, analytics_db_memory):
        # Mismo usuario, 3 visitas → cuenta como 1
        for _ in range(3):
            analytics_db_memory.log_visit('juan@test.com', 'Juan', '/inventory')
        result = analytics_db_memory.get_unique_users(days=30)
        assert result == 1

    def test_counts_multiple_users(self, analytics_db_memory):
        analytics_db_memory.log_visit('juan@test.com', 'Juan', '/inventory')
        analytics_db_memory.log_visit('maria@test.com', 'María', '/dashboard')
        analytics_db_memory.log_visit('pedro@test.com', 'Pedro', '/inventory')
        result = analytics_db_memory.get_unique_users(days=30)
        assert result == 3

    def test_same_user_multiple_pages_counts_once(self, analytics_db_memory):
        analytics_db_memory.log_visit('juan@test.com', 'Juan', '/inventory')
        analytics_db_memory.log_visit('juan@test.com', 'Juan', '/dashboard')
        analytics_db_memory.log_visit('juan@test.com', 'Juan', '/analytics')
        result = analytics_db_memory.get_unique_users(days=30)
        assert result == 1


# ---------------------------------------------------------------------------
# get_visits_by_user
# ---------------------------------------------------------------------------

class TestGetVisitsByUser:
    def test_returns_empty_list_on_empty_db(self, analytics_db_memory):
        result = analytics_db_memory.get_visits_by_user()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_returns_user_with_correct_count(self, analytics_db_memory):
        analytics_db_memory.log_visit('juan@test.com', 'Juan', '/inventory')
        analytics_db_memory.log_visit('juan@test.com', 'Juan', '/dashboard')
        result = analytics_db_memory.get_visits_by_user()
        assert len(result) >= 1
        user_row = next((r for r in result if r['user_email'] == 'juan@test.com'), None)
        assert user_row is not None
        assert user_row['visit_count'] == 2


# ---------------------------------------------------------------------------
# get_visits_by_page
# ---------------------------------------------------------------------------

class TestGetVisitsByPage:
    def test_returns_empty_list_on_empty_db(self, analytics_db_memory):
        result = analytics_db_memory.get_visits_by_page()
        assert isinstance(result, list)

    def test_counts_page_visits_correctly(self, analytics_db_memory):
        analytics_db_memory.log_visit('a@test.com', 'A', '/inventory')
        analytics_db_memory.log_visit('b@test.com', 'B', '/inventory')
        analytics_db_memory.log_visit('c@test.com', 'C', '/dashboard')
        result = analytics_db_memory.get_visits_by_page()
        inv_row = next((r for r in result if r['page_url'] == '/inventory'), None)
        assert inv_row is not None
        assert inv_row['visit_count'] == 2
