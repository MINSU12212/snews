import json
import os
import sqlite3
from datetime import date
from contextlib import contextmanager

DB_PATH = 'news.db'
SEEN_LINKS_PATH = 'seen_links.json'


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
    """지금까지 한 번이라도 보낸 적 있는 모든 링크 (중복 방지용).
    news_items 테이블과 별개의 파일로 관리해서, 오래된 뉴스를 DB에서
    지워도(아카이브) 예전에 보낸 뉴스가 "새 소식"으로 재등장하지 않게 한다."""
    if not os.path.exists(SEEN_LINKS_PATH):
        return set()
    with open(SEEN_LINKS_PATH, 'r', encoding='utf-8') as f:
        return set(json.load(f))


def add_seen_links(links):
    existing = get_seen_links()
    existing.update(links)
    with open(SEEN_LINKS_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted(existing), f, ensure_ascii=False, indent=2)


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


def get_dates_older_than(cutoff_date):
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT DISTINCT collected_date FROM news_items WHERE collected_date < ? ORDER BY collected_date',
            (cutoff_date,)
        ).fetchall()
    return [row['collected_date'] for row in rows]


def delete_date(target_date):
    with get_conn() as conn:
        conn.execute('DELETE FROM news_items WHERE collected_date = ?', (target_date,))
