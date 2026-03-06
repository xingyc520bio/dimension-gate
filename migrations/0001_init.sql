-- 维度之门 D1 数据库初始化
CREATE TABLE IF NOT EXISTS submissions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    company     TEXT    NOT NULL,
    phone       TEXT    NOT NULL,
    interests   TEXT,
    message     TEXT,
    created_at  TEXT    NOT NULL
);
