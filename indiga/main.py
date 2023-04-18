from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import requests
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
import time
from bs4 import BeautifulSoup
from langdetect import detect

app = FastAPI()
error_list = []

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"browser": "ALL"}

@app.get("/")
async def root():
    return "Hello World"

@app.post("/check_url")
async def check_url(url: str):
    def check_image_size():
        # Sayfadaki tüm resimleri buluyoruz
        image_elements = driver.find_elements(By.TAG_NAME, "img")

        if image_elements.count == 0:
            return

        # Her bir resmin boyutunu kontrol ediyoruz
        for img_element in image_elements:
            image_url = img_element.get_attribute("src")
            response = requests.get(image_url)
            if response.status_code == 200:
                # Resmi belleğe alıyoruz
                image_bytes = BytesIO(response.content)
                image = Image.open(image_bytes)

                # Resim boyutunu kontrol ediyoruz
                if len(image.fp.read()) < 10240:  # Resim boyutu 10 KB'dan küçükse
                    error_list.append("Images not high resolution")
                    break
    
    def check_javascript():
        js_log = driver.get_log("browser")
        for log in js_log:
            if log["level"] == "SEVERE":
                error_list.append("Javascript error")
                break

    def check_language():
        soup = BeautifulSoup(driver.page_source, "html.parser")
        if detect(soup.get_text()) != "hi":
            error_list.append("Language is not Hindi")
            

    driver = webdriver.Chrome(desired_capabilities=capabilities) 

    # Kullanıcının girdiği URL'ye gidip sayfayı açıyoruz
    driver.get(url)

    driver.implicitly_wait(5)
    time.sleep(5)
    
    check_image_size()

    check_javascript()

    check_language()

    driver.implicitly_wait(3)
    time.sleep(3)

    # Tarayıcıyı kapatıyoruz
    driver.quit()

    if error_list:
        return {"status": "error", "message": ', '.join(error_list)}
    else:
        return {"status": "success", "message": "No error found"}