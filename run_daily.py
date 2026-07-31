from collections import defaultdict

from flask import render_template

from app import app, CATEGORY_ORDER, CATEGORY_EMOJI
from database import init_db, save_news_items, get_seen_links
from fetch_news import fetch_all_news
from send_email import send_news_email

SITE_URL = 'http://localhost:5000'  # 배포 후 실제 웹사이트 주소로 교체 예정


def run():
    init_db()

    print("=" * 50)
    print("음향기기 뉴스 자동 수집 시작")
    print("=" * 50)

    seen_links = get_seen_links()
    items = fetch_all_news(exclude_links=seen_links)
    print(f"\n새로운 뉴스 {len(items)}개 발견")

    if not items:
        print("새로운 소식이 없어 오늘은 이메일을 보내지 않습니다.")
        print("=" * 50)
        return

    collected_date = save_news_items(items)
    print(f"DB 저장 완료: {collected_date}")

    grouped = defaultdict(list)
    for item in items:
        grouped[item['category']].append(item)

    categories = [
        (cat, CATEGORY_EMOJI.get(cat, '📰'), grouped[cat])
        for cat in CATEGORY_ORDER if grouped.get(cat)
    ]

    with app.app_context():
        html_content = render_template(
            'email.html',
            categories=categories,
            current_date=collected_date,
            site_url=SITE_URL,
        )

    send_news_email(html_content)

    print("=" * 50)
    print("완료!")
    print("=" * 50)


if __name__ == '__main__':
    run()
