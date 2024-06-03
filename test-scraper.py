from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the webdriver
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

# Set the search query and URL
search_query = "restaurants in new york"  # Replace with your search query
url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

# Navigate to the search results page
driver.get(url)

# Wait for the search results to load
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.section-result")))

# Extract the business listings
business_listings = driver.find_elements(By.CSS_SELECTOR, "div.section-result")

# Loop through each business listing and extract the attributes
for listing in business_listings:
    name_attribute = listing.get_attribute("aria-label")
    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
    phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
    
    address = listing.find_element(By.XPATH, address_xpath).text
    website = listing.find_element(By.XPATH, website_xpath).text
    phone_number = listing.find_element(By.XPATH, phone_number_xpath).text
    
    print(f"Name: {name_attribute}")
    print(f"Address: {address}")
    print(f"Website: {website}")
    print(f"Phone Number: {phone_number}")
    print("---------")

# Close the webdriver
driver.quit()