# -*- coding: utf-8 -*-
"""
User set variable input file for INCHEM-Py.
A detailed description of this file can be found within the user manual.

Copyright (C) 2019-2021
David Shaw : david.shaw@york.ac.uk
Nicola Carslaw : nicola.carslaw@york.ac.uk

All rights reserved.

This file is part of INCHEM-Py.

INCHEM-Py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

INCHEM-Py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with INCHEM-Py.  If not, see <https://www.gnu.org/licenses/>.
"""

# Import modules
import os
import datetime
from pandas import read_csv
from math import ceil
#import shutil
#import sys

# =============================================================================================== #

# Basic model settings
filename = 'mcm_v331.fac'   # Chemical mechanism file in FACSIMILE format

particles = False   # set to True if particles are included

INCHEM_additional = True   # set to True to include the additional INCHEM mechanism

custom = False   # Custom reactions that are not in the MCM or in the INCHEM mechanism
                 # The format of this file is described in `custom_input.txt`

diurnal = True   # Diurnal outdoor concentrations. Boolean

city = "Bergen_urban"   # Source city of outdoor concentrations of O3, NO, NO2, and PM2.5
                        # Options are "London_urban", "London_suburban" or "Bergen_urban"
                        # Changes to outdoor concentrations can be done in outdoor_concentrations.py
                        # See the INCHEM-Py manual for details of sources and fits

date = "21-06-2020"   # Day of simulation in format "DD-MM-YYYY"
lat = 45.4   # Latitude of simulation location

# =============================================================================================== #
# Integration settings and time control

dt = 150     # Time between outputs (s), simulation may fail if this is too large
             # also used as max_step for the scipy.integrate.ode integrator
t0 = 0       # time of day, in seconds from midnight, to start the simulation

total_seconds_to_integrate = 4800   # how long to run the model in seconds (86400*3 will run 3 days)

end_of_total_integration = t0+total_seconds_to_integrate

 # Set length of chemistry-only integrations between simple treatments of transport (assumed separable)
tchem_only = 600     # NB: MUST BE < 3600 SECONDS

# Calculate nearest whole number of chemistry-only integrations, approximating seconds_to_integrate
nchem_only = round(total_seconds_to_integrate/tchem_only)

if nchem_only == 0:
    nchem_only = 1

# print('total_seconds_to_integrate set to',total_seconds_to_integrate)
# print('tchem_only set to',tchem_only)
# print('nchem_only therefore set to',nchem_only)

seconds_to_integrate = tchem_only
# print('seconds_to_integrate set to',seconds_to_integrate)

# =============================================================================================== #

# INPUT DATA: physical characteristics of the rooms
#
# Room parameters that do not change with time: `mr_tcon_room_params.csv`
# - number of rooms
# - volume of each room
# - surface area in each room
# - type of light in each room
# - type of glass (windows) in each room
# - types of surface in each room (as percent coverage)
tcon_params = read_csv("config/mr_tcon_room_params.csv")

nroom = len(tcon_params['room_number']) # number of rooms (each room treated as one box)

mrvol = tcon_params['volume_in_m3'].tolist()
mrsurfa = tcon_params['surf_area_in_m2'].tolist()
mrlightt = tcon_params['light_type'].tolist()
mrglasst = tcon_params['glass_type'].tolist()

# TODO : need input from Dave
# mrsoft = tcon_params['percent_soft'].tolist()
# mrpaint = tcon_params['percent_paint'].tolist()
# mrwood = tcon_params['percent_wood'].tolist()
# mrmetal = tcon_params['percent_metal'].tolist()
# mrconcrete = tcon_params['percent_concrete'].tolist()
# mrpaper = tcon_params['percent_paper'].tolist()
# mrplastic = tcon_params['percent_plastic'].tolist()
# mrglass = tcon_params['percent_glass'].tolist()
# mrlino = tcon_params['percent_lino'].tolist()

# =============================================================================================== #

# INPUT DATA: physical and chemical variables of the rooms
#
# Room parameters that change with time and emissions of chemical species
all_mrtemplist = []
all_mrrh = []
all_mrpres = []
all_mracrate = []
all_mrlswitch = []

all_mradults = []
all_mrchildren = []

all_mremis = {}
all_timemis = []

for iroom in range(0, nroom):

    # physical parameters of each room variable with time: `mr_tvar_room_params_*.csv`
    # - temperature (K)
    # - relative humidity (%)
    # - pressure (Pa)
    # - outdoor/indoor change rate (s^-1)
    # - light switch (on/off)
    tvar_params = read_csv("config/mr_tvar_room_params_"+str(iroom+1)+".csv")

    secsfrommn = tvar_params['seconds_from_midnight'].tolist()
    mrtemp = tvar_params['temp_in_kelvin'].tolist()
    mrrh = tvar_params['rh_in_percent'].tolist()
    mrpres = tvar_params['pressure_in_pascal'].tolist()
    mracrate = tvar_params['airchange_in_per_second'].tolist()
    mrlswitch = tvar_params['light_switch'].tolist()

    mrtemplist = list(zip(secsfrommn,mrtemp))
    #print(mrtemplist)

    all_mrtemplist.append(mrtemplist)
    all_mrrh.append(mrrh)
    all_mrpres.append(mrpres)
    all_mracrate.append(mracrate)
    all_mrlswitch.append(mrlswitch)
    #print('all_mrtemplist=',all_mrtemplist)

    # people in each room variable with time: `mr_tvar_expos_params_*.csv`
    # - number of adults
    # - number of children
    tvar_params = read_csv("config/mr_tvar_expos_params_"+str(iroom+1)+".csv")

    secsfrommn = tvar_params['seconds_from_midnight'].tolist()
    mradults = tvar_params['n_adults'].tolist()
    mrchildren = tvar_params['n_children'].tolist()

    all_mradults.append(mradults)
    all_mrchildren.append(mrchildren)
    #print('all_mradults=',all_mradults)

    # emissions of chemical species in each room variable with time: `mr_room_emis_params_*.csv`
    #
    # NB: when using timed emissions it's suggested that the start time and end times are
    # divisible by dt and that (start time - end time) is larger then 2*dt to avoid the
    # integrator skipping any emissions over small periods of time.
    mremis_params = read_csv("config/mr_room_emis_params_"+str(iroom+1)+".csv")

    mremis_species = mremis_params['species'].tolist()
    nemis_species = len(mremis_species)

    mremis_tstart1 = mremis_params['tstart1_in_seconds'].tolist()
    mremis_tend1 = mremis_params['tend1_in_seconds'].tolist()
    mremis_emis1 = mremis_params['emis1_in_molcm-3sec-1'].tolist()

    mremis_tstart2 = mremis_params['tstart2_in_seconds'].tolist()
    mremis_tend2 = mremis_params['tend2_in_seconds'].tolist()
    mremis_emis2 = mremis_params['emis2_in_molcm-3sec-1'].tolist()

    mremis_tstart3 = mremis_params['tstart3_in_seconds'].tolist()
    mremis_tend3 = mremis_params['tend3_in_seconds'].tolist()
    mremis_emis3 = mremis_params['emis3_in_molcm-3sec-1'].tolist()

    mremis_tstart4 = mremis_params['tstart4_in_seconds'].tolist()
    mremis_tend4 = mremis_params['tend4_in_seconds'].tolist()
    mremis_emis4 = mremis_params['emis4_in_molcm-3sec-1'].tolist()

    mremis_tstart5 = mremis_params['tstart5_in_seconds'].tolist()
    mremis_tend5 = mremis_params['tend5_in_seconds'].tolist()
    mremis_emis5 = mremis_params['emis5_in_molcm-3sec-1'].tolist()

    mremis_tstart6 = mremis_params['tstart6_in_seconds'].tolist()
    mremis_tend6 = mremis_params['tend6_in_seconds'].tolist()
    mremis_emis6 = mremis_params['emis6_in_molcm-3sec-1'].tolist()

    mremis = {}
    for iemis_species in range(0, nemis_species):
        mremis [mremis_species[iemis_species]] = [mremis_tstart1[iemis_species],mremis_tend1[iemis_species],mremis_emis1[iemis_species]],\
          [mremis_tstart2[iemis_species],mremis_tend2[iemis_species],mremis_emis2[iemis_species]],\
          [mremis_tstart3[iemis_species],mremis_tend3[iemis_species],mremis_emis3[iemis_species]],\
          [mremis_tstart4[iemis_species],mremis_tend4[iemis_species],mremis_emis4[iemis_species]],\
          [mremis_tstart5[iemis_species],mremis_tend5[iemis_species],mremis_emis5[iemis_species]],\
          [mremis_tstart6[iemis_species],mremis_tend6[iemis_species],mremis_emis6[iemis_species]]

    all_mremis[iroom] = mremis
    #print('all_mremis(',iroom,')=',all_mremis[iroom])
    
    # switch emissions off if the csv file for this room is empty
    if len(mremis) == 0: 
        all_timemis.append(False)
    else:
        all_timemis.append(True)

# =============================================================================================== #

# PRIMARY LOOP: run INCHEM-Py in each room for the duration of tchem_only,
# then run the transport module (`mr_transport.py`), reinitialize the model and
# run again until end_of_total_integration
for ichem_only in range (0,nchem_only): # loop over chemistry-only integration periods
    #print('ichem_only=',ichem_only)

    if ichem_only > 0:
        #(1) ADD SIMPLE TREATMENT OF TRANSPORT HERE
        if (__name__ == "__main__") and (nroom >= 2):
            from modules.mr_transport import calc_transport
            #calc_transport(custom_name,ichem_only,tchem_only,nroom,mrvol)

        #(2) Update t0; adjust time of day to start simulation (seconds from midnight),
        #    reflecting splitting total_seconds_to_integrate into nchem_only x tchem_only
        t0 = t0 + tchem_only

    # Determine time index for tvar_params, itvar_params
    # NB: assumes tchem_only < 3600 seconds (time resolution of tvar_params data)
    end_of_tchem_only = t0 + tchem_only
    t0_corrected = t0-((ceil(t0/86400)-1)*86400)
    end_of_tchem_only_corrected = end_of_tchem_only-((ceil(t0/86400)-1)*86400)
    if end_of_tchem_only_corrected <= 86400:
        mid_of_tchem_only = 0.5*(t0_corrected + end_of_tchem_only_corrected)
    else:
        mid_of_tchem_only = (0.5*(t0_corrected + end_of_tchem_only_corrected))-86400
        if mid_of_tchem_only < 0:
            mid_of_tchem_only = mid_of_tchem_only + 86400
    itvar_params = ceil(mid_of_tchem_only/3600)-1
    # print('t0=',t0)
    # print('end_of_tchem_only=',end_of_tchem_only)
    # print('mid_of_tchem_only=',mid_of_tchem_only)
    # print('itvar_params=',itvar_params)

    # ------------------------------------------------------------------------------------------- #

    # SECONDARY LOOP: for each chemistry-only integration period run INCHEM-Py in each room
    # and save the output of the run in a separate directory
    for iroom in range (0,nroom): # loop over rooms
        #print('iroom=',iroom)


        # Set temperature, relative humidity, number density of air (M)
        # from tvar_params data

        # Temperatures are interpolated from a list of given values (`mr_tvar_room_params_*.csv`)
        # using either a 'Linear' or a 'BSpline' interpolation method. The list has the format:
        # [[time (s), temperature (K)],[time (s), temperature (K)], ...]
        # Alternatively, a constant temperature can also be set without interpolation.
        # Details of these methods are given in the INCHEM-Py user manual.
        # Note that in MBM-Flex, temperatures are set as a list of tuples not a list of lists:
        # this shouldn't make a difference unless the code tries to change the temperature.
        spline = 'Linear'  # 'Linear' interpolation, by default
        temperatures = all_mrtemplist[iroom]#[itvar_params] # temperature (Kelvin)
        #print('temperatures=',temperatures)

        rel_humidity = all_mrrh[iroom][itvar_params] # relative humidity (%)
        #print('rel_humidity=',rel_humidity)

        Mfact = (all_mrpres[iroom][itvar_params]/8.3144626)*(6.0221408e23/1e6)
        M = [tuple[1]*Mfact for tuple in temperatures] # number density of air (molecule cm^-3)
        #print('M=',M)

        # place any species you wish to remain constant in the below dictionary. Follow the format
        # const_dict = {
        #     'O2':0.2095*M,
        #     'N2':0.7809*M,
        #     'H2':550e-9*M,
        #     'saero':1.3e-2 # aerosol surface area concentration
        #     }

        #ACRate = all_mracrate[iroom][itvar_params] # air change rate (s^-1)
        #print('ACRate=',ACRate)

        light_type = mrlightt[iroom]
        #print('light_type=',light_type)

        glass = mrglasst[iroom]
        #print('glass=',glass)

        # The surface dictionary exists in surface_dictionary.py in the modules folder.
        # To change any surface deposition rates of individual species, or to add species
        # this file must be edited. Production rates can be added as normal reactions
        # in the custom inputs file. To remove surface deposition AV should be set to 0 and
        # H2O2_dep and O3_dep should be set to False.

        # AV is the surface to volume ratio (cm^-1)
        #AV = 0.02

        # Schemes for deposition of O3 and H2O2 are optionally provided. These schemes
        # provide calculated surface emissions proportional to O3 and H2O2 deposition
        # to different surfaces. The schemes can be turned off or on below.
        # If either scheme is on then AV will be calculated as a sum of the AVs given
        # for the individual surfaces.

        #surfaces_AV = {             # (cm^-1)
        #     'AVSOFT' : 0.0035,      # soft furnishings
        #     'AVPAINT' : 0.0114,     # painted surfaces
        #     'AVWOOD' : 0.0061,      # wood
        #     'AVMETAL' : 0.0025,     # metal
        #     'AVCONCRETE' : 0.0001,  # concrete
        #     'AVPAPER' : 0.0006,     # paper
        #     'AVLINO' : 0.0000,      # linoleum
        #     'AVPLASTIC' : 0.0048,   # plastic
        #     'AVGLASS' : 0.0009,     # glass
        #     'AVHUMAN' : 0.0000}     # humans

        # H2O2_dep = True
        # O3_dep = True

        # '''
        # Breath emissions from humans
        # '''
        # adults = 0     #Number of adults in the room
        # children = 0   #Number of children in the room (10 years old)

#         AV = (mrsurfa[iroom]/mrvol[iroom])/100 #NB Factor of 1/100 converts units from m^-1 to cm^-1
#         print('AV=',AV)

#         lotstr='['
#         for ihour in range (0,24):
#             if (ihour==0 and all_mrlswitch[iroom][ihour]==1) or (ihour>0 and all_mrlswitch[iroom][ihour]==1 and all_mrlswitch[iroom][ihour-1]==0):
#                 lotstr=lotstr+'['+str(ihour)+','
#             if (ihour>0 and all_mrlswitch[iroom][ihour]==0 and all_mrlswitch[iroom][ihour-1]==1):
#                 lotstr=lotstr+str(ihour)+'],'
#             if (ihour==23 and all_mrlswitch[iroom][ihour]==1):
#                 lotstr=lotstr+str(ihour+1)+'],'
#         lotstr=lotstr.strip(",")
#         lotstr=lotstr+']'
#         if end_of_total_integration>86400:
#             lotstr=lotstr.strip("[]")
#             nrep=ceil(end_of_total_integration/86400)
#             lotstr='['+((nrep-1)*('['+lotstr+'],'))+'['+lotstr+']]'
#         print('lotstr=',lotstr)
#         if lotstr=="[]":
#             light_type="off"
#         print('light_type=',light_type)
#         if light_type!="off":
#             light_on_times=eval(lotstr)
#             print('light_on_times=',light_on_times)


#         # Settings re emissions are outside ichem_only and iroom loops
#         # timed_inputs assigned below based on room-specific parameter string constructed above
    #    # the dictionary should be populated as
        # timed_inputs = {species1:[[start time (s), end time (s), rate of increase in (mol/cm^3)/s]],
        #                 species2:[[start time (s), end time (s), rate of increase in (mol/cm^3)/s]]}
        # each species can be emitted in 6 separate intervals with an emission rate in molecule cm^-3 s^-1
        # different chemical species can be emitted in each room
#         """
#         Timed concentrations
#         """
#         timed_inputs = all_mremis [iroom]
#         print('timed_inputs=', timed_inputs)


#         """
#         Output
#         """
#         # An output pickle file is automatically saved so that all data can be recovered
#         # at a later date for analysis.  Applies to folder name and settings file copy name.
#         custom_name = 'Test_20230602_Serial'
#         print('custom_name=',custom_name)

#         # INCHEM-Py calculates the rate constant for each reaction at every time point
#         # Setting reactions_output to True saves all reactions and their assigned constant
#         # to reactions.pickle and adds all calculated reaction rates to the out_data.pickle
#         # file which will increase its size substantially. Surface deposition rates are also
#         # added to the out_data.pickle file for analysis.
#         reactions_output = False

#         # This function purely outputs a graph to the
#         # output folder of a list of selected species and a CSV of concentrations.
#         # If the species do not exist in the run then a key error will cause it to fail
#         output_graph = True #Boolean
#         output_species = ['O3',"O3OUT","tsp"]


#         """
#         Initial concentrations in molecules/cm^3 saved in a text file
#         """
#         #JGL: Moved and updated settings re init concs here

#         if ichem_only == 0:
#             initials_from_run = False #JGL: for first chem-only integration, init concs must be taken from initial_conditions_gas; for now, same file/same concs for all rooms

#             # If initials_from_run is set to False then initial gas conditions must be available
#             # in the file specified by initial_conditions_gas, the inclusion of particles is optional.
#             initial_conditions_gas = 'initial_concentrations.txt'


#             # initial gas concentrations can be taken from a previous run of the model.
#             # Set initials_from_run to True if this is the case and move a previous out_data.pickle
#             # to the main folder and rename to in_data.pickle. The code will then take this
#             # file and extract the concentrations from the time point closest to t0 as
#             # initial conditions.

#             # in_data.pickle must contain all of the species required, including particles if used.

#         else:
#             initials_from_run = True #JGL: for all but the first chem-only integration, init concs taken from previous room-specific output
#             #shutil.copyfile('%s/%s/%s' % (path,output_folder,'out_data.pickle'), '%s/%s' % (path,'in_data_c'+str(ichem_only)+'_r'+str(iroom+1)+'.pickle'))

#         #JGL: Moved assignment of path and output_folder to settings.py and passed these to inchem_main.py

#         '''
#         setting the output folder in current working directory
#         '''
#         path=os.getcwd()
#         now = datetime.datetime.now()
#         #output_folder = ("%s_%s" % (now.strftime("%Y%m%d_%H%M%S"), custom_name))
#         output_folder = ("%s_%s_%s" % (custom_name,'c'+str(ichem_only),'r'+str(iroom+1))) # JGL: Includes chemistry-only integration number and room number)
#         os.mkdir('%s/%s' % (path,output_folder))
#         with open('%s/__init__.py' % output_folder,'w') as f:
#             pass
#         print('Creating folder:', output_folder)

        #print(filename)
        #print(particles)
        #print(INCHEM_additional)
        #print(custom)
        #print(temperatures)
        #print(rel_humidity)
        #print(M)
        #print(const_dict)
        # print(ACRate)
        #print(diurnal)
        #print(city)
        #print(date)
        #print(lat)
        #print(light_type)
        # print(light_on_times)
        #print(glass)
        # print(AV)
        # print(initials_from_run)
        # print(initial_conditions_gas)
        # print(timed_emissions)
        # print(timed_inputs)
        # print(dt)
        # print(t0)
        # print(iroom)
        # print(ichem_only)
        # print(path)
        # print(output_folder)
        # print(seconds_to_integrate)
        # print(custom_name)
        # print(output_graph)
        # print(output_species)
        # print(reactions_output)
        # print(H2O2_dep)
        # print(O3_dep)
        # print(adults)
        # print(children)
        # print(surfaces_AV)
        # print(__file__)
        #print(temperatures)
        #print(spline)
        #print("---------------------")
#         """
#         Run the simulation
#         """
#         if __name__ == "__main__":
#             from modules.inchem_main import run_inchem
#             run_inchem(filename, particles, INCHEM_additional, custom, rel_humidity,
#                        M, const_dict, ACRate, diurnal, city, date, lat, light_type,
#                        light_on_times, glass, AV, initials_from_run,
#                        initial_conditions_gas, timed_emissions, timed_inputs, dt, t0,
#                        iroom, ichem_only, path, output_folder,
#                        seconds_to_integrate, custom_name, output_graph, output_species,
#                        reactions_output, H2O2_dep, O3_dep, adults,
#                        children, surfaces_AV, __file__, temperatures, spline)
