from AutoScout24Scraper import AutoScout24Scraper
from pymongo import MongoClient
import os

class DummyScraper(AutoScout24Scraper):
    def __init__(self, *args, **kwargs):
        # Don't call the parent __init__ that launches Selenium
        self.scraper_id = kwargs.get('scraper_id', 'dummy')
        self.make = kwargs.get('make', 'volkswagen')
        self.model = kwargs.get('model', 'golf')
        self.version = kwargs.get('version', '')
        self.year_from = kwargs.get('year_from', 2015)
        self.year_to = kwargs.get('year_to', 2020)
        self.power_from = kwargs.get('power_from', 50)
        self.power_to = kwargs.get('power_to', 200)
        self.powertype = kwargs.get('powertype', 'kw')
        self.zip = kwargs.get('zip', '38442-wolfsburg')
        self.zipr = kwargs.get('zipr', 200)
        self.price_to = kwargs.get('price_to', 6000)
        import pandas as pd
        self.listing_frame = pd.DataFrame(columns=["make", "model", "mileage", "fuel-type", "first-registration", "price", "zip", "ad-link", "location"])
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/autoscout24")
        from pymongo import MongoClient
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client.get_default_database()
        self.collection = self.db["listings"]
        self.collection.create_index("ad-link", unique=True, name="unique_ad_link", background=True)
    def quit_browser(self):
        self.mongo_client.close()

# Set up test parameters for the dummy scraper
scraper = DummyScraper(
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
    scraper_id="test_scraper_check_fields"
)

# Simulate a scraped listing (bypass Selenium for this test)
scraper.listing_frame = scraper.listing_frame._append({
    "make": "volkswagen",
    "model": "golf",
    "mileage": 123456,
    "fuel-type": "petrol",
    "first-registration": "2019-05",
    "price": 9999,
    "zip": 38442,
    "ad-link": "https://www.autoscout24.de/angebote/test-ad-link",
    "location": "Berlin"
}, ignore_index=True)

# Save to MongoDB
scraper.save_to_mongo()

# Check the inserted document
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/autoscout24")
client = MongoClient(mongo_uri)
db = client.get_default_database()
collection = db["listings"]
doc = collection.find_one({"ad-link": "https://www.autoscout24.de/angebote/test-ad-link"})
print("Inserted document:", doc)

# Comment out cleanup for fetch test
# del_result = collection.delete_one({"ad-link": "https://www.autoscout24.de/angebote/test-ad-link"})
# print("Deleted test document count:", del_result.deleted_count)

scraper.quit_browser()
