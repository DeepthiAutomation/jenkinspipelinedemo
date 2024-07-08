from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Specify the path to the ChromeDriver executable
chrome_driver_path = '/path/to/chromedriver'
service = Service(chrome_driver_path)

# Set Chrome options
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

# Initialize WebDriver with the Service and Options
driver = webdriver.Chrome(service=service, options=options)

# Open a webpage
driver.get('https://example.com')

# Perform actions
title = driver.title
print(f'Title: {title}')

# Close the driver
driver.quit()
