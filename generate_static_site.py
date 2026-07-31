import os
from collections import defaultdict

from flask import Flask, render_template

from database import init_db, get_news_by_date, get_latest_date

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


def generate():
    init_db()
    latest = get_latest_date()

    app = Flask(__name__)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with app.app_context():
        if not latest:
            html = render_template('empty.html')
        else:
            items = get_news_by_date(latest)
            grouped = defaultdict(list)
            for item in items:
                grouped[item['category']].append(item)

            categories = [
                (cat, CATEGORY_EMOJI.get(cat, '📰'), grouped[cat])
                for cat in CATEGORY_ORDER if grouped.get(cat)
            ]

            html = render_template(
                'static_index.html',
                categories=categories,
                current_date=latest,
            )

    output_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"정적 사이트 생성 완료: {output_path}")


if __name__ == '__main__':
    generate()
