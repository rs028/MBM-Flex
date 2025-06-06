import unittest
from multiroom_model.inchem import InChemPyInstance


class TestInChemPyMainMethod(unittest.TestCase):
    def test_inchempy_runs(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    def test_inchempy_runs_with_chem_mech_set(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/mcm_v331.fac",
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    def test_inchempy_runs_with_escs_v1_set(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/escs_v1.fac",
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    def test_inchempy_runs_with_rcs_2023_set(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/rcs_2023.fac",
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    def test_inchempy_runs_with_mcm_subset_set(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/mcm_subset.fac",
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    
    def test_inchempy_runs_with_chem_mech_set_and_additions(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/mcm_v331.fac",
            particles=True,
            INCHEM_additional=True,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    def test_inchempy_runs_with_escs_v1_set_and_additions(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/escs_v1.fac",
            particles=True,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    def test_inchempy_runs_with_rcs_2023_set_and_additions(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/rcs_2023.fac",
            particles=True,
            INCHEM_additional=True,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    def test_inchempy_runs_with_mcm_subset_set_and_additions(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/mcm_subset.fac",
            particles=True,
            INCHEM_additional=True,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()


if __name__ == '__main__':
    unittest.main()
