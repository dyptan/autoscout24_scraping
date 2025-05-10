import time
import pandas as pd
from selenium import webdriver
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class AutoScout24Scraper:
    def __init__(self, make, model, version, year_from, year_to, power_from, power_to, powertype, zip, zipr, price_to, scraper_id):
        self.scraper_id = scraper_id
        self.make = make
        self.model = model
        self.version = version
        self.year_from = year_from
        self.year_to = year_to
        self.power_from = power_from
        self.power_to = power_to
        self.powertype = powertype
        self.zip = zip
        self.zipr = zipr
        self.price_to = price_to
        self.base_url = ("https://www.autoscout24.de/lst/{make}/{model}?atype=C&cy=D&damaged_listing=exclude&desc=0&"
                         "fregfrom={year_from}&fregto={year_to}&powerfrom={power_from}&powerto={power_to}&"
                         "powertype={powertype}&priceto={price_to}&sort=standard&"
                         "source=homepage_search-mask&ustate=N%2CU&zip={zip}&zipr={zipr}")
        self.listing_frame = pd.DataFrame(
            columns=["make", "model", "mileage", "fuel-type", "first-registration", "price"])
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--incognito")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--headless") 
        self.options.add_argument("--disable-gpu") 
        self.options.add_argument("--no-sandbox")  
        self.options.add_argument("--disable-dev-shm-usage")  
        self.browser = webdriver.Chrome(options=self.options)
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo_client["autoscout24"]
        self.collection = self.db["listings"]
        self.collection.create_index("ad-link", unique=True, name="unique_ad_link", background=True)

    def generate_urls(self, num_pages):
        url_list = [self.base_url.format(make=self.make, model=self.model, version=self.version, year_from=self.year_from, year_to=self.year_to,
                                         power_from=self.power_from, power_to=self.power_to, powertype=self.powertype, price_to=self.price_to, zip=self.zip, zipr=self.zipr)]
        for i in range(2, num_pages + 1):
            url_to_add = (self.base_url.format(make=self.make, model=self.model, version=self.version, year_from=self.year_from, year_to=self.year_to,
                                               power_from=self.power_from, power_to=self.power_to, powertype=self.powertype, price_to=self.price_to, zip=self.zip, zipr=self.zipr) +
                          f"&page={i}&sort=standard&source=listpage_pagination&ustate=N%2CU")
            url_list.append(url_to_add)
        return url_list

    def scrape(self, num_pages, verbose=True):
        # Clear the listing_frame at the start of each job cycle
        self.listing_frame = pd.DataFrame(columns=["make", "model", "mileage", "fuel-type", "first-registration", "price"])

        url_list = []
        for page in range(1, num_pages + 1):
            url_list.extend(self.generate_urls(page))

        print(url_list)

        for webpage in url_list:
            self.browser.get(webpage)
            listings = self.browser.find_elements("xpath", "//article[contains(@class, 'cldt-summary-full-item') and @data-boosting_product='none' and @data-source='listpage_search-results']")

            print("listings " + str(len(listings)))
            for listing in listings:
                data_make = listing.get_attribute("data-make")
                data_model = listing.get_attribute("data-model")
                data_mileage = listing.get_attribute("data-mileage")
                data_mileage = int(data_mileage) if data_mileage else None
                data_fuel_type = listing.get_attribute("data-fuel-type")
                data_first_registration = listing.get_attribute("data-first-registration")
                data_price = listing.get_attribute("data-price")
                data_price = int(data_price) if data_price else None
                data_zip_code = listing.get_attribute("data-listing-zip-code")
                data_zip_code = int(data_zip_code) if data_zip_code else None

                # Extract the ad link
                ad_link_element = listing.find_element("xpath", ".//a[contains(@href, '/angebote/')]")
                ad_link = ad_link_element.get_attribute("href") if ad_link_element else None

                listing_data = {
                    "make": data_make,
                    "model": data_model,
                    "mileage": data_mileage,
                    "fuel-type": data_fuel_type,
                    "first-registration": data_first_registration,
                    "price": data_price,
                    "zip": data_zip_code,
                    "ad-link": ad_link  # Add the ad link to the data
                }

                if verbose:
                    print(listing_data)

                frame = pd.DataFrame(listing_data, index=[0])
                self.listing_frame = self.listing_frame._append(frame, ignore_index=True)
                time.sleep(1)

    def save_to_mongo(self):
        if not self.listing_frame.empty:
            data = self.listing_frame.to_dict(orient="records")
            successfully_saved = 0
            duplicate_count = 0

            for record in data:
                try:
                    self.collection.insert_one(record)
                    successfully_saved += 1
                except DuplicateKeyError:
                    duplicate_count += 1

            documents_saved = successfully_saved  # Correct the metric by excluding duplicates
            print(f"Successfully saved {documents_saved} documents to MongoDB")
            print(f"Skipped {duplicate_count} duplicate documents.")

            # Return documents_saved for external use
            return documents_saved
        else:
            print("No data to save to MongoDB")
            return 0

    def quit_browser(self):
        self.browser.quit()
        self.mongo_client.close()


if __name__ == "__main__":
        # Test the scraper
    scraper = AutoScout24Scraper(
        make="volkswagen",
        model="golf",
        version="",
        year_from=2015, 
        year_to=2020,  
        power_from=50,  
        power_to=200,  
        powertype="kw",
        zip="38442-wolfsburg",  
        zipr=200,  
        price_to=6000,
        scraper_id="test_scraper_123"
    )

    try:
        scraper.scrape(num_pages=1, verbose=True)
        scraper.save_to_mongo()
    finally:
        scraper.quit_browser()