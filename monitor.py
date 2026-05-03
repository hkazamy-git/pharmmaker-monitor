import asyncio
from playwright.async_api import async_playwright
import os
import requests

PHARMMAKER_ID = os.environ["PHARMMAKER_ID"]
PHARMMAKER_PW = os.environ["PHARMMAKER_PW"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

async def main():
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

        # 봇 감지 우회
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
        """)

        print("페이지 이동 중...")
        await page.goto("https://www.pharmmaker.com/intro")
        await page.wait_for_timeout(8000)
        print("8초 대기 완료")

        # 스크린샷 찍어서 텔레그램으로 전송
        await page.screenshot(path="screen.png")
        with open("screen.png", "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID},
                files={"photo": f}
            )
        print("스크린샷 텔레그램 전송 완료!")
        await browser.close()

asyncio.run(main())
