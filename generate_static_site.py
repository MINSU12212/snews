import os
import shutil
from collections import defaultdict

from flask import Flask, render_template

from database import init_db, get_news_by_date, get_available_dates
from calendar_utils import build_calendar_blocks

CATEGORY_ORDER = ['신제품', '기술개발', '행사/이벤트', '비교/리뷰', '업계소식/인터뷰', '기타']
CATEGORY_EMOJI = {
    '신제품': '🆕',
    '기술개발': '⚙️',
    '행사/이벤트': '🎪',
    '비교/리뷰': '🔍',
    '업계소식/인터뷰': '🎤',
    '기타': '📰',
}

OUTPUT_DIR = 'docs_build'


def group_by_category(items):
    grouped = defaultdict(list)
    for item in items:
        grouped[item['category']].append(item)
    return [
        (cat, CATEGORY_EMOJI.get(cat, '📰'), grouped[cat])
        for cat in CATEGORY_ORDER if grouped.get(cat)
    ]


def generate():
    init_db()

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    available_dates = get_available_dates()
    calendar_blocks = build_calendar_blocks(available_dates)
    latest = available_dates[0] if available_dates else None

    app = Flask(__name__)

    with app.app_context():
        # 홈페이지: 최신 날짜 소식 + 캘린더
        latest_items = get_news_by_date(latest) if latest else []
        homepage_html = render_template(
            'news_page.html',
            categories=group_by_category(latest_items),
            current_date=latest,
            calendar_blocks=calendar_blocks,
            back_link=None,
        )
        with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(homepage_html)

        # 날짜별 서브페이지 (달력에서 클릭해서 들어가는 과거 뉴스)
        for target_date in available_dates:
            items = get_news_by_date(target_date)
            page_html = render_template(
                'news_page.html',
                categories=group_by_category(items),
                current_date=target_date,
                calendar_blocks=None,
                back_link='../',
            )
            date_dir = os.path.join(OUTPUT_DIR, target_date)
            os.makedirs(date_dir, exist_ok=True)
            with open(os.path.join(date_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(page_html)

    print(f"정적 사이트 생성 완료: 홈페이지 + 날짜별 페이지 {len(available_dates)}개")


if __name__ == '__main__':
    generate()
