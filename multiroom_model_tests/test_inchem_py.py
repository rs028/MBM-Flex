import unittest
from multiroom_model.inchem import InChemPyInstance
from inchempy import modules

class TestInChemPy(unittest.TestCase):
    def test_inchempy_runs(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance()

        inchem_py_instance.run()



if __name__ == '__main__':
    unittest.main()
