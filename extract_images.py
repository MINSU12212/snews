import requests
from bs4 import BeautifulSoup
import json
import time

# 뉴스 링크 목록 (AudioHead + HiFi Pig)
news_urls = [
    # AudioHead
    {
        "title": "Top 10 Best Party Speakers",
        "url": "https://audio-head.com/top-10-best-party-speakers/",
        "source": "AudioHead"
    },
    {
        "title": "An Interview With Benchmark Media Systems",
        "url": "https://audio-head.com/an-interview-with-benchmark-media-systems/",
        "source": "AudioHead"
    },
    {
        "title": "Sony's Latest IEM Focuses On Noise Isolation",
        "url": "https://audio-head.com/sonys-latest-iem-focuses-on-noise-isolation/",
        "source": "AudioHead"
    },
    {
        "title": "Top 10 Best Speakers For 2026",
        "url": "https://audio-head.com/top-10-best-speakers-2026/",
        "source": "AudioHead"
    },
    {
        "title": "HIGH END Vienna 2026",
        "url": "https://audio-head.com/high-end-vienna-2026-hifi-highlights-and-best-of-show/",
        "source": "AudioHead"
    },
    {
        "title": "AudioQuest Dragonfly Copper",
        "url": "https://audio-head.com/audioquest-unveils-the-dragonfly-copper/",
        "source": "AudioHead"
    },
    {
        "title": "Dan Clark Audio's AEON CORE",
        "url": "https://audio-head.com/dan-clark-audios-newest-aeon-core/",
        "source": "AudioHead"
    },
    {
        "title": "An Interview With Julie Mullins",
        "url": "https://audio-head.com/an-interview-with-julie-mullins/",
        "source": "AudioHead"
    },
    {
        "title": "Schiit Vestri",
        "url": "https://audio-head.com/schiit-audio-makes-a-dongle-now-schiit-vestri/",
        "source": "AudioHead"
    },
    {
        "title": "What is Realism in HiFi",
        "url": "https://audio-head.com/what-is-realism-in-hifi-bill-low/",
        "source": "AudioHead"
    },
    # HiFi Pig
    {
        "title": "Constellation & Wilson Audio at Hong Kong Show",
        "url": "https://www.hifipig.com/constellation-statement-with-wilson-audio-autobiography-at-hong-kong-high-end-av-show-2026/",
        "source": "HiFi Pig"
    },
    {
        "title": "In-Akustik Micro AIR Reference Cable Series",
        "url": "https://www.hifipig.com/in-akustik-micro-air-reference-cable-series-expanded/",
        "source": "HiFi Pig"
    },
    {
        "title": "Audio Group Denmark Borresen M8",
        "url": "https://www.hifipig.com/audio-group-denmark-borresen-m8-and-aavik-m880-at-hong-kong-high-end-av-show-2026/",
        "source": "HiFi Pig"
    },
    {
        "title": "Acoustic Signature Thirty Neo",
        "url": "https://www.hifipig.com/acoustic-signature-thirty-neo-and-merlin-neo-at-hong-kong-high-end-av-show-2026/",
        "source": "HiFi Pig"
    },
    {
        "title": "The HiFi PiG Selection Box",
        "url": "https://www.hifipig.com/the-hifi-pig-selection-box-july-2026/",
        "source": "HiFi Pig"
    }
]

def extract_image_url(url):
    """페이지에서 대표 이미지 URL 추출"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Open Graph 이미지 찾기
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']

        # 2. Twitter 이미지 찾기
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']

        # 3. 페이지 내 첫 번째 이미지 찾기 (lazy-loading 제외)
        images = soup.find_all('img')
        for img in images:
            img_src = img.get('src') or img.get('data-src')
            if img_src and 'logo' not in img_src.lower() and 'icon' not in img_src.lower():
                # 상대 URL을 절대 URL로 변환
                if not img_src.startswith('http'):
                    from urllib.parse import urljoin
                    img_src = urljoin(url, img_src)
                return img_src

        return None

    except Exception as e:
        print(f"❌ 오류 ({url}): {str(e)}")
        return None

# 이미지 추출 시작
print("🔍 뉴스 페이지에서 이미지 URL 추출 중...\n")

results = []
for i, news in enumerate(news_urls, 1):
    print(f"[{i}/{len(news_urls)}] {news['title']} ({news['source']})")
    image_url = extract_image_url(news['url'])

    if image_url:
        print(f"    ✅ 이미지 찾음: {image_url[:80]}...")
    else:
        print(f"    ⚠️  이미지를 찾을 수 없습니다")

    results.append({
        "title": news['title'],
        "url": news['url'],
        "source": news['source'],
        "image_url": image_url
    })

    time.sleep(1)  # 서버 부하 방지

# 결과를 JSON 파일로 저장
with open('D:\\USER\\Documents\\snews\\news_images.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n✅ 완료! 결과가 news_images.json에 저장되었습니다.")

# 요약 출력
found = sum(1 for r in results if r['image_url'])
print(f"\n📊 요약: {found}/{len(results)} 뉴스에서 이미지 추출 성공")
