import csv
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


try:
    with open("data.json", "r") as file:
        creds = json.load(file)
    EMAIL = creds["email"]
    PASSWORD = creds["password"]
except Exception as e:
    print(f"Ошибка при загрузке учетных данных: {e}")
    exit(1)

try:
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://novosibirsk.cian.ru")

    login_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-name='LoginButton']"))
    )
    login_button.click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]'))
    )

    auth_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-name='SwitchToEmailAuthBtn']")
        )
    )
    auth_button.click()

    email_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
    )
    email_input.send_keys(EMAIL)

    continue_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-name='ContinueAuthBtn']"))
    )
    continue_button.click()
    time.sleep(1)

    passwd_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
    )
    passwd_input.send_keys(PASSWORD)

    enter_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-name='ContinueAuthBtn']"))
    )
    enter_button.click()
    time.sleep(1)

    search_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-mark='FiltersSearchButton']"))
    )
    search_button.click()

    data = []

    for _ in range(5):
        time.sleep(3)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//article[@data-name='CardComponent']")
            )
        )

        flats = driver.find_elements(By.XPATH, "//article[@data-name='CardComponent']")

        for flat in flats:
            try:
                link = flat.find_element(By.XPATH, ".//a[@href]").get_attribute("href")
                title_elements = flat.find_elements(
                    By.XPATH, ".//span[@data-mark='OfferTitle']"
                )
                subtitle_elements = flat.find_elements(
                    By.XPATH, ".//span[@data-mark='OfferSubtitle']"
                )
                price_element = flat.find_element(
                    By.XPATH, ".//span[@data-mark='MainPrice']"
                )
                address_elements = flat.find_elements(
                    By.XPATH, ".//a[@data-name='GeoLabel']"
                )

                title = (
                    " ".join([elem.text for elem in title_elements])
                    + " "
                    + " ".join([elem.text for elem in subtitle_elements])
                )
                price = price_element.text
                address = ", ".join([elem.text for elem in address_elements])

                data.append([title, price, address, link])
            except Exception as e:
                print(f"Ошибка при обработке объявления: {e}")

        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Дальше']]"))
            )
            next_button.click()
        except Exception as e:
            print(f"Ошибка при переходе на следующую страницу: {e}")

    with open("flats.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="|")
        writer.writerow(["Название", "Цена", "Адрес", "Ссылка"])
        writer.writerows(data)

except Exception as e:
    print(f"Ошибка: {e}")
finally:
    driver.quit()
