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
# Define the base folder where the data is stored
#todos son mili
#base_folder = r"C:\Users\Usuario\Documents\Resonadores 2024\RespequeDist\aluminum"
#agpeque17 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma\Disk5JNormal16\Offset 1.7cm"
#agpeque4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma\Disk5JNormal16\Offset 4cm"
agnormal17 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AgNuevoDef\Offset 1.7cm"
agnormal4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AgNuevoDef\Offset 4cm"
agnormal8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AgNuevoDef\Offset 8cm"


alnormal17 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef\Offset 1.7cm"
alnormal4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef\Offset 4cm"
alnormal8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef\Offset 8cm"


aldientes17 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes16\AluminioDef\Offset 1.7cm"
aldientes4 =  r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes16\AluminioDef\Offset 4cm"
aldientes8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes16\AluminioDef\Offset 8cm"
# Define available distances

agdientes17 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes24\AgDef\Offset 1.7cm"
agdientes4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes24\AgDef\Offset 4cm"
agdientes8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes24\AgDef\Offset 8cm"

rescelia = r"J:\Medidas_ResonadoresCelia_Pablo\Offsets3cmv3"

 
distances = ["off0cm","off1cm", "off2cm","off4cm","off6cm"]
distances = ["off0cm","off1cm", "off2cm","off3cm",]
distances = ["off0cm","off1cm", "off2cm","off3cm","off4cm","off5cm", "off6cm", "off7cm", "off8cm"]
distances = ["off0cm","off1cm", "off2cm","off3cm","off4cm","off5cm", "off6cm", "off7cm", "off8cm","off9cm","off10cm","off11cm","off12cm"]
distances = ["off0cm","off-1cm", "off-2cm","off-3cm","off-4cm","off-5cm", "off-6cm", "off-7cm", "off-8cm"]

# Function to convert dB to linear scale

def db_to_linear(db):
    return 10 ** (db / 20)

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
    "off0cm": "grey",
    "off0.5cm": "blue",
    "off1cm": "red",
    "off3cm": "green",
    "off2cm" : "yellow",
    "off4cm" : "green",
    "off6cm": "orange",

}
distance_colors = {
    "off0cm": "grey",
    "off1cm": "blue",
    "off2cm": "red",
    "off3cm": "green",
    "off4cm" : "yellow",
    "off5cm": "orange", 
    "off6cm" : "purple",
    "off7cm" : "pink",
    "off8cm" : "cyan",
    "off9cm" : "olive",
    "off10cm" : "brown",
    "off11cm" : "black",
    "off12cm" : "lightgreen"
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
                # Convert to efficiency
                s21_db = 20 * np.log10(np.abs(s21))
                s21_linear = db_to_linear(s21_db)
                s21_efficiency = s21_linear ** 2
                # Convert frequency to GHz
                frequencies_ghz = frequencies / 1e9
                distance_fixed = distance.replace("-", "")
                if count == 0:
                     #Plot S21 efficiency with a solid line
                    plt.plot(frequencies_ghz, s21_efficiency, label=f"{last_two[1]} ({distance})", color=distance_colors[distance_fixed], linewidth=2)
                else: 
                     #Plot S21 efficiency with a solid line
                    plt.plot(frequencies_ghz, s21_efficiency, label=f"{last_two[1]} ({distance})", color=distance_colors[distance_fixed], linewidth=2,linestyle = "--")
                    #plt.plot(frequencies_ghz, s21_efficiency, color=distance_colors[distance], linewidth=2,linestyle = "--")
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
                #plt.plot(csv_x, csv_y, label=f"Simulation Data ({distance})", color=distance_colors[distance], linewidth=2, linestyle = "--")

            except Exception as e:
                print(e)
                print(f"Error loading {csv_file}: {e}")

# Initialize the figure
plt.figure(figsize=(10, 6))

folder1 = rescelia
folder2 = aldientes8
twofolders = False
last_two = os.path.normpath(folder1).split(os.sep)[-2:]
last_two = [0, "7cm Al Normal at  8cm dist"]
runplot(distances, folder1,0 )
if twofolders:
    last_two = os.path.normpath(folder2).split(os.sep)[-2:]
    last_two = [0,"7cm Al Teeth 8cm dist"]
    runplot(distances,folder2,1)
# Plot formatting
base_folder = folder1

last_two = os.path.normpath(base_folder).split(os.sep)[-2:]

plt.title(f"S21 Efficiency vs Frequency Offset for {last_two[0]}", fontsize=16)
plt.title(f"S21 Efficiency vs Frequency Offset for 24N Teeth Disk", fontsize=16)
plt.xlabel("Frequency (GHz)", fontsize=14)
plt.ylabel("Efficiency", fontsize=14)
plt.legend(fontsize=8)
plt.grid(True)
plt.tight_layout()
plt.xlim(0.2,.35)
#plt.xticks(np.arange(1,1.4,0.05))
plt.ylim(0,.3)

# Show the plot
plt.show()