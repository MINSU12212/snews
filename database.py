import sqlite3
from datetime import date
from contextlib import contextmanager

DB_PATH = 'news.db'


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS news_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collected_date TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                summary TEXT,
                image_url TEXT,
                source TEXT,
                category TEXT,
                published TEXT,
                UNIQUE(collected_date, link)
            )
        ''')


def save_news_items(items, collected_date=None):
    collected_date = collected_date or date.today().isoformat()
    with get_conn() as conn:
        for item in items:
            conn.execute('''
                INSERT OR IGNORE INTO news_items
                (collected_date, title, link, summary, image_url, source, category, published)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                collected_date, item['title'], item['link'], item['summary'],
                item['image_url'], item['source'], item['category'], item['published']
            ))
    return collected_date


def get_seen_links():
    """지금까지 한 번이라도 수집된 적 있는 모든 링크 (중복 방지용)"""
    with get_conn() as conn:
        rows = conn.execute('SELECT DISTINCT link FROM news_items').fetchall()
    return {row['link'] for row in rows}


def get_news_by_date(target_date):
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT * FROM news_items WHERE collected_date = ? ORDER BY category, id',
            (target_date,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_available_dates():
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT DISTINCT collected_date FROM news_items ORDER BY collected_date DESC'
        ).fetchall()
    return [row['collected_date'] for row in rows]


def get_latest_date():
    dates = get_available_dates()
    return dates[0] if dates else None
