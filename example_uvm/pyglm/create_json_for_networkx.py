# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 13:16:45 2019

@author: monish.mukherjee
"""

import json
import numpy as np

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


def createJson(feeder_name, model,clock,directives,modules,classes, coords_data = []): 
    
    feeder = {}
    feeder['directed'] = bool(1)
    feeder['graph'] = {}
    feeder['links'] = []
    feeder['multigraph'] = bool(1)
    feeder['nodes'] = []
    
   
    #######################    Feeder Links   #################################
    Link_models = ['overhead_line','underground_line', 'triplex_line','regulator', 'fuse', 'recloser','switch', 'fuse','transformer', 'sectionalizer']
    for item in range(len(Link_models)):
        if Link_models[item] in model:
            for link_item in model[Link_models[item]]:
                if Link_models[item] == 'transformer' or Link_models[item] == 'regulator':
                    feeder['links'].append({'eclass': Link_models[item],
                                        'edata': model[Link_models[item]][link_item],
                                        'ename': link_item,
                                        'source': model[Link_models[item]][link_item]['from'],
                                        'target': model[Link_models[item]][link_item]['to'],
                                        "weight": 1,
                                        'Transformer': 'True'})
                elif Link_models[item] == 'switch' or Link_models[item] == 'fuse' or Link_models[item] == 'recloser' :
                    if model[Link_models[item]][link_item]['status'] == 'CLOSED':
                        feeder['links'].append({'eclass': Link_models[item],
                                            'edata': model[Link_models[item]][link_item],
                                            'ename': link_item,
                                            'source': model[Link_models[item]][link_item]['from'],
                                            'target': model[Link_models[item]][link_item]['to'],
                                            "weight": 2,
                                            'Transformer': 'False'})
                else:
                    # print(model[Link_models[item]][link_item], item, link_item)
                    feeder['links'].append({'eclass': Link_models[item],
                                        'edata': model[Link_models[item]][link_item],
                                        'ename': link_item,
                                        'source': model[Link_models[item]][link_item]['from'],
                                        'target': model[Link_models[item]][link_item]['to'],
                                        "weight":  float(model[Link_models[item]][link_item]['length']),                            
                                        'Transformer': 'False'})
                    
                
           
 
    ################## feeder nodes, triplex_node and  substation #############
    # node_models = ['node', 'meter', 'load', 'inverter_dyn']
    pos_data_json = {}
    node_models = ['node', 'triplex_node', 'triplex_load', 'capacitor', 'load', 'substation', 'meter']
    for it in range(len(node_models)):
        if node_models[it] in model.keys():
            for node in model[node_models[it]]:
                # print(node_models[it], it, node)
                feeder['nodes'].append({'id': node,
                                        'nclass': node_models[it],
                                        'ndata': {'voltage': (model[node_models[it]][node]['nominal_voltage'])}})
                node_key = node
                if 'parent' in model[node_models[it]][node].keys():
                    feeder['links'].append({'eclass': 'load-node',
                                            'edata': {},
                                            'ename': node + '_' + model[node_models[it]][node]['parent'],
                                            'source': model[node_models[it]][node]['parent'],
                                            'target': node,
                                            "weight": 2,
                                            'Transformer': 'False'})
                
                    node_key =  model[node_models[it]][node]['parent']
                if len(coords_data) >  0:
                    node_clean = gld_strict_name(node)
                    pos_data_json[node_clean] = (coords_data.loc[node_key.replace('"', '')]['x'], coords_data.loc[node_key.replace('"', '')]['y'])

    
    return feeder, pos_data_json
    
                 
                
    
    
