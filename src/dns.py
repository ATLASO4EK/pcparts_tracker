import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display
from fake_useragent import UserAgent

display = Display(visible=0, size=(1920, 1080))
display.start()
options = webdriver.ChromeOptions()
ua = UserAgent()
user_agent = ua.chrome
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f"user-agent={user_agent}")
options.add_argument("--headless")  # Тот самый headless режим. Можно использовать "--headless=new"
options.add_argument("--disable-gpu")  # Отключаем GPU для стабильности
options.add_argument("--no-sandbox")  # Нужно для Linux
options.add_argument("--window-size=1920,1080")  # Размер окна
options.add_argument('--allow-running-insecure-content')

driver = webdriver.Chrome(options=options)

driver.set_window_position(-2000,0)
products = []
prices = []
final = []
num = 1
def urlsite():
    for num in range(6):
        if num == 0:
            continue
        url = f'https://www.dns-shop.ru/catalog/17a8950d16404e77/klaviatury/?p={num}'
        driver.get(url)
        time.sleep(3)
        parsingsite()
        time.sleep(3)
        print(f'Parsed page {num}')
    #print(products)
    #print(prices)
    for i in range(len(products)):
        print(products[i] + prices[i])
    driver.quit()


def parsingsite():
    content = driver.page_source
    soup = BeautifulSoup(content, features='lxml')
    for item in soup.findAll('div', attrs={'class': 'products-list__content'}):
        # print(item)
        image2 = item.find_all('a', class_='catalog-product__name ui-link ui-link_black')
        # print(image2)
        for jj in image2:
            # print(str(jj))
            ag = jj.find("span")
            # print(ag)
            products.append(ag.text)
        czena = item.find_all('div', class_='product-buy__price')
        # print(czena)
        for i in czena:
            prices.append(str(i.text))
urlsite()
print(0)
print(0)