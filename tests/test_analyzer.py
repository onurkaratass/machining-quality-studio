"""
tests.test_analyzer
~~~~~~~~~~~~~~~~~~~
spc.analyzer ve spc.reporter birim testleri.
"""

import unittest
import numpy as np

from spc import CapabilityAnalyzer, CapabilityStatus, ProcessReporter


class TestCapabilityAnalyzer(unittest.TestCase):

    def setUp(self):
        self.nominal = 20.00
        self.usl = 20.06
        self.lsl = 19.94
        self.analyzer = CapabilityAnalyzer(self.nominal, self.usl, self.lsl)

    def test_perfectly_centered_process(self):
        # 6 sigma = 0.12 => sigma = 0.02 => Cp = 0.12 / (6 * 0.02) = 1.00
        data = [19.96, 19.98, 20.00, 20.00, 20.02, 20.04]
        result = self.analyzer.analyze(data)

        self.assertAlmostEqual(result.mean, 20.00, places=4)
        self.assertAlmostEqual(result.cp, result.cpk, places=2)
        self.assertAlmostEqual(result.mean_deviation, 0.0, places=4)
        self.assertAlmostEqual(result.centering_ratio_k, 0.0, places=2)

    def test_offset_process(self):
        # Shifted towards USL
        data = [20.02, 20.03, 20.04, 20.05, 20.05]
        result = self.analyzer.analyze(data)

        self.assertGreater(result.mean, self.nominal)
        self.assertGreater(result.cp, result.cpk)
        self.assertGreater(result.centering_ratio_k, 0.0)

    def test_invalid_limits(self):
        with self.assertRaises(ValueError):
            CapabilityAnalyzer(nominal=20.0, usl=19.0, lsl=21.0)

    def test_nominal_out_of_bounds(self):
        with self.assertRaises(ValueError):
            CapabilityAnalyzer(nominal=25.0, usl=20.0, lsl=19.0)

    def test_insufficient_data(self):
        with self.assertRaises(ValueError):
            self.analyzer.analyze([20.01])

    def test_zero_variance(self):
        with self.assertRaises(ValueError):
            self.analyzer.analyze([20.00, 20.00, 20.00])

    def test_reporter_output(self):
        data = [19.98, 20.00, 20.01, 20.02, 19.99]
        result = self.analyzer.analyze(data)
        report = ProcessReporter.generate_report(result, part_name="Test Parça")

        self.assertIn("İSTATİSTİKSEL PROSES KONTROL", report)
        self.assertIn("Cp", report)
        self.assertIn("Cpk", report)
        self.assertIn("Test Parça", report)


if __name__ == "__main__":
    unittest.main()
