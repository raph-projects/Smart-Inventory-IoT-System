import unittest
from server import app, db
from tinydb import Query

class TestObjectDetection(unittest.TestCase):
    def setUp(self):
        """Set up a clean database before each test"""
        db.purge()  # Clear TinyDB
        self.app = app.test_client()

    def test_object_detection(self):
        """Test if object detection works correctly"""
        print("\n🧪 Test 1: Object Detection Logic")
        
        # Case 1: Object within range
        response = self.app.post('/update', json={"distance": 30})
        data = response.get_json()
        expected = True
        actual = data["detected"]
        print(f" - Expected: {expected}, Actual: {actual}")
        self.assertEqual(actual, expected)

        # Case 2: Object out of range
        response = self.app.post('/update', json={"distance": 60})
        data = response.get_json()
        expected = False
        actual = data["detected"]
        print(f" - Expected: {expected}, Actual: {actual}")
        self.assertEqual(actual, expected)

        print("✅ Test 1 Passed: Object detection works correctly.")

    def test_database_storage(self):
        """Test if distance data is stored and retrievable"""
        print("\n🧪 Test 2: Database Storage")

        # Add a distance entry
        self.app.post('/update', json={"distance": 25})

        # Retrieve the latest entry
        response = self.app.get('/latest')
        data = response.get_json()

        expected_distance = 25
        expected_detected = True
        actual_distance = data["distance"]
        actual_detected = data["detected"]

        print(f" - Expected Distance: {expected_distance}, Actual Distance: {actual_distance}")
        print(f" - Expected Detected: {expected_detected}, Actual Detected: {actual_detected}")

        self.assertEqual(actual_distance, expected_distance)
        self.assertEqual(actual_detected, expected_detected)

        print("✅ Test 2 Passed: Database stores and retrieves distance correctly.")

if __name__ == '__main__':
    unittest.main()
