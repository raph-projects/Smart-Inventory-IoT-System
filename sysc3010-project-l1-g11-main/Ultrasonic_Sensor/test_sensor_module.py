import unittest
from unittest.mock import patch
from ultrasonic import measure_distance

class TestSensorMeasurement(unittest.TestCase):

    @patch('ultrasonic.GPIO')
    @patch('ultrasonic.time')
    def test_normal_distance_measurement(self, mock_time, mock_gpio):
        mock_gpio.input.side_effect = [0, 1, 1, 0]
        mock_time.time.side_effect = [0.0, 0.00001, 0.0001, 0.0002]

        distance = measure_distance()
        expected = ((0.0001 - 0.00001) * 34300) / 2
        assert round(distance, 2) == round(expected, 2)

    @patch('ultrasonic.GPIO')
    @patch('ultrasonic.time')
    def test_timeout_waiting_for_echo_high(self, mock_time, mock_gpio):
        mock_gpio.input.return_value = 0
        mock_time.time.side_effect = [0.0, 0.03]

        distance = measure_distance()
        assert distance is None

    @patch('ultrasonic.GPIO')
    @patch('ultrasonic.time')
    def test_timeout_waiting_for_echo_low(self, mock_time, mock_gpio):
        mock_gpio.input.side_effect = [0, 1, 1, 1]
        mock_time.time.side_effect = [0.0, 0.00001, 0.03]

        distance = measure_distance()
        assert distance is None

if __name__ == '__main__':
    unittest.main()
