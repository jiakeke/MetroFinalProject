import sys
import sys

sys.path.append("..")

import unittest
import unittest.mock as mock
from MetroFinalProject.pilot import get_weather_index
from MetroFinalProject.pilot import calculate_carbon_emission
from MetroFinalProject.pilot import calculate_flight_reward
from MetroFinalProject.pilot import get_map




class SayHelloTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_weather_index(self):
        global index
        index = -1
        def mock_random():
            numbers = [
                0.2,
                0.8, 0.8,
                0.5, 0.5, 0.05,
                0.5, 0.5, 0.1,
                0.5, 0.5, 0.15]
            global index
            index += 1
            num = numbers[index]
            print(index, num)
            return num
        self.assertEqual(get_weather_index('tutorial'), ('Normal', 1.0))

        with mock.patch('random.random', mock_random):
            self.assertEqual(get_weather_index(60), ('Great', 0.9))
            self.assertEqual(get_weather_index(60), ('Heavy Rain', 1.1))
            self.assertEqual(get_weather_index(60), ('Blizzard', 1.3))
            self.assertEqual(get_weather_index(40), ('Snow', 1.2))
            self.assertEqual(get_weather_index(30), ('Thunderstorm', 1.2))

    def test_calculate_carbon_emission(self):
        self.assertEqual(calculate_carbon_emission(100), 100*0.275)
        self.assertEqual(calculate_carbon_emission(500), 55+0.105*(500-200))
        self.assertEqual(calculate_carbon_emission(2000), 2000*0.139)


    def test_calculate_flight_reward(self):
        with mock.patch('random.randint', lambda x, y: 100):
            self.assertEqual(calculate_flight_reward(100), 785)

    def test_get_map(self):
        mock_task = mock.Mock()
        mock_task.departure = mock.Mock()
        mock_task.departure.longitude_deg = 30
        mock_task.departure.latitude_deg = 60
        mock_task.departure.name = 'A'
        mock_task.destination = mock.Mock()
        mock_task.destination.longitude_deg = 40
        mock_task.destination.latitude_deg = 70
        mock_task.destination.name = 'B'

        mock_geo = mock.Mock()
        mock_geo.kilometers = 1206.9527730857637
        res = (
            'https://maps.geoapify.com/v1/staticmap?apiKey=b73b796d6f574a5ab1'
            'bd25c3b777dd5d&style=klokantech-basic&width=1024&height=768&cent'
            'er=lonlat:35.0,65.0&zoom=4.262846489425556&marker=lonlat:30,60;'
            'text:A;color:%23ff0000;size:large;textsize:small|lonlat:40,70;'
            'text:B;color:%23ff0000;size:large;textsize:small',
        (375, 589), (649, 179),
        mock_task.departure.name,
        mock_task.destination.name,
        )
        with mock.patch('pilot.geodesic', mock_geo):
            self.assertEqual(get_map(mock_task), res)


if __name__ == '__main__':
    unittest.main()
