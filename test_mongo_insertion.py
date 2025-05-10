import unittest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

class TestMongoInsertion(unittest.TestCase):
    def setUp(self):
        # Set up MongoDB client and collection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["autoscout24"]
        self.collection = self.db["listings"]
        self.collection.create_index("ad-link", unique=True, name="unique_ad_link", background=True)

        # Insert a document to test duplicate handling
        self.test_document = {
            "_id": "681fcdf44289b470d2eee807",
            "make": "volkswagen",
            "model": "golf",
            "mileage": 174000,
            "fuel-type": "b",
            "first-registration": "02-2015",
            "price": 5950,
            "zip": 12249.0,
            "ad-link": "https://www.autoscout24.de/angebote/volkswagen-golf-vii-standheizung-cup-bluemotiontech-benzin-schwarz-e401c121-5a46-4ef2-b316-3a63e90648b5",
            "job_id": "scraper_1746914679"
        }
        try:
            self.collection.insert_one(self.test_document)
        except Exception as e:
            print("Document already exists in the collection during setup.")

    def tearDown(self):
        # Clean up the collection after the test
        self.collection.delete_many({})
        self.client.close()

    def test_duplicate_insertion(self):
        # Attempt to insert the same document again to trigger a duplicate error
        try:
            self.collection.insert_one(self.test_document)
        except DuplicateKeyError as e:
            self.assertIn("E11000 duplicate key error", str(e))
        else:
            self.fail("Duplicate error was not raised.")

if __name__ == "__main__":
    unittest.main()