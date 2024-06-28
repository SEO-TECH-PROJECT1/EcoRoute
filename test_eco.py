import unittest
from app import (
    create_connection,
    create_table,
    get_directions,
    geocode_address,
    get_weather,
    get_tips,
    store_route
)
import os
import json

class TestEcoRouteFunctions(unittest.TestCase):
    
    def setUp(self):
        # Setup any pre-requisites for the tests
        self.test_db = 'test_ecoroute.db'
        os.environ['DB_PATH'] = self.test_db
        create_table()  # Ensure table creation

    def tearDown(self):
        # Clean up the test database
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_create_connection(self):
        conn = create_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_get_directions(self):
        start_coords = (37.7749, -122.4194)  # San Francisco
        end_coords = (34.0522, -118.2437)    # Los Angeles
        response = get_directions(start_coords, end_coords)
        self.assertIn('routes', response)

    def test_geocode_address(self):
        lat, lon = geocode_address("1600 Amphitheatre Parkway, Mountain View, CA")
        self.assertIsNotNone(lat)
        self.assertIsNotNone(lon)

    def test_get_weather(self):
        weather_data = get_weather("Mountain View")
        self.assertIn('weather', weather_data)

    def test_get_tips(self):
        route_info = "Start at Mountain View, CA, End at San Francisco, CA"
        tips = get_tips(route_info)
        self.assertTrue(len(tips) > 0)

    def test_store_route(self):
        store_route("Mountain View, CA", "San Francisco, CA", "55 miles", "1 hour", "<html>Map content</html>")
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM routes WHERE start_location='Mountain View, CA'")
        rows = cur.fetchall()
        self.assertEqual(len(rows), 1)
        conn.close()

if __name__ == '__main__':
    unittest.main()
