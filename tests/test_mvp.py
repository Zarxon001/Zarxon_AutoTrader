import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from zarxon_autotrader.market import load_csv
from zarxon_autotrader.strategy import Config, signal

ROOT = Path(__file__).resolve().parent.parent


class MVPTests(unittest.TestCase):
    def setUp(self):
        self.candles = load_csv(ROOT / 'data' / 'demo.csv')

    def csv_error(self, transform):
        text = (ROOT / 'data' / 'demo.csv').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.csv'
            path.write_text(transform(text), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_csv(path)

    def test_buy_cross_and_known_levels(self):
        result = signal(self.candles)
        self.assertEqual((result['direction'], result['entry'], result['sl'], result['tp']),
                         ('BUY', '4105.00', '4063.95', '4187.10'))
        self.assertEqual(Decimal(result['reward_ratio']), 2)

    def test_mirrored_prices_produce_sell_and_correct_level_order(self):
        mirrored = [replace(c, open=8200-c.open, high=8200-c.low,
                            low=8200-c.high, close=8200-c.close) for c in self.candles]
        result = signal(mirrored)
        self.assertEqual(result['direction'], 'SELL')
        self.assertLess(Decimal(result['tp']), Decimal(result['entry']))
        self.assertLess(Decimal(result['entry']), Decimal(result['sl']))

    def test_no_cross_has_no_levels(self):
        flat = [replace(c, close=Decimal(4100)) for c in self.candles]
        result = signal(flat)
        self.assertEqual(result['direction'], 'HOLD')
        self.assertTrue(all(result[key] is None for key in ('entry', 'sl', 'tp')))

    def test_existing_trend_is_not_a_new_cross(self):
        rising = [replace(c, close=Decimal(4100+i)) for i, c in enumerate(self.candles)]
        self.assertEqual(signal(rising)['direction'], 'HOLD')

    def test_not_enough_history(self):
        with self.assertRaises(ValueError):
            signal(self.candles[:5])

    def test_bad_configs(self):
        for config in (Config(short=5, long=3), Config(stop_percent=Decimal('NaN')),
                       Config(reward_ratio=Decimal('-1')), Config(decimals=-1)):
            with self.subTest(config=config), self.assertRaises(ValueError):
                signal(self.candles, config)

    def test_invalid_ohlc_and_nonfinite_values(self):
        self.csv_error(lambda s: s.replace('4100,4101,4099,4100', '4100,4090,4099,4100', 1))
        self.csv_error(lambda s: s.replace('4100,4101', 'NaN,4101', 1))
        self.csv_error(lambda s: s.replace('4100,4101', '-1,4101', 1))

    def test_time_must_be_ordered_and_zoned(self):
        self.csv_error(lambda s: s.replace('00:05:00Z', '00:00:00Z'))
        self.csv_error(lambda s: s.replace('00:00:00Z', '00:00:00'))

    def test_volume_and_missing_columns(self):
        self.csv_error(lambda s: s.replace(',10\n', ',-1\n', 1))
        self.csv_error(lambda s: s.replace(',volume', ',amount'))

    def test_zero_rounded_stop_fails(self):
        with self.assertRaises(ValueError):
            signal(self.candles, Config(stop_percent=Decimal('0.00000001')))

    def test_cli_json_is_demo_and_disabled(self):
        run = subprocess.run([sys.executable, '-m', 'zarxon_autotrader', '--json'],
                             cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertTrue(result['demo_only'])
        self.assertEqual(result['execution'], 'disabled')

    def test_cli_invalid_input_exits_without_signal(self):
        run = subprocess.run([sys.executable, '-m', 'zarxon_autotrader', '--stop-percent', 'NaN'],
                             cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, '')


if __name__ == '__main__':
    unittest.main()
