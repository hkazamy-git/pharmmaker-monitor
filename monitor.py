import asyncio
from playwright.async_api import async_playwright
import os
import json
import hashlib
import requests
import base64

PHARMMAKER_ID = os.environ["PHARMMAKER_ID"]
PHARMMAKER_PW = os.environ["PHARMMAKER_PW"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
STATE_FILE = "last_state.json"

async def get_posts():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("페이지 이동 중...")
        await page.goto("https://www.pharmmaker.com/intro")
        await page.wait_for_timeout(5000)  # 5초 대기

        # 스크린샷 찍기
        await page.screenshot(path="screenshot.png")
        print("스크린샷 저장완료")

        # 페이지 HTML 출력
        html = await page.content()
        print("HTML 일부:", html[:2000])

        # input 찾기 시도
        inputs = await page.query_selector_all("input")
        print(f"input 개수: {len(inputs)}")
        for inp in inputs:
            name = await inp.get_attribute("name")
            id_ = await inp.get_attribute("id")
            type_ = await inp.get_attribute("type")
            print(f"input - name:{name}, id:{id_}, type:{type_}")

        await browser.close()
        return []

async def main():
    await get_posts()

asyncio.run(main())
