import unittest
from modules.inchem_main_class import InChemPyMainClass
from multiroom_model.inchem import generate_main_class, run_main_class


class TestInChemPyMainCass(unittest.TestCase):

    def test_inchempy_runs(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            particles=False,
            INCHEM_additional=False)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_runs_with_chem_mech_set(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            filename="chem_mech/mcm_v331.fac",
            particles=False,
            INCHEM_additional=False)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_runs_with_escs_v1_set(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            filename="chem_mech/escs_v1.fac",
            particles=False,
            INCHEM_additional=False)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_runs_with_rcs_2023_set(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            filename="chem_mech/rcs_2023.fac",
            particles=False,
            INCHEM_additional=False)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_runs_with_mcm_subset_set(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            filename="chem_mech/mcm_subset.fac",
            particles=False,
            INCHEM_additional=False)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_runs_with_chem_mech_set_and_additions(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            filename="chem_mech/mcm_v331.fac",
            particles=True,
            INCHEM_additional=True)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_runs_with_escs_v1_set_and_additions(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            filename="chem_mech/escs_v1.fac",
            particles=True,
            INCHEM_additional=False)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_runs_with_rcs_2023_set_and_additions(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            filename="chem_mech/rcs_2023.fac",
            particles=True,
            INCHEM_additional=True)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_runs_with_mcm_subset_set_and_additions(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            filename="chem_mech/mcm_subset.fac",
            particles=True,
            INCHEM_additional=True)

        run_main_class(inchem_main_class, initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

    def test_inchempy_run_in_2_phases(self):
        inchem_main_class: InChemPyMainClass = generate_main_class(
            particles=False,
            INCHEM_additional=False)

        phase_1_output_concentrations, phase_1_times = run_main_class(inchem_main_class,
                                                                      initial_conditions_gas='initial_concentrations.txt', 
                                                                      seconds_to_integrate=180)

        output_concentrations, phase_2_times = run_main_class(inchem_main_class,
                                                              initials_from_run=True, 
                                                              initial_dataframe=phase_1_output_concentrations, 
                                                              t0=180, 
                                                              seconds_to_integrate=180)

        self.assertEqual(4, len(phase_1_output_concentrations))
        self.assertEqual(4, len(output_concentrations))

        for species in inchem_main_class.species:
            self.assertEqual(phase_1_output_concentrations.get(species)[180.0],
                             output_concentrations.get(species)[180.0], f"species check failed: {species}")


if __name__ == '__main__':
    unittest.main()
