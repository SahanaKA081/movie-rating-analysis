import unittest
import json
import os
from dotenv import load_dotenv
from app import app, get_db_collection
from seed_data import seed_database

load_dotenv()

class MovieRatingAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Seed test data into MongoDB before running API tests."""
        print("\n--- Seeding test dataset into MongoDB ---")
        seeded = seed_database()
        if not seeded:
            raise RuntimeError("MongoDB service is unavailable or seeding failed.")

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_dashboard_api(self):
        """Test GET /api/dashboard returns 200 OK and valid summary structure."""
        response = self.app.get('/api/dashboard')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertGreater(data["summary"]["total_records"], 500)
        self.assertGreater(data["summary"]["distinct_movies"], 30)
        self.assertGreater(data["summary"]["distinct_users"], 50)
        self.assertIn("top_movies", data)
        self.assertIn("genre_popularity", data)

    def test_02_get_ratings_pagination(self):
        """Test GET /api/ratings pagination and search."""
        response = self.app.get('/api/ratings?page=1&limit=10')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["data"]), 10)
        self.assertGreater(data["pagination"]["total_records"], 500)

    def test_03_crud_lifecycle(self):
        """Test POST, PUT, DELETE rating document lifecycle."""
        # 1. Create
        new_doc = {
            "user_id": "TEST_USER_999",
            "movie_title": "Test Movie 2026",
            "genre": "Sci-Fi",
            "release_year": 2026,
            "rating": 4.5
        }
        create_res = self.app.post('/api/ratings', json=new_doc)
        self.assertEqual(create_res.status_code, 201)
        created_data = json.loads(create_res.data)
        doc_id = created_data["data"]["_id"]
        self.assertIsNotNone(doc_id)

        # 2. Update
        update_doc = {
            "user_id": "TEST_USER_999",
            "movie_title": "Test Movie 2026 Updated",
            "genre": "Sci-Fi",
            "release_year": 2026,
            "rating": 5.0
        }
        update_res = self.app.put(f'/api/ratings/{doc_id}', json=update_doc)
        self.assertEqual(update_res.status_code, 200)

        # 3. Delete
        delete_res = self.app.delete(f'/api/ratings/{doc_id}')
        self.assertEqual(delete_res.status_code, 200)

    def test_04_analysis_endpoints(self):
        """Test all analytics aggregation endpoints."""
        endpoints = [
            '/api/analysis/top-movies?min_votes=3',
            '/api/analysis/most-rated',
            '/api/analysis/genres',
            '/api/analysis/rating-distribution',
            '/api/analysis/year-stats',
            '/api/analysis/insights'
        ]
        for ep in endpoints:
            res = self.app.get(ep)
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["status"], "success")

if __name__ == "__main__":
    unittest.main()
