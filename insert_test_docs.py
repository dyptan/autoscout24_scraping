from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client.autoscout24  # Use the main database
collection = db.saved_documents

collection.delete_many({})
collection.insert_many([
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
    },
    {
        "make": "Toyota",
        "model": "Corolla",
        "year": 2021,
        "price": 18000,
        "mileage": 20000,
        "location": "Hamburg",
        "createdAt": datetime.fromisoformat("2025-05-03T09:00:00")
    }
])

print("Test documents inserted into main database.")
