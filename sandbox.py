from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import re
import time

@dataclass
class Business:
    """holds business data"""
    name: str = None or "None"
    address: str = None or "None"
    phone_number: str = None or "None"
    website: str = None or "None"
    email: str = None or "None"

@dataclass
class BusinessList:
    """holds list of Business objects"""
    business_list: list[Business] = field(default_factory=list)

def extract_coordinates_from_url(url: str) -> tuple[float,float]:
    """helper function to extract coordinates from url"""
    
    coordinates = url.split('/@')[-1].split('/')[0]
    # return latitude, longitude
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

def extract_email_from_website(page):
    """Extract email from a webpage using a regex pattern"""
    # Get the entire page content
    content = page.content()
    # Regex pattern to find emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, content)
    # Return the first email found or None
    return emails[0] if emails else "None"

def main(search_term, quantity=9999999):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Navigating to Google Maps...")
        page.goto("https://www.google.com/maps")
        print("Navigation successful!")
        page.wait_for_timeout(5000)

        print(f"-----\n{search_term}".strip())

        page.locator('//input[@id="searchboxinput"]').fill(search_term)
        page.keyboard.press("Enter")
        page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

        previously_counted = 0
        while True:
            page.mouse.wheel(0, 10000)
            href = page.evaluate('() => document.location.href')
            page.wait_for_timeout(3000)

            if (
                page.locator(
                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                ).count()
                >= quantity
            ):
                time.sleep(5) # Wait for 5 seconds
                listings = page.locator(
                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                ).all()[:quantity]
                break
            else:
                if (
                    page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).count()
                    == previously_counted
                ):
                    listings = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()
                    print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                    break
                else:
                    previously_counted = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).count()

        business_list = BusinessList()

        for listing in listings:
            try:
                listing.click()
                page.wait_for_timeout(5000)

                business = Business()

                name_attribute = 'aria-label'
                address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'

                business.name = listing.get_attribute(name_attribute)
                

                if page.locator(address_xpath).count() > 0:
                    business.address = page.locator(address_xpath).all()[0].inner_text()
                else:
                    business.address = "None"

                if page.locator(website_xpath).count() > 0:
                    website = page.locator(website_xpath).all()[0].inner_text()
                    if website:
                        website = "https://" + website if not website.startswith("http") else website
                        business.website = website
                        new_page = browser.new_page()
                        new_page.goto(website)
                        new_page.wait_for_load_state("networkidle")
                        # Extract email from the website
                        business.email = extract_email_from_website(new_page)
                        new_page.close()
                    else:
                        business.website = None
                        business.email = "None"
                else:
                    business.website = "None"
                    business.email = "None"

                if page.locator(phone_number_xpath).count() > 0:
                    business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                else:
                    business.phone_number = "None"

                yield asdict(business)
            except Exception as e:
                print(f'Error occurred: {e}')


        browser.close()

def business_to_table_row(business):
    row = [
        business.name,
        business.address,
        business.phone_number,
        business.email,  # Added email to the row
    ]
    return row
