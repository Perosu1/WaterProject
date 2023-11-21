#-------------------------------------------------#
#--------------Libraries--------------------------#
#-------------------------------------------------#

import numpy as np
import scipy as scp
import pandas as pd
import matplotlib.pyplot as plt
from scipy import integrate
from numpy import inf, e

#-------------------------------------------------#
#--------------Tunable Parameters-----------------#
#-------------------------------------------------#

#Please select the heavy atom your group 16 hydride contains. 
#Please note that all the code is writted with labels for oxygen, but correctly computes values for all group 16 hydrides.
heavy_atom = "Se" #options: O, S, Se, Te, Po

T = 208.71 #K
N_H = 1024 #number of hydrogens
N_heavy = 512 #number of heavy atoms

usable_vacf = 1000 #how many timesteps of the vacf to use

nu_min = 0 
nu_max = 0.120e+15
nu_step = 0.60e+11

#-------------------------------------------------#
#---------------Constants-------------------------#
#-------------------------------------------------#

#Constants
boltzmann = 1.380649e-23
lightspeed = 2.99792458e8 #ms-1
gasconstant = 8.31446261815324	#J⋅K−1⋅mol−1
avogadro = 6.02214076e23 #mol-1
planck = 6.62607015e-34 #J⋅Hz−1

masses = {
    "H":1.6735575e-27,
    "O":2.6567e-26,
    "S":5.3245e-26,
    "Se":1.3113e-25,
    "Te":2.1188e-25,
    "Po":3.5e-25
} #masses are in kg. mass of polonium atom only approximate (mass number 209-Po)

molecule = "H2"+heavy_atom
filename = "H2"+heavy_atom+".png"

#-------------------------------------------------#
#---------------Functions-------------------------#
#-------------------------------------------------#

#mass_selector
def mass(atom):
    try:
        return masses[str(atom)]
    except KeyError:
        print("Error: Sorry, only O, S, Se, Te, Po are supported")
    except:
        print("Unknown error") 

def calc_theta(freq):
    """
    Calculates theta from frequency
    """
    theta = (planck * freq)/boltzmann
    return theta

def calc_dW(temp, freq):
    """
    Calculates del heat capacity from temperature and using the calc_theta function inside
    T is temperature
    freq is frequency
    """
    #first getting a value of theta
    if freq == 0.0:
        return 0.0
    else:
        theta = calc_theta(freq)
        dW = ( (theta/T)**2 * ((e**(theta/T))/(e**(theta/T)-1)**2) -1  )
        return dW #i cut out a boltzmann from del_cv  

#-------------------------------------------------#
#---------------Importing Data--------------------#
#-------------------------------------------------#

#Importing all data.
#combining the oxygen and hydrogen data together
def loader():
    H_data = pd.read_csv("vacfH.dat", comment='#', header=None, delim_whitespace=True)
    O_data = pd.read_csv("vacfheavy.dat", comment='#', header=None, delim_whitespace=True)

    vacf = pd.DataFrame({
    "t":H_data.iloc[:,0],
    "H":H_data.iloc[:,4]*1e10, 
    "O":O_data.iloc[:,4]*1e10
    }) #factor 10**10 is to convert from A^2/fs^2 to m^2/s^2

    vacf["Total_Weighted"] = N_H*mass("H")*vacf["H"] + N_heavy*mass(heavy_atom)*vacf["O"]

    return vacf


vacf = loader()

#cut all but the first n rows (where n is defined in usable_vacf)
vacf_short = vacf[0:usable_vacf]

times = vacf_short["t"] #in fs
times_s = times*1e-15
Total_Weighted = vacf_short["Total_Weighted"]

frequencies = np.arange(nu_min, nu_max+nu_step, nu_step)

#-------------------------------------------------#
#---------------Checking Data---------------------#
#-------------------------------------------------#

#checking with equipartition theorem S(0) = <v^2> = 3*k*T/m 
print("The value of s(0) of H calculated through MD is", vacf.iloc[0,1]) 
print("The value of s(0) of H estimated through the equipartition theorem is", 3*boltzmann*T/mass("H")) 
print("The %error is", abs((vacf.iloc[0,1]-(3*boltzmann*T/mass("H")))/(3*boltzmann*T/mass("H")))*100, "%")
print("  ")
print("The value of s(0) of O calculated through MD is", vacf.iloc[0,2])
print("The value of s(0) of O estimated through the equipartition theorem is", 3*boltzmann*T/mass(heavy_atom)) 
print("The %error is", abs((vacf.iloc[0,2]-(3*boltzmann*T/mass(heavy_atom)))/(3*boltzmann*T/mass(heavy_atom)))*100, "%")

#-------------------------------------------------#
#-----Integration and multiplication with theta---#
#-------------------------------------------------#

s = []
for f in frequencies:
    kernel = Total_Weighted * np.cos(2 * np.pi * times_s * f)    
    s_temp = integrate.simpson(kernel, times_s) * 4.0 / (boltzmann * T) 
    s.append(s_temp)    

dW = []
for freq in frequencies:
    dW.append(calc_dW(T, freq))

s_times_dW = np.asarray(dW) * np.asarray(s)

#-------------------------------------------------#
#---------------Plotting--------------------------#
#-------------------------------------------------#

df = pd.DataFrame({"frequencies":frequencies, "wavenumbers":frequencies/(lightspeed*100), "s_times_dW":s_times_dW, "s":s})

fig, ax = plt.subplots()
s = ax.plot(df["frequencies"], df["s"], color = "r", label = "s(v)")
dWs = ax.plot(df["frequencies"], df["s_times_dW"], color = "b", label = "dW(v) x s(v)") #here I need to invert
ax.legend()
#ax.invert_xaxis()   # here how you can invert
ax.set_xlabel('Frequency [Hz]')
ax.set_ylabel('dW x s(ν) or s(ν)')
ax.set_title(filename)
plt.savefig(filename, bbox_inches='tight')
plt.show()

#-------------------------------------------------#
#------------Calculating correction---------------#
#-------------------------------------------------#


deltahc = boltzmann * gasconstant * integrate.simpson(s_times_dW, frequencies) / 512
print(deltahc, "per molecule")
print(deltahc*avogadro, "J per mol")
