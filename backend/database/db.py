"""Local SQLite persistence with short-lived connections."""
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

DEFAULT_DB = Path(__file__).resolve().parents[1] / 'data' / 'employx.sqlite'


class ProfileRepository:
    def __init__(self, path=None):
        self.path = Path(path or os.getenv('EMPLOYX_DB_PATH', str(DEFAULT_DB)))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute('''CREATE TABLE IF NOT EXISTS cv_profiles (
                id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL)''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def decode(row):
        if row is None:
            return None
        return {**json.loads(row['payload']), 'id': row['id'],
                'created_at': row['created_at'], 'updated_at': row['updated_at']}

    def list(self):
        with self.connect() as connection:
            rows = connection.execute(
                'SELECT * FROM cv_profiles ORDER BY updated_at DESC, id').fetchall()
        return [self.decode(row) for row in rows]

    def get(self, profile_id):
        with self.connect() as connection:
            row = connection.execute('SELECT * FROM cv_profiles WHERE id = ?', (profile_id,)).fetchone()
        return self.decode(row)

    def save(self, payload, profile_id=None):
        now = datetime.now(timezone.utc).isoformat()
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        with self.connect() as connection:
            if profile_id is None:
                profile_id = str(uuid4())
                connection.execute('INSERT INTO cv_profiles VALUES (?, ?, ?, ?)',
                                   (profile_id, encoded, now, now))
            else:
                result = connection.execute(
                    'UPDATE cv_profiles SET payload = ?, updated_at = ? WHERE id = ?',
                    (encoded, now, profile_id))
                if result.rowcount == 0:
                    raise KeyError(profile_id)
        return self.get(profile_id)
