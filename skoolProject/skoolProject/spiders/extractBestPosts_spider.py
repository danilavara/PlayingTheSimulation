from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
import json
from dotenv import load_dotenv
import os

class LoginSpider(scrapy.Spider):
    name = 'login'
    start_urls = ['https://www.skool.com/login']  # Adjust to the real URL

    custom_settings = {
        'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
    }

    download_delay = 1

    def start_requests(self):

        # Load environment variables from .env file
        load_dotenv()

        # Get email and password from environment variables
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')
        
        # Setup Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.skool.com/login")

        # Enter login credentials and submit form
        driver.find_element_by_id('email').send_keys(email)
        driver.find_element_by_id('password').send_keys(password)
        driver.find_element_by_xpath('//*[@id="__next"]/div/div/form/button').click()  # Adjust the element finder as per the actual login button
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@title="Playing the Simulation"]')))  # Adjust the ID to a post-login element

        # Wait for the login to complete (can be adjusted)
        driver.implicitly_wait(10)

        # Collect cookies and pass them to Scrapy
        cookies = driver.get_cookies()
        driver.quit()

        # Scrapy starts here
        return [scrapy.Request(url="https://www.skool.com/playing-the-simulation-7538", cookies=cookies, callback=self.after_login)]

    def after_login(self, response):
        # Check if login was successful
        if "authentication failed" in response.text:
            self.logger.error("Login failed")
        else:
            self.logger.info("Login successful")

            yield scrapy.Request('https://www.skool.com/playing-the-simulation-7538?c=&s=newest-cm&fl=', callback=self.parse_posts, meta={'page': 1})

    def parse_posts(self, response):
        # Extract post details using the provided XPaths
        arrayJSON = response.text.split('type="application/json">')
        finalText = arrayJSON[1].split('</script')[0]
        data = json.loads(finalText)
        props = data['props']['pageProps']['postTrees']
        for post_dict in props:
            # Directly access the 'post' key in the dictionary
            post = post_dict['post']
            likes = post.get('upvotes', post['metadata'].get('upvotes', 0))
            
            yield {
                'nombre': post['user']['firstName'],
                'apellido': post['user']['lastName'],
                'titulo': post['metadata']['title'],
                'url': 'https://www.skool.com/playing-the-simulation-7538/'+post['name'],
                'likes': likes,
                'created': post['createdAt'],
                'categoria': post['labelId']
            }
        
        # Handling pagination
        current_page = response.meta['page']
        if current_page < 5:
            next_page = current_page + 1
            next_page_url = f"{response.url.split('&p=')[0]}&p={next_page}"  # Ensure correct URL formation
            yield scrapy.Request(next_page_url, callback=self.parse_posts, meta={'page': next_page})
