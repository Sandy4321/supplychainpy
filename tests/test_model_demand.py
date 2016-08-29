import os
from unittest import TestCase

from supplychainpy import data_cleansing
from supplychainpy.model_demand import simple_exponential_smoothing_forecast_from_file, \
    holts_trend_corrected_exponential_smoothing_forecast_from_file, holts_trend_corrected_exponential_smoothing_forecast


class TestModelDemand(TestCase):
    def setUp(self):
        self._data_set = {'jan': 25, 'feb': 25, 'mar': 25, 'apr': 25, 'may': 25, 'jun': 25, 'jul': 75,
                          'aug': 75, 'sep': 75, 'oct': 75, 'nov': 75, 'dec': 75}

        self._orders = [165, 171, 147, 143, 164, 160, 152, 150, 159, 169, 173, 203, 169, 166, 162, 147, 188, 161, 162,
                        169, 185, 188, 200, 229, 189, 218, 185, 199, 210, 193, 211, 208, 216, 218, 264, 304]

        self.app_dir = os.path.dirname(__file__, )
        self.rel_path = 'supplychainpy/data2.csv'
        self.abs_file_path = os.path.abspath(os.path.join(self.app_dir, '..', self.rel_path))
        self.file_type = 'csv'

        with open(self.abs_file_path, 'r') as raw_data:
            self.item_list = data_cleansing.clean_orders_data_row_csv(raw_data, length=12)
        self.sku_id = []

        for sku in self.item_list:
            self.sku_id.append(sku.get("sku id"))

        self.ses_forecast = [i for i in
                             simple_exponential_smoothing_forecast_from_file(file_path=self.abs_file_path,
                                                                             file_type='csv',
                                                                             length=12,
                                                                             smoothing_level_constant=0.5,
                                                                             optimise=True)]
        self.keys = [list(i.keys()) for i in self.ses_forecast]
        self.unpack_keys = [i[0] for i in self.keys]

        self.htces_forecast = [i for i in
                               holts_trend_corrected_exponential_smoothing_forecast_from_file(
                                   file_path=self.abs_file_path,
                                   file_type='csv',
                                   length=12,
                                   alpha=0.5,
                                   gamma=0.5,
                                   smoothing_level_constant=0.5,
                                   optimise=True)]

        self.keys = [list(i.keys()) for i in self.htces_forecast]
        self.unpack_keys_htces = [i[0] for i in self.keys]

    def test_simple_exponential_smoothing_forecast(self):
        """ Tests every sku listed in file, is processed for forecast """
        for key in self.sku_id:
            self.assertIn(key, self.unpack_keys)

    def test_simple_exponential_smoothing_forecast_trend(self):
        trending = [list(i.values()) for i in self.ses_forecast]
        unpack_trending = [i[0] for i in trending]
        stats = []
        for i in unpack_trending:
            stats.append(i.get('statistics'))
        for stat in stats:
            if stat.get('trend'):
                self.assertTrue(stat.get('pvalue') < 0.05)

    def test_holts_trend_corrected_exponential_smoothing_keys(self):
        for key in self.sku_id:
            self.assertIn(key, self.unpack_keys_htces)

    def test_holts_trend_corrected_exponential_smoothing(self):
        holts_trend_corrected_esf = holts_trend_corrected_exponential_smoothing_forecast(demand=self._orders,
                                                                                         alpha=0.5,
                                                                                         gamma=0.5,
                                                                                         forecast_length=6,
                                                                                         initial_period=18)

        self.assertEqual(281, round(holts_trend_corrected_esf.get('forecast')[0]))
        self.assertEqual(308, round(holts_trend_corrected_esf.get('forecast')[1]))
        self.assertEqual(334, round(holts_trend_corrected_esf.get('forecast')[2]))

    def test_holts_evo_optised_alpha_gamma(self):

        holts_trend_corrected_esf = holts_trend_corrected_exponential_smoothing_forecast(demand=self._orders,
                                                                                         alpha=0.5,
                                                                                         gamma=0.5,
                                                                                         forecast_length=6,
                                                                                         initial_period=18,
                                                                                         optimise=True)

        self.assertAlmostEqual(0.66, float('{:.2f}'.format(holts_trend_corrected_esf.get('optimal_alpha'))), delta=1.3)
        self.assertAlmostEqual(0.05, holts_trend_corrected_esf.get('optimal_gamma'), delta=0.08)
