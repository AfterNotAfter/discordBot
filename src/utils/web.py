from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
def screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.set_window_position(0, 0)
    driver.set_window_size(600,1000)
    driver.get(url)
    print("start waiting...")
    time.sleep(1)
    print("taking screenshot")
    driver.save_screenshot("screenshot.png")
    with open("screenshot.png", 'rb') as f:
        b = f.read()
    print("finish")
    return b
    
