# -*- coding: utf-8 -*-
"""

@author: Monish Mukherjee (monish.mukherjee@pnnl.gov)
Pacific Northwest National Laboratory
Copyright (C) 2018-2020 Battelle Memorial Institute
"""

import glmanip
import pandas as pd
import numpy as np
import math
import random

import matplotlib.pyplot as plt
import os
import subprocess
import copy 
from create_json_for_networkx import createJson
import networkx as nx
import json

import modify_TESP

###############################################################################
################ Updating Trasformer Reactance and Resistances ################
###############################################################################
def clean_xfmr_impedance(xfmr_config):
    xfmr_config_new = copy.deepcopy(xfmr_config)
    for config_id in xfmr_config: 
        for key in xfmr_config[config_id]:
            if 'impedance' in key:
                value =  complex(xfmr_config[config_id][key])
                reac = abs(value.imag)
                res = abs(value.real)
                if reac ==0:
                    reac = 0.00001
                if res == 0:
                    res = 0.00001
                # xfmr_config_new[config_id][key] = "{:.5f}".format(res) + '+' + "{:.5f}".format(reac) +'j'          
                res_key = key.replace('impedance', 'resistance')
                reac_key = key.replace('impedance', 'reactance')
                xfmr_config_new[config_id][res_key] = "{:.5f}".format(res) 
                xfmr_config_new[config_id][reac_key] = "{:.5f}".format(reac) 
                del xfmr_config_new[config_id][key]
                
            if 'resistance' in key: 
                value =  float(xfmr_config[config_id][key])
                if value  == 0:
                    res = 0.00001
                    xfmr_config_new[config_id][key] = "{:.5f}".format(res)
            if 'reactance' in key: 
                value =  float(xfmr_config[config_id][key])
                if value  == 0:
                    reac = 0.00001
                    xfmr_config_new[config_id][key] = "{:.5f}".format(reac)   
                    
            secondar_volt = float(xfmr_config[config_id]['secondary_voltage'])
            if secondar_volt < 200:
                xfmr_config_new[config_id]['install_type'] = 'POLETOP'
            elif secondar_volt > 200 and secondar_volt < 500:
                xfmr_config_new[config_id]['install_type']  = 'PADMOUNT'
            else:
                xfmr_config_new[config_id]['install_type']  = 'VAULT' 
        
    return xfmr_config_new

###############################################################################
################# Cleaning_names of Line Configurations #######################
###############################################################################
def clean_line_configuration_name(line_config, oh_line_model):
    line_config_new = copy.deepcopy(line_config)
    oh_line_model_new = copy.deepcopy(oh_line_model)
   
    ### finding missing line_configurations ###
    line_configs_to_del = []
    for line_id in oh_line_model:
        line_config_id = oh_line_model[line_id]['configuration']
        if  '/' in line_config_id or '_' in line_config_id :

            new_line_config_id = line_config_id.replace('/', '_')
            new_line_config_id = new_line_config_id.replace('_', '')
            oh_line_model_new[line_id]['configuration'] = new_line_config_id
            
            line_config_dict = line_config[line_config_id]
            line_config_new[new_line_config_id] = line_config_dict
            line_configs_to_del.append(line_config_id)
     
    unique_line_configs_to_del = list(set(line_configs_to_del))       
    for config_id in unique_line_configs_to_del:
        del line_config_new[config_id]
        
    return line_config_new, oh_line_model_new
        
###############################################################################
############################ Get Feeder Cooridnates ###########################
###############################################################################
def node_coordinates_from_symbols(symbols_filename):
    print("Fetching Cooridniates from the symbols.json file")
    coords_data = {}
    with open(symbols_filename) as file:
        for line in file: 
            if 'name' in line: 
                line_data  = json.loads(line.replace(',\n', ''))
                if 'from' in line_data.keys(): 
                    coords_data[line_data['from']] = (line_data['x1'], line_data['y1']) 
                    coords_data[line_data['to']] = (line_data['x2'], line_data['y2']) 
                else: 
                    coords_data[line_data['name']] = (line_data['x1'], line_data['y1']) 

    data_df = pd.DataFrame.from_dict(coords_data, orient='index', columns=['x', 'y']) 
    
    return data_df

###############################################################################
############## Correct Triplex Phasing of the Feeder ##########################
###############################################################################
def correct_triplex_phasing(model_tpx_line, model_tpx_node, G_feeder):

    for line_id in model_tpx_line:
        old_ph = model_tpx_line[line_id]['phases']
        from_node = model_tpx_line[line_id]['from']
        to_node = model_tpx_line[line_id]['to']
        
        if old_ph == 'S':
            in_edge =  list(G_feeder.in_edges(from_node, data=True))
            while in_edge[0][2]['Transformer'] == 'False':
                new_from_node = in_edge[0][0]
                in_edge =  list(G_feeder.in_edges(new_from_node, data=True))
            
            new_ph = in_edge[0][2]['edata']['phases']
            model_tpx_line[line_id]['phases'] = new_ph
            model_tpx_node[from_node]['phases'] = new_ph
            model_tpx_node[to_node]['phases'] = new_ph
            
    return model_tpx_line, model_tpx_node
            

###############################################################################
############## Extract feeders from multi-feeder model ########################
###############################################################################
def remove_feeder_via_links(feeder_links, feeder_model, G_feeder):

    G_feeder_new = copy.deepcopy(G_feeder)
    
    for fd in feeder_links:       
        from_feeder = feeder_model['switch'][fd]['from']
        to_feeder = feeder_model['switch'][fd]['to']
        print("Removing Circuit buy Opening Swich between {}<--->{}".format(from_feeder, to_feeder))
        decendants = [to_feeder] + list((nx.descendants(G_feeder_new, to_feeder)))
        G_feeder_new_conn = nx.subgraph(G_feeder_new, decendants)
        
        ###### Removing node objects from the GridLAB model #######
        for nd_name, nd_ndata in G_feeder_new_conn.nodes.items():
            class_name = nd_ndata['nclass']
            if nd_name != to_feeder: 
                del feeder_model[class_name][nd_name]
                
        ###### Removing edge objects from the GridLAB model #######    
        for edge_name, edge_data in G_feeder_new_conn.edges.items():
                class_name = edge_data['eclass']
                ename = edge_data['ename']
                if class_name  !=  'load-node':
                    del feeder_model[class_name][ename]
            
    return feeder_model
       
if __name__ == '__main__':
    
    #basedir = r'C:\Users\mukh915\OneDrive - PNNL\PNNL\EWH_modelling\populationscripts\experiments\coSimulationExample\IEEE_123_feeder_0'
    basedir = '..\\cimhub_converted\\'
    feeder_name = 'South_D1_Alburgh'
    feeder_glm = 'run_' + feeder_name + '.glm'
    dir_for_glm = basedir + '\\'+ feeder_glm 
    dir_for_symbols = basedir + '\\'+ feeder_glm 
    source_bus = "\"internalsouth_d1_alburgh\"";
    TESP_compatible = True
    run_glm = True
    plot_voltage = True
    split_feeder = True   
        
        
    glm_lines = glmanip.read(dir_for_glm,basedir,buf=[])
    [model,clock,directives,modules,classes] = glmanip.parse(glm_lines)

    symbols_filename = basedir + feeder_name + '_symbols.json'
    coords_data_df = node_coordinates_from_symbols(symbols_filename)
    
    ##################### Cleaning Line Config Names ##########################
    ######### GridLAB-D has a charactere limit for names  # 
    ######### This codes loops shortens the line_configuration #
    line_config_new, oh_line_model_new = clean_line_configuration_name(model['line_configuration'], model['overhead_line'])
    
    model['line_configuration'] = line_config_new
    model['overhead_line'] = oh_line_model_new
    ###########################################################################  
    
    ################## Cleaning Transformer Impedances ########################
    ######### GridLAB-D doesn't like zero for impdenaces in transformers #
    xfmr_config_new = clean_xfmr_impedance(model['transformer_configuration'])
    model['transformer_configuration'] = xfmr_config_new
    
    ##### Adjusting votlages for DELTA configured transformers in OpenDSS #####
    for xfmr_id in model['transformer']:
        ph = model['transformer'][xfmr_id]['phases']
        config = model['transformer'][xfmr_id]['configuration']
        if len(ph) <= 2:
            sec_voltage = float(model['transformer_configuration'][config]['secondary_voltage'])
            if 475 < sec_voltage < 485:
                model['transformer_configuration'][config]['secondary_voltage'] ='277'
    ###########################################################################
            
    ##################### Udpating Regulator Taps ###########################
    for reg_cnfg_id in model['regulator_configuration']:
        for reg_cnfg_key in model['regulator_configuration'][reg_cnfg_id]:
            if 'tap_pos' in reg_cnfg_key:
                model['regulator_configuration'][reg_cnfg_id][reg_cnfg_key] = str(0)
                model['regulator_configuration'][reg_cnfg_id][reg_cnfg_key] = str(0)
    ###########################################################################             
                    
                    
    ##################### Adding Fault Check Object ###########################
    model['fault_check'] = {}
    model['fault_check']['island_checker'] = {'check_mode': 'ONCHANGE',
                                              'strictly_radial': 'false',
                                              'grid_association': 'true',
                                              'output_filename': 'outage_check.txt'}   
    ###########################################################################
    
    modules['powerflow']['line_limits'] = 'false'
    model['substation'][source_bus]['positive_sequence_voltage'] = model['substation'][source_bus]['nominal_voltage'] 
    ###########################################################################
        
    ########### Creating Network Graph from the GridLAB-D model ###############
    feeder_network, pos_data  = createJson(feeder_name, model,clock,directives,modules,classes, coords_data_df)
    G_feeder = nx.readwrite.json_graph.node_link_graph(feeder_network)
                
    ####################  Saving the Feeder Graph to Json  #####################
    Json_file = json.dumps(feeder_network, sort_keys=True, indent=4, separators=(',', ': '))    
    fp = open(basedir + feeder_name + '_networkx.json', 'w')
    print(Json_file, file=fp)
    fp.close()
    ###########################################################################
    
    
    ##################  Correcting Phasing of Triplex Lines  ###################
    ######### CIMHUB might not be to track phasing of complex triplex system #
    model_tpx_line, model_tpx_node = correct_triplex_phasing(model['triplex_line'], model['triplex_node'], G_feeder)
    model['triplex_line'] = model_tpx_line
    model['triplex_node'] = model_tpx_node      
    ###########################################################################
                
    
    ################## Writing Back the GridLAB-D Model ########################
    ofn_clean = basedir + feeder_glm.replace('run_', '').split('.glm')[0] + '_clean_full.glm'
    glmanip.write(ofn_clean,model,clock,directives,modules,classes)
   
     ##################  Removing Feeders ###################
    if split_feeder:
        feeder_1_link = '"swt_28-7-1a"'
        feeder_3_link  = '"swt_28-7-3a"'
        feeder_4_link  = '"swt_28-7-4a"'
        feeder_links_to_remove = [feeder_3_link, feeder_4_link] 
        model_new = remove_feeder_via_links(feeder_links_to_remove, model, G_feeder)
        ofn_clean = basedir + feeder_glm.replace('run_', '').split('.glm')[0] + '_clean_reduced.glm'
        glmanip.write(ofn_clean,model_new,clock,directives,modules,classes)    
            
    if run_glm:
        print('Trying GridLAB-D Simulation')
        curr_dir = os.getcwd()
        exp_dir = os.path.join(curr_dir, basedir)
        os.chdir(exp_dir)
        # p1 = subprocess.Popen(['gridlabd', feeder_name], creationflags = subprocess.CREATE_NEW_CONSOLE)
        p1 = subprocess.Popen(['gridlabd', ofn_clean], stdout=subprocess.PIPE)
        p1.wait()
        os.chdir(curr_dir)
        
    
    ########################### Plotting Voltages #############################
    if plot_voltage: 
        print('Plotting GridLAB-D Results ')
        volts = pd.read_csv(basedir + 'test_South_D1_Alburgh_volt.csv', skiprows=1, header=0)
        volts = volts.set_index('node_name')    
        
        bus_A = pd.DataFrame(columns =  ['node', 'Voltage'])
        bus_B = pd.DataFrame(columns =  ['node', 'Voltage'])
        bus_C = pd.DataFrame(columns =  ['node', 'Voltage'])
        
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
        
        print('\n..........Voltage Min-Max.............')
        plt.scatter(range(len(bus_A)), bus_A.Voltage.values)
        plt.scatter(range(len(bus_B)), bus_B.Voltage.values)
        plt.scatter(range(len(bus_C)), bus_C.Voltage.values)
        nodes = max(len(bus_B), len(bus_A), len(bus_C))

        # plt.ylim([0.8, 1.1])
        plt.xlabel('Bus Index')
        plt.ylabel('Voltage (p.u.)')
        plt.legend(['Phase-A', 'Phase-B', 'Phase-C'])
        plt.plot(np.ones(nodes) * 1.05, 'r--')
        plt.plot(np.ones(nodes) * 0.95, 'r--')
        plt.show()
        
    
    
    