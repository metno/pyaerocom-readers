import unittest
import os

import numpy as np
import pyaro
import pyaro.timeseries
from pyaro.timeseries.Wrappers import VariableNameChangingReader


class TestCSVTimeSeriesReader(unittest.TestCase):
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'testdata', 'csvReader_testdata.csv')
    def test_init(self):
        engine = pyaro.list_timeseries_engines()['csv_timeseries']
        self.assertEqual(engine.url(), "https://github.com/metno/pyaro")
        # just see that it doesn't fails
        engine.description()
        engine.args()
        with engine.open(self.file, filters=[]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(count, 208)
            self.assertEqual(len(ts.stations()), 2)

    def test_stationfilter(self):
        engine = pyaro.list_timeseries_engines()['csv_timeseries']
        sfilter = pyaro.timeseries.filters.get('stations', exclude=['station1'])
        with engine.open(self.file, filters=[sfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(count, 104)
            self.assertEqual(len(ts.stations()), 1)

    def test_boundingboxfilter_exception(self):
        with self.assertRaises(Exception): #pyaro.timeseries.Filter.BoundingBoxException
            pyaro.timeseries.filters.get('bounding_boxes', include=[(-90,0,90,180)])

    def test_boundingboxfilter(self):
        engine = pyaro.list_timeseries_engines()['csv_timeseries']
        sfilter = pyaro.timeseries.filters.get('bounding_boxes',
                                               include=[(90,180,-90,0)])
        self.assertEqual(sfilter.init_kwargs()['include'][0][3], 0)
        with engine.open(self.file, filters=[sfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 1)
            self.assertEqual(count, 104)
        sfilter = pyaro.timeseries.filters.get('bounding_boxes',
                                               exclude=[(90,0,-90,-180)])
        self.assertEqual(sfilter.init_kwargs()['exclude'][0][3], -180)
        with engine.open(self.file, filters=[sfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 1)
            self.assertEqual(count, 104)


    def test_wrappers(self):
        engine = pyaro.list_timeseries_engines()['csv_timeseries']
        newsox = 'oxidised_sulphur'
        with VariableNameChangingReader(engine.open(self.file, filters=[]),
                                        {'SOx': newsox}) as ts:
            self.assertEqual(ts.data(newsox).variable, newsox)
        pass

    def test_variables_filter(self):
        engine = pyaro.list_timeseries_engines()['csv_timeseries']
        newsox = 'oxidised_sulphur'
        vfilter = pyaro.timeseries.filters.get('variables', reader_to_new={'SOx': newsox})
        with engine.open(self.file, filters=[vfilter]) as ts:
            self.assertEqual(ts.data(newsox).variable, newsox)
        pass

if __name__ == "__main__":
    unittest.main()
