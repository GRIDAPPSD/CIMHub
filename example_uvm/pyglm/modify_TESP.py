# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 20:45:50 2024

@author: Monish Mukherjee (monish.mukherjee@pnnl.gov)
Pacific Northwest National Laboratory
"""

import networkx as nx
import copy
import math 
import glmanip
from create_json_for_networkx import createJson
import json

def gld_strict_name(val):
    """ Sanitizes a name for GridLAB-D publication to FNCS
    GridLAB-D name should not begin with a number, or contain '-' for FNCS

    Args:
        val (str): the input name

    Returns:
        str: val with all '-' replaced by '_', and any leading digit replaced by 'gld\_'
    """
    val = val.replace('"', '')
    if val[0].isdigit():
        val = "gld_" + val
    return val.replace('-', '_')

def modify_feeder_for_TESP(model, clock, G_feeder, pos_data=[]): 
    
     ############### Clock Formatting for TESP compatibility ###############
     if 'starttime' in clock:
         clock['timestamp'] = clock['starttime']
         del clock['starttime']
     
     
     ############### Subsation Formatting for TESP compatibility ###############
     if 'substation' in model:
         source_bus = list(model['substation'].keys())[0]
         model['node'][source_bus] = {'phases': model['substation'][source_bus]['phases'],
                                      'bustype': model['substation'][source_bus]['bustype'],
                                      'nominal_voltage': model['substation'][source_bus]['nominal_voltage']}
         del model['substation']
     
     
     ############### Transformer Formatting for TESP compatibility ###############
     ###### TESP Looks at Transformers for populating loads 
     ###### Having Banked Transformers may lead to errors 
     ###### Aggregating Banked Transformers for TESP
     
     xfmrs_mod =  copy.deepcopy(model['transformer'])
     xfmr_config_mod =  copy.deepcopy(model['transformer_configuration'])
     
     xfmr_connect_maps = {}; 
     for xfmr_od in model['transformer']:
         from_bus = model['transformer'][xfmr_od]['from']
         to_bus = model['transformer'][xfmr_od]['to']      
         phase  =  model['transformer'][xfmr_od]['phases']
         config_name = model['transformer'][xfmr_od]['configuration']
         
         connect_tuple = (from_bus, to_bus)
         if connect_tuple not in xfmr_connect_maps.keys():
             xfmr_connect_maps[connect_tuple] = xfmr_od
         else:
             prev_xfmr_name = xfmr_connect_maps[connect_tuple]
             ph_temp = phase + xfmrs_mod[prev_xfmr_name]['phases']
             xfmrs_mod[prev_xfmr_name]['phases'] = ''.join(sorted(set(ph_temp)))              
             
             xfmr_config = model['transformer_configuration'][config_name]
             prev_config_name = model['transformer'][prev_xfmr_name]['configuration']
             prev_xfmr_config = model['transformer_configuration'][config_name]
             
             for xfmr_cnfg_key in model['transformer_configuration'][prev_config_name]:
                 if 'power' in xfmr_cnfg_key:
                     power_val =  str(float(prev_xfmr_config[xfmr_cnfg_key]) + float(xfmr_config[xfmr_cnfg_key]))
                     xfmr_config_mod[prev_config_name][xfmr_cnfg_key] = power_val
             
             del xfmr_config_mod[config_name]
             del xfmrs_mod[xfmr_od]
             
             print('Aggregating Transformer with {} to Transformer {}'.format(xfmr_od, prev_xfmr_name))
     
     model['transformer_configuration'] = xfmr_config_mod      
     model['transformer'] = xfmrs_mod    

      
    ############### Load Formatting for TESP compatibility ###############
    ###### TESP Looks at Load objects for populating loads 
    ###### Modifying Load objects with constant_power definitions     
     loads_mod = copy.deepcopy(model['load'])      
     for ld_id in model['load']:
        for ld_key in model['load'][ld_id]:
            if 'base_power' in ld_key:
                ld_pf_key = ld_key.replace('base_power', 'power_pf')
                ld_powf_key = ld_key.replace('base_power', 'power_fraction')
                ct_pow_key = ld_key.replace('base_power', 'constant_power')
                
                kVA_ph = float(model['load'][ld_id][ld_key])                        
                pf_ph = float(model['load'][ld_id][ld_pf_key])
                Watt_ph = round(kVA_ph*pf_ph, 3)
                VAR_ph = round(math.sqrt(kVA_ph**2 - Watt_ph**2), 3)
   
                loads_mod[ld_id][ct_pow_key]  = str(Watt_ph) + '+' + str(VAR_ph) + 'j'
                del loads_mod[ld_id][ld_key]
                del loads_mod[ld_id][ld_pf_key]
                del loads_mod[ld_id][ld_powf_key]       
     
        
     tpx_loads_mod = copy.deepcopy(model['triplex_load'])
     tpx_lines_mod = copy.deepcopy(model['triplex_line'])
     tpx_nodes_mod = copy.deepcopy(model['triplex_node'])
     if 'triplex_meter' in model:
         tpx_meter_mod = copy.deepcopy(model['load'])
     else:
         tpx_meter_mod = {}
         
     ###### TESP Looks at Triplex Load objects for populating loads 
     ###### Modifying Triplex objects with power_12 definitions      
     for tpx_ld_id in model['triplex_load']:
         Watt_12 = 0; VAR_12 = 0
         parent = model['triplex_load'][tpx_ld_id]['parent']
         tpx_phase = model['triplex_load'][tpx_ld_id]['phases']
         for ld_key in model['triplex_load'][tpx_ld_id]:    
            if 'base_power' in ld_key:
                  pf_ph = float(model['triplex_load'][tpx_ld_id]['power_pf_1'])
                  VA_ph = float(model['triplex_load'][tpx_ld_id]['base_power_1'])
                  Watt_ph = VA_ph*pf_ph
                  VAR_ph = math.sqrt(VA_ph**2 - Watt_ph**2)
                  Watt_12 = Watt_12 + round(Watt_ph, 3)
                  VAR_12 = VAR_12 + round(VAR_ph, 3)
       

         new_tpx_line_name = new_tpx_line_name = 'span_' + tpx_ld_id.replace('"','')
         new_to_node_tpx_line = tpx_ld_id.replace('"','') + '_tn'
         tpx_lines_mod[new_tpx_line_name] = {'from': parent,
                                            'to':   new_to_node_tpx_line,
                                            'phases': tpx_phase,
                                            'continuous_rating_' + tpx_phase.strip('S'): str(200), 
                                            'emergency_rating_' + tpx_phase.strip('S'): str(250), 
                                            'length': '30',
                                            'configuration': '"tcon_4/0triplex_12"'}  
         tpx_meter_mod[new_to_node_tpx_line] = {'phases': tpx_phase,
                                                            'nominal_voltage': '120.0'}

         tpx_nodes_mod[tpx_ld_id] = {'parent': parent,
                                    'power_12': str(Watt_12) + '+' + str(VAR_12) + 'j',
                                    'phases': tpx_phase,
                                    'nominal_voltage': '120.0'}   
         del tpx_loads_mod[tpx_ld_id]
         
         ###### Adding coordinates to newly created meters for TESP Compatibility #### 
         if len(pos_data) >  0:
             parent_clean = gld_strict_name(parent) 
             new_to_node_tpx_line_clean = gld_strict_name(new_to_node_tpx_line) 
             pos_data[new_to_node_tpx_line_clean] = pos_data[parent_clean]

         
         
     
         
     model['load'] = loads_mod
     model['triplex_node'] = tpx_nodes_mod
     model['triplex_line'] = tpx_lines_mod
     model['triplex_meter'] = tpx_meter_mod
     model['triplex_load'] = tpx_loads_mod
     
     return model, clock
 
    
if __name__ == '__main__':
    
    
    basedir = '..\\cimhub_converted\\'
    feeder_name = 'South_D1_Alburgh'
    feeder_glm = feeder_name + '_clean_full.glm'
    dir_for_glm = basedir + '\\'+ feeder_glm 
    dir_for_symbols = basedir + '\\'+ feeder_glm 
    source_bus = "\"internalsouth_d1_alburgh\"";
    TESP_compatible = True
    
    glm_lines = glmanip.read(dir_for_glm,basedir,buf=[])
    [model,clock,directives,modules,classes] = glmanip.parse(glm_lines)
    
    feeder_network, pos_data  = createJson(feeder_name, model,clock,directives,modules,classes)
    G_feeder = nx.readwrite.json_graph.node_link_graph(feeder_network)
    
    model_tesp, clock_tesp =   modify_feeder_for_TESP(model, clock, G_feeder)
    ofn = basedir + feeder_glm.replace('run_', '').split('.glm')[0] + '_mod_tesp.glm'
    glmanip.write(ofn,model_tesp,clock_tesp,directives,modules,classes)
       
    ##################  TESP Compatibility  ####################
    if TESP_compatible: 
        model_tesp, clock_tesp =  modify_feeder_for_TESP(model, clock, G_feeder, pos_data)
        ofn_tesp = basedir + feeder_glm.replace('run_', '').split('.glm')[0] + '_mod_tesp_reduced.glm'
        glmanip.write(ofn_tesp,model_tesp,clock_tesp,directives,modules,classes)
      
    with open(basedir + feeder_name + '_mod_tesp_pos'+ '.json', 'w') as fp:
        json.dump(pos_data, fp)    
        
     
     