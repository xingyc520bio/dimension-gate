"""维度之门 - 提交表单 API"""

from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import os
import re
from datetime import datetime

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
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        name = (data.get('name') or '').strip()
        company = (data.get('company') or '').strip()
        phone = (data.get('phone') or '').strip()
        interests = data.get('interests', [])
        message = (data.get('message') or '').strip()

        # 校验
        if not name:
            return self._json(400, {'ok': False, 'error': '姓名不能为空'})
        if not company:
            return self._json(400, {'ok': False, 'error': '公司名称不能为空'})
        if not phone:
            return self._json(400, {'ok': False, 'error': '联系电话不能为空'})

        phone_clean = re.sub(r'[\s\-]', '', phone)
        if not re.match(r'^(\+?86)?1[3-9]\d{9}$|^\+?[0-9]{8,15}$', phone_clean):
            return self._json(400, {'ok': False, 'error': '请输入有效的手机号码'})

        if len(message) > 200:
            return self._json(400, {'ok': False, 'error': '留言不能超过200字'})

        interests_str = ','.join(interests) if isinstance(interests, list) else str(interests)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        init_db()
        conn = sqlite3.connect(DB_PATH)
        try:
            c = conn.cursor()
            c.execute(
                'INSERT INTO submissions (name, company, phone, interests, message, created_at) VALUES (?,?,?,?,?,?)',
                (name, company, phone, interests_str, message, created_at)
            )
            conn.commit()
            row_id = c.lastrowid
        finally:
            conn.close()

        return self._json(200, {'ok': True, 'id': row_id, 'message': '提交成功，我们将在24小时内联系您！'})

    def _json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self._json(200, {})
