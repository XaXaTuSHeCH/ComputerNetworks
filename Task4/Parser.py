import json
import time

import mysql.connector
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


MYSQL_CONFIG = {
    "host": "localhost",
    "user": "localuser",
    "password": "",
    "database": "flats_db",
}


def save_to_mysql(data):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        for item in data:
            cursor.execute(
                "INSERT INTO flats (title, price, address, link) VALUES (%s, %s, %s, %s)",
                (item["title"], item["price"], item["address"], item["link"]),
            )
        conn.commit()
        print(f"Добавлено {len(data)} записей в базу данных.")
    except Exception as e:
        print(f"Ошибка при сохранении данных в MySQL: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def parse_flats(url):
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(url)

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
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-name='ContinueAuthBtn']")
            )
        )
        continue_button.click()
        time.sleep(1)

        passwd_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
        )
        passwd_input.send_keys(PASSWORD)

        enter_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-name='ContinueAuthBtn']")
            )
        )
        enter_button.click()
        time.sleep(1)

        search_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[@data-mark='FiltersSearchButton']")
            )
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

            flats = driver.find_elements(
                By.XPATH, "//article[@data-name='CardComponent']"
            )

            for flat in flats:
                try:
                    link = flat.find_element(By.XPATH, ".//a[@href]").get_attribute(
                        "href"
                    )
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

                    data.append(
                        {
                            "title": title,
                            "price": price,
                            "address": address,
                            "link": link,
                        }
                    )
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

        save_to_mysql(data)

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        parse_flats(sys.argv[1])
    else:
        print("URL не указан")
