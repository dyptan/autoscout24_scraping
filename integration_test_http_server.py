import unittest
from http_server import resolve_fetch_saved_documents
from pymongo import MongoClient
from datetime import datetime

class TestIntegrationFetchSavedDocuments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Connect to the test database and insert test data
        cls.client = MongoClient("mongodb://localhost:27017/")
        cls.db = cls.client.autoscout24_test
        cls.collection = cls.db.saved_documents
        cls.collection.delete_many({})  # Clean up before test
        cls.collection.insert_many([
            {
                "make": "Volkswagen",
                "model": "Golf",
                "year": 2020,
                "price": 15000,
                "mileage": 50000,
                "location": "Berlin",
                "createdAt": datetime.fromisoformat("2025-05-01T10:00:00")
            },
            {
                "make": "BMW",
                "model": "X5",
                "year": 2019,
                "price": 30000,
                "mileage": 30000,
                "location": "Munich",
                "createdAt": datetime.fromisoformat("2025-05-02T12:00:00")
            }
        ])

    @classmethod
    def tearDownClass(cls):
        # Clean up after test
        cls.collection.delete_many({})
        cls.client.close()

    def test_fetch_by_created_after(self):
        # Patch the resolver to use the test database
        original_mongo_client = resolve_fetch_saved_documents.__globals__["MongoClient"]
        resolve_fetch_saved_documents.__globals__["MongoClient"] = lambda *args, **kwargs: MongoClient("mongodb://localhost:27017/")
        resolve_fetch_saved_documents.__globals__["MongoClient"]().autoscout24 = self.db

        result = resolve_fetch_saved_documents(
            None, None,
            page=1,
            pageSize=10,
            createdAfter="2025-04-30T00:00:00",
            db_name="autoscout24_test"
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["make"], "Volkswagen")
        self.assertEqual(result[1]["make"], "BMW")

        # Restore original MongoClient
        resolve_fetch_saved_documents.__globals__["MongoClient"] = original_mongo_client

    def test_create_scraper_instance(self):
        from http_server import AutoScout24Scraper
        import time
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
            scraper_id="test_scraper_id"
        )
        time.sleep(5)
        self.assertEqual(scraper.make, "volkswagen")
        self.assertEqual(scraper.model, "golf")
        self.assertEqual(scraper.year_from, 2015)
        self.assertEqual(scraper.year_to, 2020)
        self.assertEqual(scraper.power_from, 50)
        self.assertEqual(scraper.power_to, 200)
        self.assertEqual(scraper.powertype, "kw")
        self.assertEqual(scraper.zip, "38442-wolfsburg")
        self.assertEqual(scraper.zipr, 200)
        self.assertEqual(scraper.price_to, 6000)
        self.assertEqual(scraper.scraper_id, "test_scraper_id")

if __name__ == "__main__":
    unittest.main()
