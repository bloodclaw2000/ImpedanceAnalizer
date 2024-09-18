# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 13:58:38 2024

@author: Usuario
"""

import matplotlib.pyplot as plt
from math import cos, sin, pi
import csv
import os
import re
import tkinter as tk
from tkinter import filedialog

epsilon_0 = 8.8541878128E-12
DEFAULT_SURFACE = .0207
DEFAULT_HEIGHT = 0.002

def get_folder_path():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder")
    return folder_path
def parse_csv_to_dict(file_path):
    data_dict = {}
    
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            frequency = float(row['Frequency'])  # Use 'Frequency' as the dictionary key
            data_dict[frequency] = {
                'Q Factor': float(row.get('Q Factor')) if row.get('Q Factor') else None,
                'Tan D': float(row.get('Tan D')) if row.get('Tan D') else None,
                'Impedance': float(row.get('Impedance')) if row.get('Impedance') else None,
                'Phase': float(row.get('Phase')) if row.get('Phase') else None,
                'Frequency': frequency,  # Frequency should always be present
                'L': float(row.get('L')) if row.get('L') else None,
                'C': float(row.get('C')) if row.get('C') else None,
                'R': float(row.get('R')) if row.get('R') else None
            }

    return data_dict

def extract_file_info(filename):
    # Regex to extract name, voltage, and state from filename
    match = re.match(r"(.*?)_(\d+V)_(abierto|cerrado)", filename)
    if match:
        name = match.group(1)  # e.g., 'kalman_1'
        voltage = parse_voltage(match.group(2))  # e.g., '2V' or '02V'
        state = match.group(3)  # e.g., 'cerrado' or 'abierto'
        return name, voltage, state
    return None, None, None  # If the pattern doesn't match    return None, None
def parse_voltage(voltage_str):
    # Remove the 'V' at the end of the string
    if voltage_str.endswith('V'):
        voltage_value = voltage_str[:-1]  # Remove 'V'
        
        # Check if there are leading zeros or single digits
        if voltage_value.startswith('0'):
            # Return the float of the string divided by 10^(length of string minus 1)
            return float(voltage_value) / (10 ** (len(voltage_value) - 1))
        else:
            return float(voltage_value)  # No leading zero, return as float
    
    return None  # Return None if the string format is invalid
def parse_all_files_in_folder(folder_path):
    final_data = {}

    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):  # Process only bin files
            file_path = os.path.join(folder_path, filename)
            # Extract voltage and state from filename
            name, voltage, state = extract_file_info(filename)
            if voltage and state:
                # Parse the CSV data for this file
                file_data = parse_csv_to_dict(file_path)
                fname = name +"_"+ str(voltage) +"_"+ str(state)
                # Store the data with voltage and state as additional keys
                final_data[fname] = {
                    'voltage': voltage,
                    'state': state,
                    'data': file_data,
                    'name': name
                    
                }
    
    return final_data

def export_results_to_csv(results_dict, output_file_path):
    # Dynamically get all possible columns from the dictionary
    all_columns = set()

    # Collect all possible keys from all entries in the results_dict
    for data in results_dict.values():
        all_columns.update(data.keys())
    
    # Ensure 'Frequency' is the first column and remove it from the set
    all_columns.discard('Frequency')
    
    # Convert the set to a sorted list for consistent column order
    all_columns = ['Frequency'] + sorted(all_columns)

    with open(output_file_path, mode='w', newline='') as file:
        # Initialize the CSV writer with dynamic column names
        writer = csv.DictWriter(file, fieldnames=all_columns,dialect='excel-tab')
        
        # Write the header row
        writer.writeheader()
        
        # Write the data rows, ensuring Frequency is the first column
        for frequency, data in results_dict.items():
            # Force Frequency as the first key in each row
            data['Frequency'] = frequency
            writer.writerow(data)
    
    print(f"Results successfully exported to {output_file_path}")
    
def parallelimp(cerrimp, abimp):
    #returns sample impedance from 1/cer = 1/ab + 1/samp
    return 1/(1/cerrimp - 1/abimp)  
def seriescap(x,y):
    return x-y
def calcZ(Imp, Phase):
    
    Zreal = Imp*cos(Phase*pi/180)
    Zim = Imp*sin(Phase*pi/180)
    return Zreal, Zim
def EZ(Z,Zre,Zim,surface,height, f,epsilon0 = 8.8541878128E-12 ):
    Epsre = -height* Zim / (2* pi * f * epsilon0 * surface * Z**2)
    Epsim = height* Zre / (2* pi * f * epsilon0 * surface * Z**2)
    return Epsre, Epsim
def calculate_catacitance(cap,surface,height,epsilon0 = 8.8541878128E-12):
    return (cap * height) / (surface* epsilon0)
def calculate_impedance_function(data,surface, height, folder_path):
    grouped_data = {}
    result = {}

    # Group data by name and voltage
    for file_info, content in data.items():
        name = content['name']
        voltage = content['voltage']
        state = content['state']
        
        # Create unique key for name and voltage combination
        key = (name, voltage)
        
        # Initialize entry in the grouped data dictionary
        if key not in grouped_data:
            grouped_data[key] = {}
        
        # Store 'abierto' and 'cerrado' data
        grouped_data[key][state] = content['data']

    # Calculate f(x, y) where x is impedance in 'abierto' and y is impedance in 'cerrado'
    for (name, voltage), states in grouped_data.items():
        if 'abierto' in states and 'cerrado' in states:
            abierto_data = states['abierto']
            cerrado_data = states['cerrado']
            
            # Initialize dictionary for this name and voltage pair
            result[(name, voltage)] = {}
            
                
            # Loop through frequencies to calculate f(x, y)
            for freq in abierto_data:
                if freq in cerrado_data:
                    y = abierto_data[freq]['Impedance']  # Impedance in 'abierto'
                    x = cerrado_data[freq]['Impedance']  # Impedance in 'cerrado'
                    
                    # Calculate f(x, y)
                    sampimp = parallelimp(x, y)
                    sampcap = seriescap(cerrado_data[freq]['C'],abierto_data[freq]['C'])
                    Zreal, Zim = calcZ(sampimp, cerrado_data[freq]['Phase'])
                    Epsre, Epsim = EZ(sampimp,Zreal,Zim,surface,height,freq)
                    Epsrecap = calculate_catacitance(sampcap,surface,height)
                    
                    result[(name, voltage)][freq] = {
                        'Frequency': cerrado_data[freq]['Frequency'],
                        'sample_impedance':sampimp,
                        'cerrado_impedance' : cerrado_data[freq]['Impedance'],
                        'abierto_impedance': abierto_data[freq]['Impedance'],
                        'Q Factor': cerrado_data[freq]['Q Factor'],
                        'Tan D': cerrado_data[freq]['Tan D'],
                        'Phase': cerrado_data[freq]['Phase'],
                        'L': cerrado_data[freq]['L'],
                        'C': cerrado_data[freq]['C'],
                        'R': cerrado_data[freq]['R'],
                        'Zreal' : Zreal,
                        'Zim' : Zim,
                        'Epsreal': Epsre, 
                        'Epsrealcap': Epsrecap, 
                        'Epsim' : Epsim,
                        }
                    
                    """
                    for freq in cerrado_data:
                        result[(name, voltage)][freq]['cerrado_impedance'] : cerrado_data[freq]['Impedance']
                        result[(name, voltage)][freq] = {
                            'abierto_impedance': abierto_data[freq]['Impedance']}
                        result[(name, voltage)][freq] = {
                            'Q Factor': cerrado_data[freq]['Q Factor']}
                        result[(name, voltage)][freq] = {
                            'Tan D': cerrado_data[freq]['Tan D']}
                        result[(name, voltage)][freq] = {
                            'Phase': cerrado_data[freq]['Phase']}
"""
        # Create a unique filename for each result
        output_file_name = f"{name}_{voltage}V_{state}.csv"
        output_file_path = os.path.join(folder_path, output_file_name)
        
        # Export each result to its own CSV file
        export_results_to_csv(result[(name, voltage)], output_file_path)
    return result





def plot_impedance_results(results, selected_pairs, selected_columns, y_scale):
    fig, ax = plt.subplots()
    scatter2 = None
    if len(selected_columns) == 2:
        ax2 = ax.twinx()  # Create a secondary y-axis for the second column

    colors = plt.cm.get_cmap('tab10', len(selected_pairs))  # Generate distinct colors for each pair
    scatter_plots = []
    all_frequencies = []
    all_f_values = []
    all_f2_values = []
    for i, selected_pair in enumerate(selected_pairs):
        name, voltage = selected_pair
        data = results[selected_pair]

        frequencies = list(data.keys())
        f_values = [data[freq][selected_columns[0]] for freq in frequencies]
        all_f_values.append(f_values)
        scatter1 = ax.scatter(frequencies, f_values, color=colors(i), label=f'{name} ({voltage}V) {selected_columns[0]}', picker=True)
        line1 = ax.plot(frequencies, f_values, '--', color=colors(i))
        scatter_plots.append(scatter1)

        if len(selected_columns) == 2:
            f2_values = [data[freq][selected_columns[1]] for freq in frequencies]
            all_f2_values.append(f2_values)
            scatter2 = ax2.scatter(frequencies, f2_values, color=colors(i), label=f'{name} ({voltage}V) {selected_columns[1]}', marker='x', picker=True)
            line2 = ax2.plot(frequencies, f2_values, '--', color=colors(i))
            scatter_plots.append(scatter2)

    # Set axis labels and scale for the first column
    ax.set_xlabel('Frequency')
    ax.set_ylabel(selected_columns[0], color="r")
    ax.set_xscale('log')  # Always use log scale for frequency
    ax.set_yscale(y_scale[0])  # Set the Y-axis scale for the first column

    if len(selected_columns) == 2:
        ax2.set_ylabel(selected_columns[1], color="b")
        ax2.set_yscale(y_scale[1])  # Set Y-axis scale for the second column

    # Combine legends for both y-axes
    if len(selected_columns) == 2:
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='best')
    else:
        ax.legend()

    ax.set_title(f"Comparing Groups: {', '.join([f'{name} {voltage}V ' for name, voltage in selected_pairs])}")

    # Event handler for clicking on a point
    def on_pick(event):
        if scatter2 is None:
            if event.artist not in scatter_plots:
                return
        else:
            if event.artist not in scatter_plots:
                return
            
        ind = event.ind[0]
        frequency = frequencies[ind]
        values_str = f'Clicked Frequency: {frequency:.2f}\n'
        for i, selected_pair in enumerate(selected_pairs):
            name, voltage = selected_pair
            value1 = all_f_values[i][ind]
            values_str += f'{name}  ({voltage}V): {selected_columns[0]} = {value1:.2f}'
            if len(selected_columns) == 2:
                value2 = all_f2_values[i][ind]
                values_str += f', {selected_columns[1]} = {value2:.2f}'
            values_str += '\n'
        ax.set_title(values_str)
        plt.draw()

    fig.canvas.mpl_connect('pick_event', on_pick)
    plt.show()


def interactive_plot(results):
    while True:
        pairs = list(results.keys())
        pair_names = [f'{name} ({voltage}V)' for name, voltage in pairs]

        print("Available pairs:")
        for i, pair_name in enumerate(pair_names):
            print(f"{i + 1}: {pair_name}")

        selected_pairs = []
        while True:
            try:
                # Let the user select multiple groups
                choice = int(input(f"Select a pair (1-{len(pair_names)}) or 0 to finish: ")) - 1
                if choice == -1:
                    break
                if 0 <= choice < len(pair_names):
                    selected_pairs.append(pairs[choice])
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        if not selected_pairs:
            print("No pairs selected, exiting...")
            break

        # Display available columns from the first selected data (assuming all groups have the same structure)
        available_columns = list(results[selected_pairs[0]][list(results[selected_pairs[0]].keys())[0]].keys())
        print("Available columns:")
        for i, column in enumerate(available_columns):
            print(f"{i + 1}: {column}")

        # User selects how many columns to plot (1 or 2)
        num_columns = int(input("Do you want to plot 1 or 2 columns? "))
        selected_columns = []
        
        if num_columns == 1:
            col1_choice = int(input(f"Select the column to plot (1-{len(available_columns)}): ")) - 1
            if 0 <= col1_choice < len(available_columns):
                selected_columns.append(available_columns[col1_choice])
            else:
                print("Invalid column selection.")
                continue

        elif num_columns == 2:
            col1_choice = int(input(f"Select the first column to plot (1-{len(available_columns)}): ")) - 1
            col2_choice = int(input(f"Select the second column to plot (1-{len(available_columns)}): ")) - 1
            if 0 <= col1_choice < len(available_columns) and 0 <= col2_choice < len(available_columns):
                selected_columns.append(available_columns[col1_choice])
                selected_columns.append(available_columns[col2_choice])
            else:
                print("Invalid column selection.")
                continue
        else:
            print("Invalid number of columns.")
            continue

        # Ask for the y-axis scale (linear or log) for each axis
        y_scale = []
        for i in range(num_columns):
            scale_choice = input(f"Select y-axis scale for {selected_columns[i]} (linear/log): ").strip().lower()
            y_scale.append('log' if scale_choice == 'log' else 'linear')

        # Plot the selected columns for all selected pairs
        plot_impedance_results(results, selected_pairs, selected_columns, y_scale)

        user_choice = input("Do you want to select another group (y/n)? ").strip().lower()
        if user_choice != 'y':
            print("Exiting...")
            break  
        
def main():
    print("Select Data Folder")
    folder_path = get_folder_path()
    if folder_path:
        all_data = parse_all_files_in_folder(folder_path)
        print(os.listdir(folder_path))
        # Print the final data for inspection
        # Asking for surface area and height
        surface_input = input(f"Enter surface area (in meters) [default {DEFAULT_SURFACE}]: ")
        height_input = input(f"Enter height (in meters) [default {DEFAULT_HEIGHT}]: ")
        
        surface = float(surface_input) if surface_input.strip() else DEFAULT_SURFACE
        height = float(height_input) if height_input.strip() else DEFAULT_HEIGHT
        impedance_results = calculate_impedance_function(all_data, surface, height,folder_path)
        for (name, voltage), frequencies in impedance_results.items():
            print(f"Name: {name}, Voltage: {voltage}V")
        # Run the interactive plot
        interactive_plot(impedance_results) 
        

if __name__ == "__main__":
    main()
