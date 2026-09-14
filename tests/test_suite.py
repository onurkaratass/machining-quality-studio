import unittest
import numpy as np
from core import (
    calculate_iso_fit, FitType,
    calculate_milling, calculate_turning,
    SPCEngine, CapabilityStatus,
    CostEngine, SurfaceRoughnessEngine, ThreadEngine, GCodeSimulator
)


class TestMachiningSuite(unittest.TestCase):

    def test_iso_fits_clearance(self):
        fit = calculate_iso_fit(30.0, "H7", "g6")
        self.assertEqual(fit.fit_type, FitType.CLEARANCE)
        self.assertAlmostEqual(fit.hole_min, 30.000, places=3)
        self.assertAlmostEqual(fit.hole_max, 30.021, places=3)
        self.assertAlmostEqual(fit.shaft_max, 29.993, places=3)
        self.assertAlmostEqual(fit.shaft_min, 29.980, places=3)

    def test_milling_calculation(self):
        res = calculate_milling(diameter=50.0, teeth_z=4, cutting_speed_vc=180.0, feed_per_tooth_fz=0.15, depth_ap=2.0, width_ae=35.0)
        self.assertGreater(res.rpm, 1000)
        self.assertGreater(res.power_kw, 1.0)

    def test_spc_engine(self):
        data = [20.00, 20.01, 19.99, 20.02, 19.98, 20.00]
        res = SPCEngine.analyze(data, nominal=20.00, usl=20.05, lsl=19.95)
        self.assertAlmostEqual(res.mean, 20.00, places=2)
        self.assertGreater(res.cp, 1.0)

    def test_cost_engine(self):
        c = CostEngine.calculate("Test", 50, 100, 7.85, 50, 5, 800, 20, 30, 350, 50, 25)
        self.assertGreater(c.weight_kg, 1.0)
        self.assertGreater(c.final_unit_price, c.base_unit_cost)
        self.assertAlmostEqual(c.total_batch_price, c.final_unit_price * 50, places=1)

    def test_surface_roughness_engine(self):
        s = SurfaceRoughnessEngine.calculate(0.15, 0.8, 1.6)
        self.assertAlmostEqual(s.ra_um, 0.88, places=1)
        self.assertGreater(s.max_feed_for_target_ra, 0.1)

    def test_thread_engine(self):
        th = ThreadEngine.get_thread("M8")
        self.assertEqual(th.pitch_mm, 1.25)
        self.assertEqual(th.drill_dia_mm, 6.8)

    def test_gcode_simulator(self):
        sim = GCodeSimulator(x_limits=(-100, 100), y_limits=(-100, 100), z_limits=(-50, 50))
        code = "G21 G90\nS1000 M03\nG00 X0 Y0 Z10.\nG01 X150. F500\nM30"
        res = sim.analyze(code)
        self.assertEqual(len(res.errors), 1)
        self.assertIn("AŞTI", res.errors[0])


if __name__ == "__main__":
    unittest.main()
