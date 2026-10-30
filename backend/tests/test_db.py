from app.db import get_database_url


def test_database_url_is_normalized_for_psycopg(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:pass@example.supabase.co:6543/postgres?pgbouncer=true&connection_limit=1&sslmode=no-verify",
    )

    url = get_database_url()

    assert "pgbouncer" not in url
    assert "connection_limit" not in url
    assert "sslmode=require" in url
