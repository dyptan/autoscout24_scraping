import unittest
from pymongo.errors import BulkWriteError

class TestDuplicateErrorParsing(unittest.TestCase):
    def test_count_duplicates(self):
        # Simulate a BulkWriteError with multiple duplicate errors
        error_details = {
            'writeErrors': [
                {
                    'index': 0,
                    'code': 11000,
                    'errmsg': 'E11000 duplicate key error collection: autoscout24.listings index: unique_ad_link dup key: { ad-link: "https://www.autoscout24.de/angebote/volkswagen-golf-vii-standheizung-cup-bluemotiontech-benzin-schwarz-e401c121-5a46-4ef2-b316-3a63e90648b5" }',
                    'keyPattern': {'ad-link': 1},
                    'keyValue': {'ad-link': 'https://www.autoscout24.de/angebote/volkswagen-golf-vii-standheizung-cup-bluemotiontech-benzin-schwarz-e401c121-5a46-4ef2-b316-3a63e90648b5'},
                    'op': {'make': 'volkswagen', 'model': 'golf', 'mileage': 174000, 'fuel-type': 'b', 'first-registration': '02-2015', 'price': 5950, 'zip': 12249.0, 'ad-link': 'https://www.autoscout24.de/angebote/volkswagen-golf-vii-standheizung-cup-bluemotiontech-benzin-schwarz-e401c121-5a46-4ef2-b316-3a63e90648b5', 'job_id': 'scraper_1746916038', '_id': 'ObjectId("681fd342255dbbdbf0387c12")'}
                },
                {
                    'index': 1,
                    'code': 11000,
                    'errmsg': 'E11000 duplicate key error collection: autoscout24.listings index: unique_ad_link dup key: { ad-link: "https://www.autoscout24.de/angebote/volkswagen-golf-vii-standheizung-cup-bluemotiontech-benzin-schwarz-e401c121-5a46-4ef2-b316-3a63e90648b5" }',
                    'keyPattern': {'ad-link': 1},
                    'keyValue': {'ad-link': 'https://www.autoscout24.de/angebote/volkswagen-golf-vii-standheizung-cup-bluemotiontech-benzin-schwarz-e401c121-5a46-4ef2-b316-3a63e90648b5'},
                    'op': {'make': 'volkswagen', 'model': 'golf', 'mileage': 174000, 'fuel-type': 'b', 'first-registration': '02-2015', 'price': 5950, 'zip': 12249.0, 'ad-link': 'https://www.autoscout24.de/angebote/volkswagen-golf-vii-standheizung-cup-bluemotiontech-benzin-schwarz-e401c121-5a46-4ef2-b316-3a63e90648b5', 'job_id': 'scraper_1746916038', '_id': 'ObjectId("681fd342255dbbdbf0387c12")'}
                }
            ]
        }

        # Create a BulkWriteError instance
        bulk_write_error = BulkWriteError(error_details)

        # Parse the error and count all duplicate entries
        duplicate_count = len(bulk_write_error.details['writeErrors'])

        # Assert the count of duplicates
        self.assertEqual(duplicate_count, 2)

if __name__ == "__main__":
    unittest.main()