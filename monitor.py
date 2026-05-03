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

        print("로그인 중...")
        await page.goto("https://www.pharmmaker.com/intro")
        await page.wait_for_timeout(5000)
        await page.fill("input[name='user_id']", PHARMMAKER_ID)
        await page.fill("input[name='password']", PHARMMAKER_PW)
        await page.click("input[type='submit']")
        await page.wait_for_timeout(5000)
        print("로그인 완료")

        print("게시판 이동 중...")
        await page.goto("https://www.pharmmaker.com/P_Trades")
        await page.wait_for_timeout(5000)

        # 팝업 닫기 시도
        try:
            close_btn = await page.query_selector(".modal-close, .popup-close, .close, [class*='close']")
            if close_btn:
                await close_btn.click()
                await page.wait_for_timeout(1000)
                print("팝업 닫기 완료")
        except:
            print("팝업 없음")

        # 글 목록 수집 — 약국매매 글만
        posts = []
        rows = await page.query_selector_all("table tbody tr")
        for row in rows:
            # 제목 셀 찾기
            title_el = await row.query_selector("td.title a, td.subject a, td[class*='title'] a, td[class*='subject'] a")
            if not title_el:
                # 일반 링크 중 카테고리 링크 제외
                links = await row.query_selector_all("t
