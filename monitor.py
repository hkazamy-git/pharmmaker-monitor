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
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("페이지 이동 중...")
        await page.goto("https://www.pharmmaker.com/intro")
        await page.wait_for_timeout(5000)
        print("5초 대기 완료")

        # 페이지에서 input 전부 찾기
        inputs = await page.query_selector_all("input")
        print(f"input 개수: {len(inputs)}")
        for inp in inputs:
            name = await inp.get_attribute("name")
            id_ = await inp.get_attribute("id")
            type_ = await inp.get_attribute("type")
            print(f"input → name:{name}, id:{id_}, type:{type_}")

        await browser.close()

asyncio.run(main())
