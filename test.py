from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys
import re
from email_validator import validate_email, EmailNotValidError


@dataclass
class Business:
    """holds business data"""
    name: str = None
    address: str = None
    email: str = None  # New field to hold email addresses
    website: str = None
    phone_number: str = None
    linkedin: str = None  # Field to hold LinkedIn username
    twitter: str = None  # Field to hold Twitter username
    facebook: str = None  # Field to hold Facebook username
    instagram: str = None  # Field to hold Instagram username

    # reviews_count: int = None
    # reviews_average: float = None
    # latitude: float = None
    # longitude: float = None

@dataclass
class BusinessList:
    """holds list of Business objects"""
    business_list: list[Business] = field(default_factory=list)

def extract_coordinates_from_url(url: str) -> tuple[float,float]:
    """helper function to extract coordinates from url"""
    
    coordinates = url.split('/@')[-1].split('/')[0]
    # return latitude, longitude
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])


def extract_emails_from_page(page):
    """Extracts valid email addresses from a webpage"""
    email = extract_email_from_page_content(page.content())
    if email:
        # Check if the extracted email matches any placeholder pattern indicating a form
        form_email_placeholders = ["youremail@email.com", "example@emailcom"]
        if email.lower() in form_email_placeholders:
            return "no official email found. there was a form"
        
        # Validate the extracted email address
        try:
            email_info = validate_email(email, check_deliverability=True)
            return email_info.normalized
        except EmailNotValidError as e:
            # If the email address is not valid or deliverable, return None
            return "None"
    
    # If no valid email is found, search on other pages
    other_pages = ["contact", "contact-us"]
    for page_name in other_pages:
        page.goto(f"{page.url}/{page_name}")
        page.wait_for_load_state("networkidle")
        email = extract_email_from_page_content(page.content())
        if email:
            # Check if the extracted email matches any placeholder pattern indicating a form
            form_email_placeholders = ["youremail@email.com", "example@emailcom"]
            if email.lower() in form_email_placeholders:
                return "no official email found. there was a form"
            
            # Validate the extracted email address
            try:
                email_info = validate_email(email, check_deliverability=True)
                return email_info.normalized
            except EmailNotValidError as e:
                # If the email address is not valid or deliverable, return None
                return None
    
    # If no valid email is found, return "None" as a string
    return "None"



def extract_email_from_page_content(content):
    """Extracts a valid email address from webpage content"""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, content)
    # Find the first valid email
    for email in emails:
        if "@" in email:
            return email
    
    # Extract the first email from mailto links
    mailto_pattern = r"mailto:([^\s@]+@[^\s@]+\.[^\s@]+)"
    mailto_emails = re.findall(mailto_pattern, content)
    valid_mailto_email = validate_email(mailto_emails)

    if valid_mailto_email:
        return valid_mailto_email
    
    return None


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


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps", timeout=6000)
        # wait is added for dev phase. can remove it in production
        page.wait_for_timeout(5000)

        print(f"-----\n{search_term}".strip())

        page.locator('//input[@id="searchboxinput"]').fill(search_term)
        page.wait_for_timeout(3000)

        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)

        # scrolling
        page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

        # this variable is used to detect if the bot
        # scraped the same number of listings in the previous iteration
        previously_counted = 0
        while True:
            page.mouse.wheel(0, 10000)
            page.wait_for_timeout(3000)

            if (
                page.locator(
                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                ).count()
                >= quantity
            ):
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

        for i, listing in enumerate(listings):
            try:
                listing.click()
                page.wait_for_timeout(5000)

                business = Business()

                name_attribute = 'aria-label'
                address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'

                if len(listing.get_attribute(name_attribute)) >= 1:
                    business.name = listing.get_attribute(name_attribute)
                else:
                    business.name = ""

                if page.locator(address_xpath).count() > 0:
                    business.address = page.locator(address_xpath).all()[0].inner_text()
                else:
                    business.address = ""

                if page.locator(website_xpath).count() > 0:
                    website = page.locator(website_xpath).all()[0].inner_text()
                    if website:
                        website = "https://" + website if not website.startswith("http") else website
                        business.website = website
                        new_page = browser.new_page()
                        new_page.goto(website)
                        new_page.wait_for_load_state("networkidle")
                        business.email = extract_emails_from_page(new_page)
                        social_media_links = extract_social_media_links(new_page)
                        business.facebook = social_media_links["Facebook"]
                        business.instagram = social_media_links["Instagram"]
                        business.twitter = social_media_links["Twitter"]
                        business.linkedin = social_media_links["LinkedIn"]
                        new_page.close()
                    else:
                        business.website = None
                else:
                    business.website = ""

                if page.locator(phone_number_xpath).count() > 0:
                    business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                else:
                    business.phone_number = ""

                business_list.business_list.append(business)

                # Print the business information in real-time
                print_business_info(business)

            except Exception as e:
                print(f'Error occurred: {e}')


        browser.close()

        return business_list

def print_business_info(business):
    """Prints business information in real-time"""
    print("--------------------------------------")
    print(f"Name: {business.name}")
    print(f"Address: {business.address}")
    print(f"Email: {business.email}")
    print(f"Website: {business.website}")
    print(f"Phone Number: {business.phone_number}")
    print(f"LinkedIn: {business.linkedin}")
    print(f"Twitter: {business.twitter}")
    print(f"Facebook: {business.facebook}")
    print(f"Instagram: {business.instagram}")
    print("--------------------------------------")


if __name__ == "__main__":
    search_term = "lawyers in Texas, USA"
    quantity = 9
    main()
