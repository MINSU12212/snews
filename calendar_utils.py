import calendar as cal_module
from collections import defaultdict

WEEKDAY_LABELS = ['일', '월', '화', '수', '목', '금', '토']


def build_calendar_blocks(available_dates):
    """available_dates: ['YYYY-MM-DD', ...] (뉴스가 있는 날짜들)
    최근 달이 먼저 오도록, 월별 캘린더 그리드 데이터를 만든다."""
    dates_by_month = defaultdict(set)
    for d in available_dates:
        year, month, day = d.split('-')
        dates_by_month[(int(year), int(month))].add(int(day))

    months = sorted(dates_by_month.keys(), reverse=True)

    c = cal_module.Calendar(firstweekday=6)  # 일요일부터 시작
    blocks = []
    for year, month in months:
        days_with_news = dates_by_month[(year, month)]
        weeks = []
        for week in c.monthdayscalendar(year, month):
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append(None)
                else:
                    week_data.append({
                        'day': day,
                        'date_str': f"{year:04d}-{month:02d}-{day:02d}",
                        'has_news': day in days_with_news,
                    })
            weeks.append(week_data)

        blocks.append({
            'label': f"{year}년 {month}월",
            'weekday_labels': WEEKDAY_LABELS,
            'weeks': weeks,
        })

    return blocks
