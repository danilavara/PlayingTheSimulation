from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json
from dateutil import parser
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

def format_title_with_dates():
    today = datetime.today()
    seven_days_ago = today - timedelta(days=7)

    # Format dates
    today_str = today.strftime('%d')
    seven_days_ago_str = seven_days_ago.strftime('%d')
    
    # English to Spanish month mapping
    month_mapping = {
        'January': 'enero',
        'February': 'febrero',
        'March': 'marzo',
        'April': 'abril',
        'May': 'mayo',
        'June': 'junio',
        'July': 'julio',
        'August': 'agosto',
        'September': 'septiembre',
        'October': 'octubre',
        'November': 'noviembre',
        'December': 'diciembre'
    }
    
    # Get the month name in English and map to Spanish
    month_english = today.strftime('%B')
    month_spanish = month_mapping[month_english]

    # Create title string
    title = f'Mejores post semana del {seven_days_ago_str} al {today_str} de {month_spanish}'
    return title

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def format_post(post, index):
    created_date = parser.isoparse(post['created']).strftime('%d-%m-%Y')
    formatted_post = (
        f"<div><b>📝 Post {index + 1}</b></div>"
        f"<div>👤 {post['nombre']} {post['apellido']}</div>"
        f"<div>🔗 <a href='{post['url']}' target='_blank'>{post['titulo']}</a></div>"
        f"<div>👍 {post['likes']}</div>"
        f"<div>📅 {created_date}</div>"
        f"<div>🏷️ {post['categoria']}</div>"
        f"<br>"
    )
    return formatted_post

def main():
        
        # Load environment variables from .env file
        load_dotenv()

        # Get email and password from environment variables
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')

         # Load JSON data
        posts = load_json('top_posts.json')

        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")
        #if not headed:
          #  chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        service = Service(executable_path="./chromedriver.exe")
        service.start()
        driver = webdriver.Remote(service.service_url, options=chrome_options)

        driver.maximize_window()
        driver.get("https://www.skool.com/login")

        # Enter login credentials and submit form
        driver.find_element_by_id('email').send_keys(email)
        driver.find_element_by_id('password').send_keys(password)
        driver.find_element_by_xpath('//*[@id="__next"]/div/div/form/button').click()  # Adjust the element finder as per the actual login button
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@title="Playing the Simulation"]')))  # Adjust the ID to a post-login element
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[starts-with(@class, "styled__CardContent-sc")]'))
        ).click()

        dropdown_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[starts-with(@class, "styled__CategoryLabel-sc")]'))
        )
        
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_button)
        time.sleep(1)  # Sleep for a short period to ensure the scroll is complete

        driver.execute_script("arguments[0].click();", dropdown_button)

        # Click on the dropdown item
        dropdown_item = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[starts-with(@data-testid, "dropdown-item-1")]'))
        )
        driver.execute_script("arguments[0].click();", dropdown_item)

        # Wait for the title input field
        title_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Title"]'))
        )

         # Set the entire title including the emoji using JavaScript
        title = format_title_with_dates()
        full_title = f"🚨 {title}"
        driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", title_input, full_title)

        # Manually trigger input and change events
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {'bubbles': true}));", title_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', {'bubbles': true}));", title_input)


        # Navigate to the desired page and wait for the contenteditable element
        content_editable = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@contenteditable="true" and starts-with(@class, "ProseMirror skool-editor")]'))
        )

        # Format and set each post into the contenteditable element
        for index, post in enumerate(posts):
            formatted_post = format_post(post, index)
            driver.execute_script(
                "arguments[0].innerHTML += arguments[1];", content_editable, formatted_post
            )

        # Optionally trigger an input event if necessary
        driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", content_editable)

        submitButton = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@class, "SubmitButtonWrapper-sc")]'))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", submitButton)
        time.sleep(5)  # Sleep for a short period to ensure the scroll is complete

        driver.execute_script("arguments[0].click();", submitButton) 
        
        time.sleep(15)

if __name__ == "__main__":
    main()