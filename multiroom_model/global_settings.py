class GlobalSettings:
    """
         @brief Stores data needed for inchempy which does not differ between the rooms
    """
    def __init__(
        self,
        filename: str = 'chem_mech/mcm_subset.fac',
        INCHEM_additional: bool = False,
        particles: bool = False,
        constrained_file: str = None,
        output_folder: str = None,
        dt: float = 0.002,
        H2O2_dep: bool = False,
        O3_dep: bool = False,
        custom: bool = False,
        custom_filename: str = None,
        diurnal: bool = False,
        city: str = 'London_urban',
        date: str = '21-06-2020',
        lat: float = 45.4,
        path: str = None,
        reactions_output: bool = False,
        air_density: float = 0.0,
        upwind_pressure_coefficient:float = 0.3, 
        downwind_pressure_coefficient: float = -0.2
    ):
        """
        @param filename: Input FACSIMILE format filename.
        @param particles: Boolean flag to include particle modeling.
        @param INCHEM_additional: Include additional INCHEM reactions not in the MCM download.
        @param custom: Include custom reactions.
        @param custom_filename: Filename for custom reaction input.
        @param diurnal: Enable diurnal variation of outdoor concentrations.
        @param city: City for outdoor concentration profiles.
        @param date: Simulation date in format "DD-MM-YYYY".
        @param lat: Latitude of the simulation location.
        @param H2O2_dep: Enable surface deposition for H2O2.
        @param O3_dep: Enable surface deposition for O3.
        @param constrained_file: CSV file to constrain species or rates over time.
        @param dt: Time step for integration (seconds).
        @param reactions_output: Save detailed reaction rates and constants.
    """
        self.filename = filename
        self.INCHEM_additional = INCHEM_additional
        self.particles = particles
        self.constrained_file = constrained_file
        self.output_folder = output_folder
        self.dt = dt
        self.H2O2_dep = H2O2_dep
        self.O3_dep = O3_dep
        self.custom = custom
        self.custom_filename = custom_filename
        self.diurnal = diurnal
        self.city = city
        self.date = date
        self.lat = lat
        self.path = path
        self.reactions_output = reactions_output
        self.air_density = air_density
        self.upwind_pressure_coefficient = upwind_pressure_coefficient
        self.downwind_pressure_coefficient = downwind_pressure_coefficient
