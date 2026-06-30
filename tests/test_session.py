from storage.session import db_connection


def test_db_connection_opens_and_closes(db_path):
    with db_connection(db_path) as connection:
        connection.execute("SELECT 1").fetchone()
