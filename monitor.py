import asyncio
from playwright.async_api import async_playwright
import os
import json
import hashlib
import requests

PHARMMAKER_ID = os.environ["PHARMMAKER_ID"]
PHARMMAKER_PW = os.environ["PHARMMAKER_PW"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
STATE_FILE = "last_state.json"

async def get_posts():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="ko-KR",
        )
        page = await context.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
        """)

        print("로그인 페이지 이동 중...")
        await page.goto("https://www.pharmmaker.com/intro")
        await page.wait_for_timeout(5000)

        print("로그인 시도 중...")
        await page.fill("input[name='user_id']", PHARMMAKER_ID)
        await page.fill("input[name='password']", PHARMMAKER_PW)
        await page.click("input[type='submit']")
        await page.wait_for_timeout(5000)
        print("로그인 완료")

        print("약국매매 게시판 이동 중...")
        await page.goto("https://www.pharmmaker.com/P_Trades")
        await page.wait_for_timeout(5000)

        # 스크린샷 텔레그램 전송 (확인용)
        await page.screenshot(path="screen.png")
        with open("screen.png", "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID},
                files={"photo": f}
            )
        print("게시판 스크린샷 전송 완료!")

        # 글 목록 수집
        posts = []
        rows = await page.query_selector_all("table tr")
        for row in rows:
            link_el = await row.query_selector("td a")
            if link_el:
                title = await link_el.inner_text()
                href = await link_el.get_attribute("href")
                if href and title.strip():
                    if href.startswith("/"):
                        href = "https://www.pharmmaker.com" + href
                    posts.append({"title": title.strip(), "link": href})

        print(f"글 수집 완료: {len(posts)}개")
        await browser.close()
        return posts

def get_hash(posts):
    return hashlib.md5(json.dumps(posts, ensure_ascii=False).encode()).hexdigest()

def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    )

async def main():
    posts = await get_posts()
    current_hash = get_hash(posts)

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            data = json.load(f)
        last_hash = data.get("hash", "")
        last_posts = data.get("posts", [])
    else:
        last_hash = ""
        last_posts = []

    if current_hash != last_hash:
        new_posts = [p for p in posts if p not in last_posts]
        if new_posts:
            msg = "🏥 <b>pharmmaker 약국매매 새 글 알림!</b>\n\n"
            for p in new_posts:
                msg += f"📌 {p['title']}\n🔗 {p['link']}\n\n"
            send_telegram(msg)
            print("알림 전송 완료!")
        else:
            print("변경 감지됐지만 새 글 없음")
    else:
        print("변경 없음")

    with open(STATE_FILE, "w") as f:
        json.dump({"hash": current_hash, "posts": posts}, f, ensure_ascii=False)

asyncio.run(main())
