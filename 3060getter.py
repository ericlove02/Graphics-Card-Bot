import bs4
import sys
import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# Twilio config
toNumber = '2106431140'  # receive number
fromNumber = '6147339949'  # twilio account number
accountSid = 'AC6adc67b53b0db7357c2791b3067b5c0c'
authToken = '5c759cc18e5db6df2db08c9bf1cca117'
client = Client(accountSid, authToken)

# Product Page
url = 'https://www.bestbuy.com/site/nvidia-geforce-rtx-3060-ti-8gb-gddr6-pci-express-4-0-graphics-card-steel-and-black/6439402.p?skuId=6439402&irclickid=TWX3AwWhHxyLWbW0TWXZ0S3wUkB0LuT%3ANVPqWU0&irgwc=1&ref=198&loc=Troposphere%20LLC&acampID=0&mpid=62662'


def timeSleep(x, driver):
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('{:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    driver.refresh()
    sys.stdout.write('\r')
    sys.stdout.write('Page refreshed\t')
    print('Item still sold out.\n')
    sys.stdout.flush()


def createDriver():
    """Creating driver."""
    options = Options()
    options.headless = False  # Change To False if you want to see Firefox Browser
    profile = webdriver.FirefoxProfile(
        r'C:\Users\ericl\AppData\Roaming\Mozilla\Firefox\Profiles\zx0pffrh.default-release')  # change to ur firefox info, go to about:profiles to get ur info
    driver = webdriver.Firefox(profile, options=options, executable_path=GeckoDriverManager().install())
    return driver


def driverWait(driver, findType, selector):
    """Driver Wait Settings."""
    while True:
        if findType == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                print('found css element')
                break
            except NoSuchElementException:
                print('did not find css element')
                driver.implicitly_wait(0.2)
        elif findType == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.2)


def findingCards(driver):
    """Scanning all cards."""
    driver.get(url)
    while True:
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
        wait = WebDriverWait(driver, 15)
        wait2 = WebDriverWait(driver, 2)
        try:
            findAllCards = soup.find('button',
                                     {'class': 'btn btn-primary btn-lg btn-block btn-leading-ficon add-to-cart-button'})
            if findAllCards:
                print(f'Button Found!: {findAllCards.get_text()}')

                # click add to cart button
                driverWait(driver, 'css', '.add-to-cart-button')

                # open cart
                driver.get('https://www.bestbuy.com/cart')

                # check for item ion cart
                try:
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary']")))
                    driver.find_element_by_xpath("//*[@class='btn btn-lg btn-block btn-primary']").click()
                    print("Item Is Still In Cart.")
                except (NoSuchElementException, TimeoutException):
                    print("Item is not in cart anymore. Retrying..")
                    timeSleep(2, driver)
                    findingCards(driver)
                    return

                # sign in to account
                print("Attempting to Login.")

                # goto shipping options
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#fulfillment_1losStandard0")))
                    time.sleep(1)
                    driverWait(driver, 'css', '#fulfillment_1losStandard0')
                    print("Clicking Shipping Option.")
                except (NoSuchElementException, TimeoutException):
                    pass

                # item in cart
                print('ITEM IN CART')
                try:
                    client.messages.create(to=toNumber, from_=fromNumber, body='3060 in your cart') # send twilio
                except (NameError, TwilioRestException):
                    pass
                for i in range(3):
                    time.sleep(1)
                time.sleep(1800)
                driver.quit()
                return
            else:
                pass

        except (NoSuchElementException, TimeoutException):
            pass
        timeSleep(1, driver)


if __name__ == '__main__':
    driver = createDriver()
    findingCards(driver)
