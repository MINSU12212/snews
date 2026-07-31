import re
import feedparser
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

RSS_FEEDS = [
    # What Hi-Fi?는 오디오뿐 아니라 TV/스마트폰/프로젝터 뉴스도 함께 다루므로
    # 카테고리 태그로 순수 음향기기 뉴스만 필터링한다.
    {'url': 'https://www.whathifi.com/feeds.xml', 'source': 'What Hi-Fi?', 'filter_audio_only': True},
    {'url': 'https://audio-head.com/feed/', 'source': 'AudioHead'},
    {'url': 'https://www.hifipig.com/feed/', 'source': 'HiFi Pig'},
]

# 음향기기로 인정할 RSS 카테고리 태그 (소문자 비교)
AUDIO_TAGS = {
    'hi-fi', 'headphones', 'speakers', 'wireless speakers', 'hi-fi speakers',
    'cd players', 'stereo amplifiers', 'stereo systems', 'wired headphones',
    'wireless earbuds', 'earbuds', 'soundbars', 'av receivers',
    'surround sound systems', 'turntables', 'music streamers', 'dacs',
    'cables', 'av accessories', 'av',
}

# 음향기기가 아닌 것으로 명확히 판단되는 태그 (하나라도 있으면 제외)
NON_AUDIO_TAGS = {
    'televisions', 'projectors', 'smartphones', 'smartphones & tablets',
    'blu-ray players', 'gaming', 'streaming & entertainment',
    'how to watch', 'tv streaming services', 'music streaming',
}


def is_audio_related(tags):
    """RSS 카테고리 태그를 보고 음향기기 관련 뉴스인지 판단"""
    if not tags:
        return True  # 태그 정보가 없으면 배제하지 않음
    terms = {t.lower() for t in tags}
    if terms & NON_AUDIO_TAGS:
        return False
    return bool(terms & AUDIO_TAGS)

CATEGORY_KEYWORDS = {
    '신제품': ['unveil', 'launch', 'release', 'new ', 'announce', 'introduc'],
    '행사/이벤트': ['show', 'fest', 'expo', 'event', 'exhibit'],
    '비교/리뷰': ['review', ' vs ', 'best', 'top 10', 'compare'],
    '업계소식/인터뷰': ['interview', 'talk', 'discuss'],
    '기술개발': [' ai ', 'technology', 'engineering', 'develop'],
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


def extract_image_from_entry(entry):
    if 'media_content' in entry and entry.media_content:
        url = entry.media_content[0].get('url')
        if url:
            return url
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get('url')
        if url:
            return url
    if 'enclosures' in entry and entry.enclosures:
        url = entry.enclosures[0].get('href')
        if url:
            return url
    return None


def extract_image_from_page(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        og = soup.find('meta', property='og:image')
        if og and og.get('content'):
            return og['content']
        tw = soup.find('meta', attrs={'name': 'twitter:image'})
        if tw and tw.get('content'):
            return tw['content']
    except Exception as e:
        print(f"  이미지 추출 실패 ({url}): {e}")
    return None


def categorize(title, summary=''):
    text = (title + ' ' + summary).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return '기타'


def clean_summary(raw_html, max_len=150):
    if not raw_html:
        return ''
    text = BeautifulSoup(raw_html, 'html.parser').get_text().strip()
    text = re.sub(r'\s+', ' ', text)
    return text[:max_len] + ('...' if len(text) > max_len else '')


def translate_to_korean(text):
    if not text:
        return text
    try:
        return GoogleTranslator(source='en', target='ko').translate(text)
    except Exception as e:
        print(f"  번역 실패: {e}")
        return text


def fetch_all_news(per_feed=None, fetch_missing_images=True, translate=True, exclude_links=None):
    exclude_links = exclude_links or set()
    all_items = []
    for feed_info in RSS_FEEDS:
        print(f"수집 중: {feed_info['source']}...")
        feed = feedparser.parse(feed_info['url'])

        entries = feed.entries
        if feed_info.get('filter_audio_only'):
            filtered = []
            skipped = 0
            for entry in entries:
                tags = [t.term for t in entry.get('tags', [])]
                if is_audio_related(tags):
                    filtered.append(entry)
                else:
                    skipped += 1
            if skipped:
                print(f"  음향기기 외 뉴스 {skipped}건 제외")
            entries = filtered

        # 이미 이전에 수집한 적 있는 링크(=예전 소식)는 제외하고 새 소식만 남긴다
        new_entries = [e for e in entries if e.get('link', '') not in exclude_links]
        already_seen = len(entries) - len(new_entries)
        if already_seen:
            print(f"  이미 보낸 소식 {already_seen}건 제외")
        entries = new_entries

        for entry in entries[:per_feed]:
            image = extract_image_from_entry(entry)
            link = entry.get('link', '')

            if not image and fetch_missing_images and link:
                image = extract_image_from_page(link)

            summary_en = clean_summary(entry.get('summary', ''))
            title_en = entry.get('title', 'No title')

            # 카테고리는 원문(영어) 기준으로 분류
            category = categorize(title_en, summary_en)

            title = translate_to_korean(title_en) if translate else title_en
            summary = translate_to_korean(summary_en) if translate else summary_en

            item = {
                'title': title,
                'title_en': title_en,
                'link': link,
                'summary': summary,
                'image_url': image,
                'source': feed_info['source'],
                'category': category,
                'published': entry.get('published', ''),
            }
            all_items.append(item)

    return all_items


if __name__ == '__main__':
    items = fetch_all_news()
    print(f"\n총 {len(items)}개 뉴스 수집 완료\n")
    for item in items:
        print(f"[{item['category']}] {item['title']} ({item['source']})")
        print(f"  이미지: {item['image_url']}")
