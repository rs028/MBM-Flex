import unittest
from multiroom_model.inchem import InChemPyInstance


class TestInChemPy(unittest.TestCase):
    def test_inchempy_runs(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()


if __name__ == '__main__':
    unittest.main()
