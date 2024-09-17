import os
import pandas as pd
from dataclasses import asdict, dataclass, field
import requests
import re
import time
from playwright.sync_api import sync_playwright

EMAIL_VALIDATOR_API_KEY = os.getenv('EMAIL_VALIDATOR_API_KEY')

@dataclass
class Business:
    """holds business data"""
    name: str = "None"
    address: str = "None"
    email: str = "None"
    website: str = "None"
    phone_number: str = "None"
    linkedin: str = "None"
    twitter: str = "None"
    facebook: str = "None"
    instagram: str = "None"

@dataclass
class BusinessList:
    """holds list of Business objects"""
    business_list: list[Business] = field(default_factory=list)

def validate_email_api(email: str) -> bool:
    url = "https://email-validator28.p.rapidapi.com/email-validator/validate"
    querystring = {"email": email}

    headers = {
        "x-rapidapi-key": EMAIL_VALIDATOR_API_KEY,
        "x-rapidapi-host": "email-validator28.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response_data = response.json()
        return response_data.get("isValid", False) and response_data.get("isDeliverable", False)
    except Exception as e:
        print(f"Error validating email {email}: {e}")
        return False

def extract_emails_from_page(page):
    """Extract email from a webpage using a regex pattern and validate it"""
    content = page.content()
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, content)

    for email in emails:
        if validate_email_api(email):
            return email
    return "None"

def extract_social_media_links(page):
    """Extracts social media links from a webpage"""
    social_media_links = {
        "Facebook": "None",
        "Instagram": "None",
        "Twitter": "None",
        "LinkedIn": "None"
    }
    
    # Search for social media links
    for platform in social_media_links.keys():
        pattern = rf"https?:\/\/(www\.)?{platform.lower()}\.com\/(\w+)\/?"
        match = re.search(pattern, page.content())
        if match:
            social_media_links[platform] = match.group(0)

    return social_media_links

def main(search_term, quantity=30):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps")
        # wait is added for dev phase. can remove it in production
        # page.wait_for_timeout(5000)
        

        page.locator('//input[@id="searchboxinput"]').fill(search_term)
        # page.wait_for_timeout(3000)

        page.keyboard.press("Enter")
        # page.wait_for_timeout(5000)

        # scrolling
        page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

    
        previously_counted = 0
        while True:
            page.mouse.wheel(0, 10000)
            page.wait_for_timeout(2000)

            count = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
            if count >= quantity:
                time.sleep(5)
                listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:quantity]
                break
            else:
                if count == previously_counted:
                    listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                    print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                    break
                else:
                    previously_counted = count
        
        print(f"Found {len(listings)} listings")


        business_list = BusinessList()

        for listing in listings:
            try:
                listing.click()
                page.wait_for_timeout(1000)


                business = Business()

                name_attribute = 'aria-label'
                address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                website_xpath = '//a[@data-item-id="authority"]'
                website_domain_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'


                
                business.name = listing.get_attribute(name_attribute)
                if business.name:
                    match = re.search(r"^[^·]+", business.name)
                    if match:
                        business.name = match.group(0).strip()
                    else:
                        business.name = business.name.strip()
                        
                business.address = page.locator(address_xpath).inner_text() if page.locator(address_xpath).count() > 0 else "None"
                business.website = page.locator(website_domain_xpath).inner_text() if page.locator(website_domain_xpath).count() > 0 else "None"
                business.phone_number = page.locator(phone_number_xpath).inner_text() if page.locator(phone_number_xpath).count() > 0 else "None"

                if business.website != "None":
                    with page.context.expect_page() as new_page_info:
                        page.locator(website_xpath).click()
                    new_page = new_page_info.value
                    new_page.wait_for_load_state("networkidle")
                    business.email = extract_emails_from_page(new_page)
                    social_media_links = extract_social_media_links(new_page)
                    business.facebook = social_media_links["Facebook"]
                    business.instagram = social_media_links["Instagram"]
                    business.twitter = social_media_links["Twitter"]
                    business.linkedin = social_media_links["LinkedIn"]

                try:
                    # Scraping logic
                    business_list.business_list.append(business)
                    print(f"Processed: {business.name}")
                except Exception as e:
                    print(f'Error occurred while processing {business.name}: {e}')
                    business_list.business_list.append(business)

            except Exception as e:
                print(f'Error occurred: {e}')

        data = [asdict(business) for business in business_list.business_list]
        df = pd.DataFrame(data)
        df.to_excel('business_data.xlsx', index=False)
        print("Data saved to business_data.xlsx")

        browser.close()

if __name__ == "__main__":
    main("gift shops IN BRONX, NEW YORK")