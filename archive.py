import json
import os
from datetime import date, timedelta

from database import get_dates_older_than, get_news_by_date, delete_date

RETENTION_DAYS = 30  # 웹사이트(캘린더)에 보여줄 최근 기간
ARCHIVE_DIR = 'archive'


def archive_old_news(retention_days=RETENTION_DAYS):
    """retention_days 보다 오래된 뉴스를 월별 JSON 파일(archive/YYYY-MM.json)로
    저장(git 저장소에 영구 보관)한 뒤, 실제 서비스 중인 DB에서는 삭제한다.
    -> 웹사이트 용량은 늘 최근 데이터만 유지하고, 과거 데이터는 저장소에 남는다."""
    cutoff = (date.today() - timedelta(days=retention_days)).isoformat()
    old_dates = get_dates_older_than(cutoff)

    if not old_dates:
        return []

    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    items_by_month = {}
    for target_date in old_dates:
        month_key = target_date[:7]  # YYYY-MM
        items_by_month.setdefault(month_key, []).extend(get_news_by_date(target_date))

    for month_key, items in items_by_month.items():
        archive_path = os.path.join(ARCHIVE_DIR, f'{month_key}.json')
        existing = []
        if os.path.exists(archive_path):
            with open(archive_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)

        existing_links = {item['link'] for item in existing}
        new_items = [item for item in items if item['link'] not in existing_links]
        existing.extend(new_items)
        existing.sort(key=lambda x: (x['collected_date'], x['category']))

        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    for target_date in old_dates:
        delete_date(target_date)

    return old_dates


if __name__ == '__main__':
    archived = archive_old_news()
    if archived:
        print(f"아카이브 완료: {len(archived)}개 날짜 ({archived[0]} ~ {archived[-1]})")
    else:
        print("아카이브할 오래된 뉴스가 없습니다.")
