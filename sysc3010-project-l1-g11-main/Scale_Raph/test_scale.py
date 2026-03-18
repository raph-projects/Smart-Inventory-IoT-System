import unittest
from unittest.mock import MagicMock
from loadcell import calibrate_scale, count_objects

class TestScaleFunctions(unittest.TestCase):

    def test_calibrate_scale_sets_correct_ratio(self):
        mock_hx = MagicMock()
        mock_hx.get_data_mean.return_value = 20000
        known_weight = 100.0

        ratio = calibrate_scale(mock_hx, known_weight)

        self.assertEqual(ratio, 200.0)
        mock_hx.set_scale_ratio.assert_called_with(200.0)

    def test_count_objects_correctly_counts(self):
        total_weight = 345.0
        single_object_weight = 57.5

        count = count_objects(total_weight, single_object_weight)

        self.assertEqual(count, 6)

    def test_count_objects_handles_invalid_object_weight(self):
        total_weight = 100.0
        
        # Zero weight
        count_zero = count_objects(total_weight, 0.0)
        self.assertEqual(count_zero, 0)

        # Negative weight
        count_negative = count_objects(total_weight, -50.0)
        self.assertEqual(count_negative, 0)

if __name__ == '__main__':
    unittest.main()
