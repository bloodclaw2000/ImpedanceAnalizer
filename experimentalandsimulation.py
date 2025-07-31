# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 11:49:18 2025

@author: Usuario
"""

import numpy as np
import matplotlib.pyplot as plt
from skrf import Network
import glob
import re 
import os
import skrf as rf
# Define the base folder where the data is stored
#TODOS SON DEFENSA
#base_folder = r"C:\Users\Usuario\Documents\Resonadores 2024\RespequeDist\aluminum"
#agviejo = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma\DiskNormal16\Ag Viejo"
agnuevo = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AgNuevoDef"
agpeque = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma\Disk5JNormal16"
agdientes24 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes24\AgDef"
alnormal = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef"
alnormal = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef"
alnormalv2 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef_2\Distancia"
alentalla = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\Al_Entalla\Distancia"
aldientes16 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes16\AluminioDef"
#agalnormal = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma\DiskNormal16\A1l_Ag2"
#agagpnormal = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma\DiskNormal16\Ag1_Agp2"
#alnormalmili = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma\DiskNormal16\AluminioDef"
# Define available distances

rescelia = r"J:\Medidas_ResonadoresCelia_Pablo\distancev2"
rescelia2 = r"C:\Users\Usuario\Documents\Celia Paper\Celia Ver\R5 vs dst"



distances = ["1.7cm","2cm", "3cm","4cm","5cm","6cm","7cm","8cm","9cm","10cm","11cm","12cm","13cm","14cm","15cm"]
distances = ["1.5cm","2cm", "3cm","4cm","5cm","6cm","7cm","8cm","9cm","10cm"]

#distances = ["5cm"]
# Function to convert dB to linear scale
def db_to_linear(db):
    return 10 ** (db / 20)
def returns (s21):
    s21_db = 20 * np.log10(np.abs(s21))
    s21_linear = db_to_linear(s21_db)
    s21_efficiency = s21_linear ** 2
    return s21_db,s21_linear,s21_efficiency
def find_max_efficiency(frequencies_ghz, s21_efficiency, f_min, f_max):
    """
    Finds the frequency with the maximum S21 efficiency within a specified frequency range.

    Parameters:
    - frequencies_ghz (np.ndarray): Array of frequencies in GHz.
    - s21_efficiency (np.ndarray): Array of corresponding S21 efficiency values.
    - f_min (float): Minimum frequency (GHz) for the search range.
    - f_max (float): Maximum frequency (GHz) for the search range.

    Returns:
    - max_freq (float): Frequency in GHz where efficiency is highest within the range.
    - max_eff (float): Maximum efficiency within the range.
    - max_idx_global (int): Index of the maximum efficiency in the original array.
    """
    if frequencies_ghz.shape != s21_efficiency.shape:
        raise ValueError("frequencies_ghz and s21_efficiency must have the same shape.")
    # Create a mask for the frequency range
    mask = (frequencies_ghz >= f_min) & (frequencies_ghz <= f_max)

    if not np.any(mask):
        raise ValueError("No frequencies found in the specified range.")
        
    # Get indices of the frequencies in the range
    valid_indices = np.argwhere(mask).flatten()

    # Get the efficiencies at those indices
    filtered_eff = s21_efficiency[valid_indices]

    # Find local index of the maximum efficiency
    max_local_idx = np.argmax(filtered_eff)

    # Map back to original array index
    max_global_idx = valid_indices[max_local_idx]
    print("aa")
    # Return values
    return frequencies_ghz[max_global_idx], s21_efficiency[max_global_idx], max_global_idx    


# Define colors for different distances
distance_colors = {
    "1.7cm": "grey",
    "2cm": "blue",
    "3cm": "red",
    "4cm": "green",
    "5cm": "green",

    "6cm" : "yellow",
    "7cm": "orange",
    "8cm" : "purple",
    "9cm" : "pink",
    "10cm" : "cyan",
    "11cm" : "olive",
    "12cm" : "brown",
    "13cm" : "black",
    "14cm" : "lightgreen",
    "15cm" : "pink"
}
def runplot(distances, base_folder,count):
    for distance in distances:
        # Find Touchstone file
        s2p_files = glob.glob(f"{base_folder}/*{distance}*.s2p")
        # Get all .s2p files
        escaped_distance = re.escape(distance)

        # \b doesn't work well with dots, so we make our own boundary
        pattern = re.compile(rf"(?<![\d.]){escaped_distance}(?![\d.])")

        all_s2p_files = glob.glob(f"{base_folder}/*.s2p")

        # Apply strict pattern match on basename
        s2p_files = [
            f for f in all_s2p_files 
            if pattern.search(os.path.splitext(os.path.basename(f))[0])
        ]
        print(s2p_files)
        # Process each Touchstone file
        for s2p_file in s2p_files:
            try:
                network = Network(s2p_file)
                frequencies = network.f  # Frequencies in Hz
                s21 = network.s[:, 1, 0]  # Extract S21 parameter
                s11 = network.s[:, 0, 0]
                s22 = network.s[:,1,1]
                s12 = network.s[:,0,1] #just test
                # Convert to efficiency
                """s11_db = 20 * np.log10(np.abs(s11))
                s11_linear = db_to_linear(s11_db)
                s11_efficiency = s11_linear ** 2"""
                s21_db,s21_linear,s21_efficiency = returns(s21)
                s11_db,s11_linear,s11_efficiency = returns(s11)
                s22_db,s22_linear,s22_efficiency = returns(s22)
                s12_db,s12_linear,s12_efficiency = returns(s12)

                """s21_db = 20 * np.log10(np.abs(s21))
                s21_linear = db_to_linear(s21_db)
                s21_efficiency = s21_linear ** 2"""
                
                """s11_db = 20 * np.log10(np.abs(s11))
                s11_linear = db_to_linear(s11_db)
                s11_efficiency = s11_linear**2
                PTE = s21_efficiency/(1-s11_efficiency)
                
                s12_db = 20 * np.log10(np.abs(s12))
                s12_linear = db_to_linear(s12_db)
                s12_efficiency = s12_linear ** 2"""
                
                # Convert frequency to GHz
                frequencies_ghz = frequencies / 1e9
                # Characteristic impedance (Z0)
                
                
                #last_two = " ".join(last_two)
                if count == 0:
                     #Plot S21 efficiency with a solid line
                    plt.plot(frequencies_ghz, s11_efficiency, label=f"{last_two[1]} ({distance})", color=distance_colors[distance], linewidth=2)
                    plt.plot(frequencies_ghz, s22_efficiency, label=f"{last_two[1]} ({distance})", color="green", linewidth=2)

                    #plt.plot(frequencies_ghz, s11_efficiency, label=f"{last_two[1]} ({distance})", color=distance_colors[distance], linewidth=2,linestyle = "--")

                    #plt.plot(frequencies_ghz, PTE, label=f"{last_two[1]} ({distance})", color=distance_colors[distance], linewidth=2)

                    
                    #plt.plot(frequencies_ghz, PTE, label=f"PTE ({distance})", color=distance_colors[distance], linewidth=2, linestyle = ":")
                else: 
                     #Plot S21 efficiency with a solid line
                    plt.plot(frequencies_ghz, s11_efficiency, label=f"{last_two[1]} ({distance})", color=distance_colors[distance], linewidth=2,linestyle = "--")
                    #plt.plot(frequencies_ghz, PTE, label=f"{last_two[1]} ({distance})", color=distance_colors[distance], linewidth=2,linestyle = "--")
                    plt.plot(frequencies_ghz, s22_efficiency, label=f"{last_two[1]} ({distance})", color="green", linewidth=2 ,linestyle = "--")

                print("aa")
                f_min = 0.2
                f_max = 0.4
                max_freq, max_eff, idx = find_max_efficiency(frequencies_ghz, s21_efficiency, f_min, f_max)
                print(f"{distance}: {max_freq:.4f} GHz, {max_eff:.4f} eff")

            except Exception as e:
                print(f"Error loading {s2p_file}: {e}")
        # Find CSV files for this distance
        csv_files = glob.glob(f"{base_folder}/*_{distance}*.csv")
        
        # Process each CSV file
        for csv_file in csv_files:
            try:
                csv_x = []
                csv_y = []

                with open(csv_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("%"):  # Skip header lines
                            continue
                        
                        # Handle both comma (`,`) and tab (`\t`) separators
                        if "," in line:
                            x, y = line.split(",")
                        elif "\t" in line:
                            x, y = line.split("\t")
                        elif ";" in line:
                            x, y = line.split(";")
                        else:
                            raise ValueError(f"Unknown separator in {csv_file}")

                        csv_x.append(float(x) / 1e9)  # Convert Hz to GHz
                        csv_y.append(float(y))

                # Plot CSV data with a dotted line in the same color
                print("aaa")
                #plt.plot(csv_x, csv_y, label=f"Simulation Data ({distance})", color=distance_colors[distance], linewidth=2, linestyle = "--")

            except Exception as e:
                print(e)
                print(f"Error loading {csv_file}: {e}")
    return s2p_files
# Initialize the figure
plt.figure(figsize=(10, 6))
folder1 = alnormal
folder2 = alnormalv2
twofolders = True
distances = ["3cm"]
last_two = os.path.normpath(folder1).split(os.sep)[-2:]
last_two = [0, "7cm Al Normal Mili Disk"]
s2p_files= runplot(distances, folder1,0 )
if twofolders:
    last_two = os.path.normpath(folder2).split(os.sep)[-2:]
    last_two = [0,"7cm Al Entallada 2 Mili Disk "]
    runplot(distances,folder2,1)
base_folder = folder1
# Loop through distances and find corresponding files
last_two = os.path.normpath(base_folder).split(os.sep)[-2:]
#last_two = " ".join(last_two)
# Plot formatting
#plt.xscale("log")
plt.title(f"S21 Efficiency vs Frequency for {last_two[0]}", fontsize=16)
plt.title(f"S21 Efficiency vs Frequency Distance ", fontsize=16)
plt.xlabel("Frequency (GHz)", fontsize=14)
plt.ylabel("Efficiency ($S^2_{21} $)", fontsize=14)
plt.ylabel("S11)", fontsize=14)

plt.legend(fontsize=6)
plt.grid(True)
plt.tight_layout()
plt.xlim(1.5,2.5)
#plt.xticks(np.arange(1,1.4,0.05))
#plt.ylim(0,.01)

# Show the plot
plt.show()
"""
print("AAAA")
print(s2p_files)
#s2p_files = ['C:\\Users\\Usuario\\Documents\\Resonadores 2025\\Medidas Plataforma\\DiskNormal16\\Ag Nuevo\\7cm.s2p','C:\\Users\\Usuario\\Documents\\Resonadores 2025\\Medidas Plataforma\\DiskNormal16\\Aluminio\\7cm.s2p']
for s2p_file in s2p_files:
    print(s2p_files)
    plt.figure()
    network = Network(s2p_file)
    frequencies = network.f  # Frequencies in Hz
    fig, ax = plt.subplots()
    network.plot_s_db(m=0, n=0, ax=ax, color='r')
    network.plot_s_db(m=1, n=0, ax=ax, color='b')
    ax.set_xlim(0,0.15E9)
    ax.set_ylim(0,1E-2)
    plt.show()
    plt.figure()
    network.plot_s_smith(m=0,n=0)
    plt.show()"""