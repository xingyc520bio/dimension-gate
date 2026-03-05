"""
维度之门 - Vercel Serverless Function
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Vercel 只有 /tmp 可写，SQLite 数据在冷启动后会丢失
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


@app.route('/api/submit', methods=['POST'])
def submit():
    init_db()
    data = request.get_json(silent=True) or {}

    name = (data.get('name') or '').strip()
    company = (data.get('company') or '').strip()
    phone = (data.get('phone') or '').strip()
    interests = data.get('interests', [])
    message = (data.get('message') or '').strip()

    if not name:
        return jsonify({'ok': False, 'error': '姓名不能为空'}), 400
    if not company:
        return jsonify({'ok': False, 'error': '公司名称不能为空'}), 400
    if not phone:
        return jsonify({'ok': False, 'error': '联系电话不能为空'}), 400

    phone_clean = re.sub(r'[\s\-]', '', phone)
    if not re.match(r'^(\+?86)?1[3-9]\d{9}$|^\+?[0-9]{8,15}$', phone_clean):
        return jsonify({'ok': False, 'error': '请输入有效的手机号码'}), 400

    if len(message) > 200:
        return jsonify({'ok': False, 'error': '留言不能超过200字'}), 400

    interests_str = ','.join(interests) if isinstance(interests, list) else str(interests)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

    return jsonify({'ok': True, 'id': row_id, 'message': '提交成功，我们将在24小时内联系您！'})


@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    init_db()
    token = request.args.get('token', '')
    if token != os.environ.get('ADMIN_TOKEN', 'dimensiongate2025'):
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401

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
    return jsonify({'ok': True, 'total': len(result), 'data': result})
