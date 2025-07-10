class GlobalSettings:
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
        reactions_output: bool = False
    ):
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

