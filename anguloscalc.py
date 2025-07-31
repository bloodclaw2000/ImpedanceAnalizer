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

#base_folder = r"C:\Users\Usuario\Documents\Resonadores 2024\RespequeDist\aluminum"

agnuevoangle4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AgNuevoDef\Angle4cm"
agnuevoangle8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AgNuevoDef\Angle8cm"
agnuevohorangle4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AgNuevoDef\AngleHor4cm"
agnuevohorangle8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AgNuevoDef\AngleHor8cm"


agdientes24angle4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes24\AgDef\Angle4cm"
agdientes24angle8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes24\AgDef\Angle8cm"
agdientes24horangle4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes24\AgDef\AngleHor4cm"
agdientes24horangle8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes24\AgDef\AngleHor8cm"

alnormalangle4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef\Angle4cm"
alnormalangle8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef\Angle8cm"
alnormalhorangle4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef\AngleHor4cm"
alnormalhorangle8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskNormal16\AluminioDef\AngleHor8cm"

aldientes16angle4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes16\AluminioDef\Angle4cm"
aldientes16angle8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes16\AluminioDef\Angle8cm"
aldientes16horangle4 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes16\AluminioDef\AngleHor4cm"
aldientes16horangle8 = r"C:\Users\Usuario\Documents\Resonadores 2025\Medidas Plataforma v2\DiskDientes16\AluminioDef\AngleHor8cm"



# Define available distances
angles = ["0deg", "5deg", "10deg", "15deg", "20deg","25deg", "30deg", "35deg", "40deg", "45deg","60deg","80deg"]
# Function to convert dB to linear scale

def db_to_linear(db):
    return 10 ** (db / 20)

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
angle_colors = {
    "0deg": "grey",
    "5deg": "blue",
    "10deg": "red",
    "15deg": "green",
    "20deg" : "yellow",
    "25deg": "orange", 
    "30deg" : "purple",
    "35deg" : "pink",
    "40deg" : "cyan",
    "45deg" : "olive",
    "50deg" : "brown",
    "60deg" : "black",
    "80deg" : "lightgreen"
    }
def runplot(angles, base_folder,count):
    for distance in angles:
        # Find Touchstone file
        s2p_files = glob.glob(f"{base_folder}/*{angles}*.s2p")
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
                if count == 0:
                     #Plot S21 efficiency with a solid line
                    plt.plot(frequencies_ghz, s21_efficiency, label=f"{last_two[1]} ({distance})", color=angle_colors[distance], linewidth=2)
                else: 
                     #Plot S21 efficiency with a solid line
                    #plt.plot(frequencies_ghz, s21_efficiency, label=f"{last_two[1]} ({distance})", color=angle_colors[distance], linewidth=2,linestyle = "--")
                    plt.plot(frequencies_ghz, s21_efficiency, color=angle_colors[distance], linewidth=2,linestyle = "--")

                print("aa")

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

# Initialize the figure
plt.figure(figsize=(10, 6))

folder1 = aldientes16angle8
folder2= aldientes16horangle8
#folder2 = agdientes4
twofolders = True
last_two = os.path.normpath(folder1).split(os.sep)[-2:]
last_two = [0, "7cm Disk Al Teeth Vertical 8cm dist"]
runplot(angles, folder1,0 )
if twofolders:
    last_two = os.path.normpath(folder2).split(os.sep)[-2:]
    last_two = [0,"7cm Disk Al Horizontal 8cm dist"]
    runplot(angles,folder2,1)
# Plot formatting
base_folder = folder1

last_two = os.path.normpath(base_folder).split(os.sep)[-2:]

plt.title(f"S21 Efficiency vs Frequency Offset for {last_two[0]}", fontsize=16)
plt.title(f"S21 Efficiency vs Frequency Offset for 24N Teeth Disk", fontsize=16)
plt.xlabel("Frequency (GHz)", fontsize=14)
plt.ylabel("Efficiency", fontsize=14)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.xlim(0.04,.15)
#plt.xticks(np.arange(1,1.4,0.05))
plt.ylim(0,.45)

# Show the plot
plt.show()