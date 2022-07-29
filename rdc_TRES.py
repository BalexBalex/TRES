from amuse.units import units, constants
from amuse.io import write_set_to_file
from amuse.io import read_set_from_file
from amuse.support.console import set_printing_strategy
import numpy as np
import pandas as pd
import sys


minimum_time_step = 1.e-9 |units.Myr


bin_type = {    
                'unknown': 0,       
                'merger': 1, 
                'disintegrated': 2, 
                'dynamical_instability': 3, 
                'detached': 4,       
                'contact': 5,    
                'collision': 6,    
                'semisecular': 7,      
                'rlof': 8,   #only used for stopping conditions
                'stable_mass_transfer': 9, 
                'common_envelope': 10,     
                'common_envelope_energy_balance': 11,     
                'ce_e': 12,     
                'ce_alpha': 13,     
                'common_envelope_angular_momentum_balance': 14,
                'ce_J': 15,
                'ce_gamma': 16,
                'double_common_envelope': 17,
                'dce': 18,
            }   

lib_print_style = { 0: "TRES standard; selected parameters", 
                1: "Full",
                2: "Readable format",}#default
       

def print_particle(particle):
        if particle.is_star:
            print(particle)                 
        else:
            print(particle) 
            print_particle(particle.child1)                
            print_particle(particle.child2)


def rdc(file_name_root, file_type, print_style, print_init, out_file_name, line_number):

    f_type = file_type
    if file_type == "hdf5":
        f_type = "hdf"
        
    file_name = file_name_root + "." + f_type            
    if file_name_root[-4:]==".hdf":
        file_name = file_name_root
    
    triple  = read_set_from_file(file_name, file_type)

    SaveDictSet = []
    for i, currtriple in enumerate(triple.history):
        CurrRun         = currtriple.number
        CurrSaveProps = {
            'SystemID': currtriple[0].number,
            'TimeMyr': (currtriple[0].time).value_in(units.Myr),
            'TripleBinType': bin_type[currtriple[0].bin_type], 
            'TripleMTStable': int(currtriple[0].is_mt_stable),
            'TripleA3RSun': (currtriple[0].semimajor_axis).value_in(units.RSun),
            'TripleE3': currtriple[0].eccentricity,
            'TripleOmega3': currtriple[0].argument_of_pericenter,
            'TripleG3': currtriple[0].longitude_of_ascending_node,
            'TripleMDotMSunYr': (currtriple[0].mass_transfer_rate).value_in(units.MSun/units.yr),
            'TrileIRel': currtriple[0].relative_inclination,
            'BinaryType': bin_type[currtriple[0].child2.bin_type],
            'BinaryStabMTQ': int(currtriple[0].child2.is_mt_stable),
            'BinaryARSun': currtriple[0].child2.semimajor_axis.value_in(units.RSun),
            'BinaryE': currtriple[0].child2.eccentricity,
            'Binaryomega': currtriple[0].child2.argument_of_pericenter,
            'BinaryOmega': currtriple[0].child2.longitude_of_ascending_node,
            'Donor1Q': int(currtriple[0].child2.child1.is_donor),
            'Type1': currtriple[0].child2.child1.stellar_type.value_in(units.stellar_type),
            'Mass1MSun': currtriple[0].child2.child1.mass.value_in(units.MSun),
            'Spin1MyrInv': currtriple[0].child2.child1.spin_angular_frequency.value_in(1./units.Myr),
            'R1RSun': currtriple[0].child2.child1.radius.value_in(units.RSun),
            'MCore1MSun': currtriple[0].child2.child1.core_mass.value_in(units.MSun),
            'Donor2Q': int(currtriple[0].child2.child2.is_donor),
            'Type2': currtriple[0].child2.child2.stellar_type.value_in(units.stellar_type),
            'Mass2MSun': currtriple[0].child2.child2.mass.value_in(units.MSun),
            'Spin2MyrInv': currtriple[0].child2.child2.spin_angular_frequency.value_in(1./units.Myr),
            'R2RSun': currtriple[0].child2.child2.radius.value_in(units.RSun),
            'MCore2MSun': currtriple[0].child2.child2.core_mass.value_in(units.MSun),
            'Donor3Q': int(currtriple[0].child1.is_donor),
            'Type3': currtriple[0].child1.stellar_type.value_in(units.stellar_type),
            'Mass3MSun': currtriple[0].child1.mass.value_in(units.MSun),
            'Spin3MyrInv': currtriple[0].child1.spin_angular_frequency.value_in(1./units.Myr),
            'R3RSun': currtriple[0].child1.radius.value_in(units.RSun),
            'MCore2MSun': currtriple[0].child1.core_mass.value_in(units.MSun),
            'DynInst': int(currtriple[0].dynamical_instability),
            'KozaiType': currtriple[0].kozai_type,
            'ErrorFlag': currtriple[0].error_flag_secular,
            'CPUTime': currtriple[0].CPU_time}       

        #print('In RDC ' + str(i) + ':')
        #print(CurrSaveProps)
        SaveDictSet.append(CurrSaveProps)

    df = pd.DataFrame(SaveDictSet)
    df.to_csv(out_file_name,index=False)
    print(df)



def parse_arguments():
    from amuse.units.optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", dest="file_name_root", default = "TRES",
                      help="file name [%default]")                      
    parser.add_option("-F", dest="file_type", default = "hdf5",
                      help="file type [%default]") 
    parser.add_option("-S", dest="print_style", type="int", default = 2,
                      help="print style [%default]") 
    parser.add_option("-E", dest="out_file_name", default = "TRESRDC.csv",
                      help="output filename [%default]")                        
    parser.add_option("--print_init", dest="print_init", action="store_true", default = False, 
                      help="print initial conditions for re running [%default]")
    parser.add_option("-l", dest="line_number", type="int", default = 0,
                      help="line number for printing initial conditions [%default]") #will only do something when print_init = True


                      
    options, args = parser.parse_args()
    return options.__dict__


if __name__ == '__main__':
    options = parse_arguments()

    set_printing_strategy("custom", 
                          preferred_units = [units.MSun, units.RSun, units.Myr], 
                          precision = 11, prefix = "", 
                          separator = " [", suffix = "]")



    print(' ')
    rdc(**options)  
    