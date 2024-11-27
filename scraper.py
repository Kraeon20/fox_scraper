from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import re

class Business:
    def __init__(self):
        self.name = ""
        self.address = ""
        self.website = ""
        self.phone_number = ""

class BusinessList:
    def __init__(self):
        self.businesses = []

    def add_business(self, business):
        self.businesses.append(business)

def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def main(search_term, quantity):
    driver = webdriver.Chrome()
    driver.maximize_window()

    driver.get("https://www.google.com/maps")

    # Enter search term
    search_box = wait_for_element(driver, By.ID, "searchboxinput")
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for search results to load

    # Locate the scrollable container for the listings
    listings_container = wait_for_element(driver, By.XPATH, '//div[contains(@aria-label, "Results for")]')

    # Scroll within the container until we get enough listings
    previously_counted = 0
    while True:
        # Scroll down within the listings container
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", listings_container)
        time.sleep(2)

        # Retrieve the listings links
        listings = driver.find_elements(By.XPATH, '//a[contains(@href, "https://www.google.com/maps/place")]')
        count = len(listings)

        if count >= quantity:
            time.sleep(2)
            listings = listings[:quantity]
            break
        elif count == previously_counted:
            print(f"Arrived at all available listings, total: {count}")
            break
        else:
            previously_counted = count

    print(f"Found {len(listings)} listings")

    business_list = BusinessList()

    for listing in listings:
        try:
            listing.click()
            time.sleep(2)

            business = Business()

            name_attribute = 'aria-label'
            address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
            website_xpath = '//a[@data-item-id="authority"]'
            website_domain_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
            phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'

            # Extracting name
            business.name = listing.get_attribute(name_attribute)
            if business.name:
                match = re.search(r"^[^·]+", business.name)
                if match:
                    business.name = match.group(0).strip()
                else:
                    business.name = business.name.strip()

            # Extracting address
            try:
                business.address = driver.find_element(By.XPATH, address_xpath).text
            except NoSuchElementException:
                business.address = "None"

            # Extracting website
            try:
                business.website = driver.find_element(By.XPATH, website_domain_xpath).text
            except NoSuchElementException:
                business.website = "None"

            # Extracting phone number
            try:
                business.phone_number = driver.find_element(By.XPATH, phone_number_xpath).text
            except NoSuchElementException:
                business.phone_number = "None"

            business_list.add_business(business)

            # Return to the main listing page
            driver.back()
            time.sleep(2)

        except Exception as e:
            print(f"Error processing listing: {e}")

    # Outputting collected data
    for business in business_list.businesses:
        print(f"Name: {business.name}")
        print(f"Address: {business.address}")
        print(f"Website: {business.website}")
        print(f"Phone: {business.phone_number}")
        print("-" * 40)

    driver.quit()

# Usage example
main("cafes in New York", 10)