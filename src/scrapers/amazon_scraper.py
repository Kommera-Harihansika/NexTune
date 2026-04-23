"""
Amazon Audio Products Scraper using Selenium with Stealth Mode

This scraper uses undetected_chromedriver to bypass bot detection and
scrape wireless bluetooth earphones data from Amazon India.
"""

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_stealth_driver():
    """
    Initialize a stealth Chrome driver that bypasses bot detection.
    
    Returns:
        WebDriver instance configured for stealth scraping
    """
    # A professional setup always masks the headless browser
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = uc.Chrome(options=options)
    logger.info("Stealth driver initialized successfully")
    return driver


def scrape_amazon_audio(pages=1):
    """
    Scrape wireless bluetooth earphones data from Amazon India.
    
    Args:
        pages: Number of pages to scrape (default: 1)
        
    Returns:
        DataFrame with scraped product data
    """
    driver = initialize_stealth_driver()
    base_url = "https://www.amazon.in/s?k=wireless+bluetooth+earphones"
    scraped_data = []
    
    logger.info(f"Starting scrape for {pages} page(s)")
    
    for page in range(1, pages + 1):
        logger.info(f"Scraping page {page}/{pages}")
        driver.get(f"{base_url}&page={page}")
        
        # Critical: Human-like delay to let DOM render
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Target the specific Div class Amazon uses for product cards
        products = soup.find_all('div', {'data-component-type': 's-search-result'})
        logger.info(f"Found {len(products)} products on page {page}")
        
        for item in products:
            try:
                # Extracting specific nodes (Note: Amazon changes these class names frequently)
                title = item.find('span', {'class': 'a-size-medium'}).text.strip()
                price_str = item.find('span', {'class': 'a-price-whole'}).text.strip()
                reviews_str = item.find('span', {'class': 'a-size-base s-underline-text'}).text.strip()
                rating_str = item.find('span', {'class': 'a-icon-alt'}).text.strip()
                
                # Immediate Data Cleaning (Transform phase of ETL)
                price = int(price_str.replace(',', ''))
                reviews = int(reviews_str.replace(',', ''))
                rating = float(rating_str.split(' ')[0])
                
                scraped_data.append({
                    'Raw_Title': title,
                    'Selling_Price_INR': price,
                    'Number_of_Reviews': reviews,
                    'Average_Rating': rating
                })
                
            except AttributeError:
                # Silently pass if a product card is missing a price/rating (e.g., sponsored ads)
                continue
    
    driver.quit()
    logger.info(f"Scraping completed. Total products scraped: {len(scraped_data)}")
    
    return pd.DataFrame(scraped_data)


def main():
    """
    Main execution function for scraping Amazon audio products.
    """
    # Scrape 5 pages of results
    df = scrape_amazon_audio(pages=5)
    
    # Save to CSV
    output_file = "data/raw_amazon_scrape.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"Data saved to {output_file}")
    
    # Display summary
    print("\n" + "=" * 80)
    print("SCRAPING SUMMARY")
    print("=" * 80)
    print(f"Total products scraped: {len(df)}")
    print(f"Price range: ₹{df['Selling_Price_INR'].min()} - ₹{df['Selling_Price_INR'].max()}")
    print(f"Average rating: {df['Average_Rating'].mean():.2f}")
    print(f"Total reviews: {df['Number_of_Reviews'].sum():,}")
    print("=" * 80)


if __name__ == "__main__":
    main()
