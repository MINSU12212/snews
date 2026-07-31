from collections import defaultdict

from flask import Flask, render_template, redirect, url_for, abort

from database import init_db, get_news_by_date, get_available_dates, get_latest_date

app = Flask(__name__)
init_db()

CATEGORY_ORDER = ['신제품', '기술개발', '행사/이벤트', '비교/리뷰', '업계소식/인터뷰', '기타']
CATEGORY_EMOJI = {
    '신제품': '🆕',
    '기술개발': '⚙️',
    '행사/이벤트': '🎪',
    '비교/리뷰': '🔍',
    '업계소식/인터뷰': '🎤',
    '기타': '📰',
}


@app.route('/')
def index():
    latest = get_latest_date()
    if not latest:
        return render_template('empty.html')
    return redirect(url_for('news_by_date', date_str=latest))


@app.route('/date/<date_str>')
def news_by_date(date_str):
    items = get_news_by_date(date_str)
    if not items:
        abort(404)

    grouped = defaultdict(list)
    for item in items:
        grouped[item['category']].append(item)

    ordered_categories = [
        (cat, CATEGORY_EMOJI.get(cat, '📰'), grouped[cat])
        for cat in CATEGORY_ORDER if grouped.get(cat)
    ]

    all_dates = get_available_dates()

    return render_template(
        'index.html',
        categories=ordered_categories,
        current_date=date_str,
        all_dates=all_dates,
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
