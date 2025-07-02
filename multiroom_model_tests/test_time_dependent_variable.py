import unittest
from multiroom_model.time_dep_value import TimeDependentValue


class TestTimeDependentValueLinearInterpolation(unittest.TestCase):
    def setUp(self):
        self.data = [
            (0.0, 0.0),
            (1.0, 10.0),
            (2.0, 20.0),
            (3.0, 30.0),
        ]
        self.tdv = TimeDependentValue(self.data)

    def test_times(self):
        self.assertEqual(self.tdv.times(), [0.0, 1.0, 2.0, 3.0])

    def test_values(self):
        self.assertEqual(self.tdv.values(), [0.0, 10.0, 20.0, 30.0])

    def test_value_at_exact_times(self):
        self.assertAlmostEqual(self.tdv.value_at_time(0.0), 0.0)
        self.assertAlmostEqual(self.tdv.value_at_time(1.0), 10.0)
        self.assertAlmostEqual(self.tdv.value_at_time(3.0), 30.0)

    def test_value_at_in_between_times(self):
        self.assertAlmostEqual(self.tdv.value_at_time(0.5), 5.0)
        self.assertAlmostEqual(self.tdv.value_at_time(1.5), 15.0)
        self.assertAlmostEqual(self.tdv.value_at_time(2.5), 25.0)

    def test_value_before_first_time_raises(self):
        with self.assertRaises(Exception) as context:
            self.tdv.value_at_time(-1.0)
        self.assertIn("too early", str(context.exception).lower())

    def test_value_after_last_time_raises(self):
        with self.assertRaises(Exception) as context:
            self.tdv.value_at_time(3.1)
        self.assertIn("too late", str(context.exception).lower())

    def test_invalid_time_order_raises(self):
        with self.assertRaises(Exception) as context:
            TimeDependentValue([(1.0, 10.0), (0.5, 20.0)])
        self.assertIn("times were not in order", str(context.exception).lower())

    def test_single_point(self):
        tdv_single = TimeDependentValue([(2.0, 100.0)])
        self.assertEqual(tdv_single.value_at_time(2.0), 100.0)
        with self.assertRaises(Exception):
            tdv_single.value_at_time(1.9)
        with self.assertRaises(Exception):
            tdv_single.value_at_time(2.1)


if __name__ == '__main__':
    unittest.main()
