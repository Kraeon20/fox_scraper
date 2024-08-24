from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import time
import re
import requests
from dotenv import load_dotenv
import os

# from email_validator import validate_email, EmailNotValidError
# import subprocess

# subprocess.run(["playwright", "install"])


# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
EMAIL_VALIDATOR_API_KEY = os.getenv('API_KEY')



@dataclass
class Business:
    """holds business data"""
    name: str = None or "None"
    address: str = None or "None"
    email: str = None or "None"
    website: str = None or "None"
    phone_number: str = None or "None"
    linkedin: str = None or "None"
    twitter: str = None or "None"
    facebook: str = None or "None"
    instagram: str = None or "None"

@dataclass
class BusinessList:
    """holds list of Business objects"""
    business_list: list[Business] = field(default_factory=list)

def extract_coordinates_from_url(url: str) -> tuple[float,float]:
    """helper function to extract coordinates from url"""
    
    coordinates = url.split('/@')[-1].split('/')[0]
    # return latitude, longitude
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

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
        
        if response_data["isValid"] and response_data["isDeliverable"]:
            return True
        else:
            return False
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
        "Facebook": None,
        "Instagram": None,
        "Twitter": None,
        "LinkedIn": None
    }
    
    # Search for social media links
    for platform in social_media_links.keys():
        pattern = rf"https?:\/\/(www\.)?{platform.lower()}\.com\/(\w+)\/?"
        match = re.search(pattern, page.content())
        if match:
            social_media_links[platform] = match.group(0)
        else:
            social_media_links[platform] = "None"

    # LinkedIn may have different patterns for personal and company profiles
    # Search for both patterns and prioritize company profiles
    linkedin_pattern_company = r"https?://(www\.)?linkedin\.com/company/([\w-]+)/?"
    linkedin_pattern_personal = r"https?://(www\.)?linkedin\.com/in/([\w-]+)/?"

    match_company = re.search(linkedin_pattern_company, page.content())
    match_personal = re.search(linkedin_pattern_personal, page.content())

    if match_company:
        social_media_links["LinkedIn"] = match_company.group(0)
    elif match_personal:
        social_media_links["LinkedIn"] = match_personal.group(0)

    return social_media_links


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
        # page.wait_for_timeout(3000)
        page.keyboard.press("Enter")
        # page.wait_for_timeout(5000)
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
                website_xpath = '//a[@data-item-id="authority"]'
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
                        # Click on the link and wait for the new page to open
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
                    else:
                        business.website = None
                else:
                    business.website = "None"


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
        business.email,
        business.website,
        business.phone_number,
        business.linkedin,
        business.twitter,
        business.facebook,
        business.instagram,
    ]
    return row
    