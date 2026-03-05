"""维度之门 - 查看提交记录 API"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sqlite3
import os

DB_PATH = '/tmp/submissions.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            company     TEXT    NOT NULL,
            phone       TEXT    NOT NULL,
            interests   TEXT,
            message     TEXT,
            created_at  TEXT    NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        token = query.get('token', [''])[0]
        admin_token = os.environ.get('ADMIN_TOKEN', 'dimensiongate2025')

        if token != admin_token:
            return self._json(401, {'ok': False, 'error': 'Unauthorized'})

        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, name, company, phone, interests, message, created_at FROM submissions ORDER BY id DESC')
        rows = c.fetchall()
        conn.close()

        result = [
            {
                'id': r[0], 'name': r[1], 'company': r[2],
                'phone': r[3], 'interests': r[4], 'message': r[5], 'created_at': r[6]
            }
            for r in rows
        ]
        return self._json(200, {'ok': True, 'total': len(result), 'data': result})

    def _json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
