import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from app.models import Listing, db
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")

def scrape_vrbo(start_url, num_pages):
    listings = []
    for page in range(num_pages):
        url = f"{start_url}&page={page+1}"
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Wait for page load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        property_cards = soup.find_all('li', {'class': 'property-card'})
        for card in property_cards:
            title = card.find('h3', {'class': 'property-card__name'}).text.strip() if card.find('h3', {'class': 'property-card__name'}) else ""
            description = card.find('div', {'class': 'property-card__description'}).text.strip() if card.find('div', {'class': 'property-card__description'}) else ""
            price = card.find('span', {'class': 'price'}).text.strip() if card.find('span', {'class': 'price'}) else ""
            location = card.find('span', {'class': 'property-card__location'}).text.strip() if card.find('span', {'class': 'property-card__location'}) else ""
            address = location  # VRBO doesn't provide separate address info
            link = card.find('a')['href'] if card.find('a') else ""

            listings.append({
                'title': title,
                'description': description,
                'price': float(price.replace('$', '').replace(',', '')) if price else None,
                'currency': 'USD',  # Assuming USD for simplicity
                'location': location,
                'address': address,
                'city': '',  # VRBO doesn't provide city separately
                'latitude': None,
                'longitude': None,
                'external_link': link
            })

    return listings

def scrape_booking(start_url, num_pages):
    listings = []
    for page in range(num_pages):
        url = f"{start_url}&page={page+1}"
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Wait for page load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        property_cards = soup.find_all('div', {'class': 'sr_item_content sr_card_content sr_property_block'})
        for card in property_cards:
            title = card.find('span', {'class': 'sr-hotel__name'}).text.strip() if card.find('span', {'class': 'sr-hotel__name'}) else ""
            description = card.find('div', {'class': 'hotel_description_wrapper_exp'}).text.strip() if card.find('div', {'class': 'hotel_description_wrapper_exp'}) else ""
            price = card.find('strong', {'class': 'price'}).text.strip() if card.find('strong', {'class': 'price'}) else ""
            location = card.find('span', {'class': 'sr-hotel__location'}).text.strip() if card.find('span', {'class': 'sr-hotel__location'}) else ""
            address = location  # Booking.com doesn't provide separate address info
            link = card.find('a')['href'] if card.find('a') else ""

            listings.append({
                'title': title,
                'description': description,
                'price': float(price.replace('$', '').replace(',', '')) if price else None,
                'currency': 'USD',  # Assuming USD for simplicity
                'location': location,
                'address': address,
                'city': '',  # Booking.com doesn't provide city separately
                'latitude': None,
                'longitude': None,
                'external_link': link
            })

    return listings

def scrape_airbnb(start_url, num_pages):
    listings = []
    for page in range(num_pages):
        url = f"{start_url}&page={page+1}"
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Wait for page load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        property_cards = soup.find_all('div', {'class': '_8ssblpx'})
        for card in property_cards:
            title = card.find('div', {'class': '_bzh5lkq'}).text.strip() if card.find('div', {'class': '_bzh5lkq'}) else ""
            description = card.find('div', {'class': '_kqh46o'}).text.strip() if card.find('div', {'class': '_kqh46o'}) else ""
            price = card.find('span', {'class': '_1p7iugi'}).text.strip() if card.find('span', {'class': '_1p7iugi'}) else ""
            location = card.find('div', {'class': '_30je6rj'}).text.strip() if card.find('div', {'class': '_30je6rj'}) else ""
            address = location  # Airbnb doesn't provide separate address info
            link = card.find('a')['href'] if card.find('a') else ""

            listings.append({
                'title': title,
                'description': description,
                'price': float(price.replace('$', '').replace(',', '')) if price else None,
                'currency': 'USD',  # Assuming USD for simplicity
                'location': location,
                'address': address,
                'city': '',  # Airbnb doesn't provide city separately
                'latitude': None,
                'longitude': None,
                'external_link': link
            })

    return listings

def save_to_database(listings):
    try:
        for listing in listings:
            new_listing = Listing(
                title=listing['title'],
                description=listing['description'],
                price=listing['price'],
                currency=listing['currency'],
                location=listing['location'],
                address=listing['address'],
                city=listing['city'],
                latitude=listing['latitude'],
                longitude=listing['longitude'],
                external_link=listing['external_link']
            )
            db.session.add(new_listing)
        db.session.commit()
        logger.info(f"Successfully added {len(listings)} listings to the database.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to add listings to database: {str(e)}")

# Usage
try:
    vrbo_listings = scrape_vrbo("https://www.vrbo.com/search/keywords:Lagos", 5)
    booking_listings = scrape_booking("https://www.booking.com/searchresults.html?ss=Lagos", 5)
    airbnb_listings = scrape_airbnb("https://www.airbnb.com/s/New York City/homes", 5)

    all_listings = vrbo_listings + booking_listings + airbnb_listings
    save_to_database(all_listings)
except Exception as e:
    logger.error(f"An error occurred during scraping: {str(e)}")

logger.info("Scraping completed.")
