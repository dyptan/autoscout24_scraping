import unittest
from http_server import resolve_fetch_saved_documents
from pymongo import MongoClient
from datetime import datetime
import os
import sys

class TestIntegrationFetchSavedDocuments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mongo_uri = "mongodb://localhost:27017/"
        print(f"Connecting to MongoDB URI: {mongo_uri}")
        cls.client = MongoClient(mongo_uri)
        cls.db = cls.client.autoscout24
        cls.collection = cls.db.listings
        print(f"Inserting into database: {cls.db.name}, collection: {cls.collection.name}")
        cls.collection.delete_many({})
        result = cls.collection.insert_many([
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
        print(f"Inserted document IDs: {result.inserted_ids}")
        print(f"Document count after insert: {cls.collection.count_documents({})}")

    @classmethod
    def tearDownClass(cls):
        # Only clean up if --cleanup is passed
        cleanup = False
        if '--cleanup' in sys.argv:
            cleanup = True
        if cleanup:
            cls.collection.delete_many({})
        print(f"Document count after test: {cls.collection.count_documents({})}")
        cls.client.close()

    def test_fetch_by_created_after(self):
        result = resolve_fetch_saved_documents(
            None, None,
            page=1,
            pageSize=10,
            createdAfter="2025-04-30T00:00:00",
            db_name="autoscout24",
            collection_name="listings"
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["make"], "Volkswagen")
        self.assertEqual(result[1]["make"], "BMW")

if __name__ == "__main__":
    if '--cleanup' in sys.argv:
        sys.argv.remove('--cleanup')
    unittest.main()
