from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import time
import arsenic 
async def screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.set_window_position(0, 0)
    driver.set_window_size(600,1000)
    driver.get(url)
    print("start waiting...")
    time.sleep(2)
    print("taking screenshot")
    driver.save_screenshot("screenshot.png")
    with open("screenshot.png", 'rb') as f:
        b = f.read()
    print("finish")
    return b
    
async def async_screenshot(url):
    service = arsenic.services.Chromedriver()
    browser = arsenic.browsers.Chrome()
    browser.capabilities = {
        "goog:chromeOptions": {"args": ["--headless", "--disable-gpu"]}
    }
    #service = arsenic.services.Geckodriver()
    #browser = arsenic.browsers.Firefox()
    async with arsenic.get_session(service, browser) as session:
        await session.set_window_size(600,1000)
        await session.get(url)
        await asyncio.sleep(2)
        a=await session.get_screenshot()
        
    print("finish")
    return a
    