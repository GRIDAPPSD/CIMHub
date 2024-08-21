# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 18:04:42 2024

@author: monish mukherjee
"""

import opendssdirect as dss
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glmanip

def get_gld_voltages(volts, node_dict):
    
    volts = volts.set_index('node_name')  
    bus_A = pd.DataFrame(columns =  ['node', 'Voltage_glm'])
    bus_B = pd.DataFrame(columns =  ['node', 'Voltage_glm'])
    bus_C = pd.DataFrame(columns =  ['node', 'Voltage_glm'])
    
    node_dict = {}
    node_dict.update(model['node'])
    # node_dict.update(model['triplex_node'])

    for node_id in node_dict:
        v_norm = float(node_dict[node_id]['nominal_voltage'])
        valA = volts.iloc[volts.index == node_id.replace('"','')]['voltA_mag'].values[0]
        valB = volts.iloc[volts.index == node_id.replace('"','')]['voltB_mag'].values[0]
        valC = volts.iloc[volts.index == node_id.replace('"','')]['voltC_mag'].values[0]
        
        if 'A' in node_dict[node_id]['phases'] and valA > 0:
            bus_A.loc[len(bus_A)]=[node_id, valA/v_norm] 
        if 'B' in node_dict[node_id]['phases'] and valB > 0:
            bus_B.loc[len(bus_B)]=[node_id, valB/v_norm] 
        if 'C' in node_dict[node_id]['phases'] and valC > 0:
            bus_C.loc[len(bus_C)]=[node_id, valC/v_norm] 
                
    return bus_A, bus_B, bus_C

def get_dss_voltage_by_phase(dss, ph, bus_volt_ph):
    
    bus_volt_ph.insert(2, "Voltage_dss", np.ones(len(bus_volt_ph)), True)
    for i in range(len(bus_volt_ph)):
        node_name = bus_volt_ph.node[i].split('"')[1]
        dss.Circuit.SetActiveBus(node_name)
        nodes = np.array(dss.Bus.Nodes())
        idx = np.where(nodes == ph)[0][0]
        voltage = dss.Bus.puVmagAngle()[idx*2]
        # print(nodes, idx, voltage)
        bus_volt_ph.loc[i, 'Voltage_dss'] = voltage
        
    return bus_volt_ph


if __name__ == '__main__':
    
    
    basedir_glm = '..\\cimhub_converted\\'
    feeder_name = 'South_D1_Alburgh'
    feeder_glm =  feeder_name + '_clean.glm'
    dir_for_glm = basedir_glm + '\\'+ feeder_glm 
    
    basedir_dss = ''
    feeder_name = 'South_D1_Alburgh'
    feeder_dss = basedir_dss + feeder_name
    
    glm_lines = glmanip.read(dir_for_glm,basedir_glm,buf=[])
    [model,clock,directives,modules,classes] = glmanip.parse(glm_lines)
    
    print('Reading GridLAB-D Voltages ....')
    gld_volts = pd.read_csv(basedir_glm + 'test_' + feeder_name + '_volt.csv', skiprows=1, header=0) 
    [bus_A, bus_B, bus_C] =  get_gld_voltages(gld_volts, model['node'])
    
    

    print('Running OpenDSS Model ....')
    dss.Command('Redirect ../{}/Master_with_tpx.dss'.format(feeder_dss))
    dss.Command('Compile ../{}/Master_with_tpx.dss'.format(feeder_dss))
    k=dss.Command("Calcv")
    dss.Solution.Solve() 
    
    print('Reading OpenDSS Voltages ....')
    bus_A = get_dss_voltage_by_phase(dss, 1, bus_A)
    bus_B = get_dss_voltage_by_phase(dss, 2, bus_B)
    bus_C = get_dss_voltage_by_phase(dss, 3, bus_C)
    
    bus_A_diff = bus_A.Voltage_glm.values - bus_A.Voltage_dss.values
    bus_B_diff = bus_B.Voltage_glm.values - bus_B.Voltage_dss.values
    bus_C_diff = bus_C.Voltage_glm.values - bus_C.Voltage_dss.values
    
    
    
    fig, ax = plt.subplots(3, figsize=(10, 8)) 
    
    ax[0].set_ylabel('Voltages - Phase A', color = 'black') 
    ax[0].scatter(range(len(bus_A)), bus_A.Voltage_glm.values, s = 10, label='GridLAB-D')
    ax[0].scatter(range(len(bus_A)), bus_A.Voltage_dss.values, s = 10, label='OpenDSS')
    ax1 = ax[0].twinx() 
    ax1.set_ylabel('Voltage Error (p.u)', color = 'red') 
    ax1.plot(range(len(bus_A)), bus_A_diff, 'r-.', linewidth=0.25) 
    ax[0].legend(loc='upper left')
    ax1.grid()
    
    ax[1].set_ylabel('Voltages - Phase B', color = 'black') 
    ax[1].scatter(range(len(bus_B)), bus_B.Voltage_glm.values, s = 10, label='GridLAB-D')
    ax[1].scatter(range(len(bus_B)), bus_B.Voltage_dss.values, s = 10, label='OpenDSS')
    ax2 = ax[1].twinx() 
    ax2.set_ylabel('Voltage Error (p.u)', color = 'red') 
    ax2.plot(range(len(bus_B)), bus_B_diff, 'r-.', linewidth=0.25) 
    ax[1].legend(loc='upper left')
    ax2.grid()
    
    
    ax[2].set_ylabel('Voltages - Phase C', color = 'black') 
    ax[2].scatter(range(len(bus_C)), bus_C.Voltage_glm.values, s = 10, label='GridLAB-D')
    ax[2].scatter(range(len(bus_C)), bus_C.Voltage_dss.values, s = 10, label='OpenDSS')
    ax3 = ax[2].twinx() 
    ax3.set_ylabel('Voltage Error (p.u)', color = 'red') 
    ax3.plot(range(len(bus_C)), bus_C_diff, 'r-.', linewidth=0.25) 
    ax[2].legend(loc='upper left')
    ax3.grid()
    

    
    
    
    
    
    