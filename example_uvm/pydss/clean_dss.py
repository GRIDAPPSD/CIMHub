# -*- coding: utf-8 -*-
"""

@author: Shiva Poudel  (shiva.poudel@pnnl.gov)
@author: Monish Mukherjee (monish.mukherjee@pnnl.gov)
Pacific Northwest National Laboratory
Copyright (C) 2018-2020 Battelle Memorial Institute
"""

import opendssdirect as dss

from model_utils import ModelUtil
import json
import copy
import pandas as pd
import sys 


def loadFile2(inputFile):
    file1 = open(inputFile,"r")
    documentLines=file1.readlines()
    file1.close()
    return documentLines


def replace_xfmr_triplex(documentLines):
    
    new_lines = 0    
    documentLines_new = []
    populate = True
    cnt = 0
    for i in range(len(documentLines)):
        if i%3 == 0 and ('!' not in documentLines[i]):
            documentLines_new.append(documentLines[i])
            line_idx = i+1
            # documentLines_new.append(documentLines[line_idx].replace(".0 ", " "))
            documentLines_new.append(documentLines[line_idx])

            line_idx = i+2
            bus2 = documentLines[line_idx].split("bus=")[1].split(" ")[0].split('.')[0]
            bus2_nodes = bus_info[bus2.upper()]['nodes']
            
            
            if populate and ('KV=0.12' in documentLines[line_idx].upper()) :
                if len(bus_info[bus2.upper()]['nodes']) < 2:
                    
                    

                    line = documentLines[line_idx].split(' ')
                    bus_data = line[2]
                    bus_data_wdg1 = bus_data[:-3]+'1.0'
                    bus_data_wdg2 = bus_data[:-3]+'0.2'
                    documentLines_new.append(documentLines[line_idx].replace(bus_data, bus_data_wdg1))                
                                            
                    line_wdg2 =  documentLines[line_idx].replace(bus_data, bus_data_wdg2)
                    line_wdg2 = line_wdg2.replace('wdg=2', 'wdg=3')
                    documentLines_new.append(line_wdg2)
                    documentLines_new[-4] = documentLines[i].replace('Windings=2', 'Windings=3')
     
                    documentLines_new[-4] = documentLines_new[-4].split('XHL=')[0] + 'Xhl=2.04  Xht=2.04  Xlt=1.36 \n'
       
                    cnt +=1
                
                    # if cnt > 2:
                    #     print(line)
                    #     populate = False
                else:
                    
                    new_line = documentLines[line_idx].replace(".0 ", " ")
                    new_line = new_line.replace("kV=0.12", "kV=0.277")
                    new_line = new_line.replace("kv=0.12", "kV=0.277")
                    new_line = new_line.replace("KV=0.12", "kV=0.277")
                    documentLines_new.append(new_line)


                    # print(new_line)
                    # if len(model_util.bus_info[bus2.upper()]['nodes']) == 3:
                    #     new_line = documentLines[line_idx].replace(".0 ", " ")
                    #     documentLines_new.append(new_line.replace("kV=0.120 ", "kV=0.277"))
                    # else:
                    #    documentLines_new.append(documentLines[line_idx])
            elif populate and ('conn=delta' in documentLines[line_idx]):
                new_line = documentLines[line_idx].replace("kV=0.207846", "kV=0.480")
                documentLines_new.append(new_line)
            else:
                ### making the secondary voltages of non delta transformers at .277
                new_line = documentLines[line_idx].replace("kV=0.480", "kV=0.277")
                new_line = new_line.replace("MaxTap=1.0000 MinTap=1.0000", " MaxTap=1.1000 MinTap=0.9000")
                documentLines_new.append(new_line)
        
    return documentLines_new


def writeDSSLines(input_file_name,documentLines):
    file1 = open(input_file_name,"w")
    file1.writelines(documentLines)
    file1.close()
    return input_file_name


if __name__ == '__main__':
    
    # feeder = 'BURTON_D1_HILL'
    feeder = 'South_D1_Alburgh'
    
    dss.Command('Redirect ../{}/Master.dss'.format(feeder))
    # dss.Command('Redirect ../{}/Transformer_new.dss'.format(feeder))
    dss.Command('Compile ../{}/Master.dss'.format(feeder))


    #### Loading This once to create the node info ####
    model_util_org = ModelUtil(dss)
    # model_util.remove_isolated_circuits(feeder)
    # model_util.grid_voltage_profile()
    
    global  bus_info 
    bus_info = model_util_org.bus_info
    del sys.modules["opendssdirect"]
       
    modify_xfmr = True
    xfmr_line = False
    

    
    if modify_xfmr: 
        
        ################ Adding Triplex Transformers in OpenDSS ##################
        transfromer_dss = '../{}/Transformer_new.dss'.format(feeder)
        documentLines=loadFile2(transfromer_dss)
        documentLines_xfmr = replace_xfmr_triplex(documentLines)
        transfromer_dss_new = transfromer_dss.replace('_new', '_new_with_triplex')                     
        new_xfmrs = writeDSSLines(transfromer_dss_new,documentLines_xfmr)
    
        dss.Command('Redirect ../{}/Master_new.dss'.format(feeder))
        dss.Command('Compile ../{}/Master_new.dss'.format(feeder))
        model_util_new = ModelUtil(dss)
        
        print('Finding Triplex nodes in the network')
        model_util_new.find_triplex_nodes()
        ######## Temporarily reading the file to save time ######## 
        with open('../{}/xfmrs_info_temp.json'.format(feeder), "r") as read_content: 
            model_util_new.transformer = (json.load(read_content))
        
        ################ Adding Triplex Lines in OpenDSS ##################
        all_tpx_node = []
        for xfmr in model_util_new.transformer:
            if 'triplex_nodes' in model_util_new.transformer[xfmr].keys():
                all_tpx_node = all_tpx_node + model_util_new.transformer[xfmr]['triplex_nodes']
    
        all_tpx_node = list(set(all_tpx_node))
        
        
        ################ Code to check for Reactor Data ##################
        # reactor_data =  pd.read_csv('../{}/Reactor.dss'.format(feeder), delimiter=' ', header=None)
        # for i in range(len(reactor_data)):
        #     bus1 = reactor_data[3][i].split("=")[1].split(".")[0].upper()
        #     bus2 = reactor_data[4][i].split("=")[1].split(".")[0].upper()   
        #     if (bus1 in all_tpx_node) or  (bus2  in all_tpx_node):
        #         print( reactor_data[1][i])
        
        print('Updating Triplex lines in the network')
        line_data =  pd.read_csv('../{}/Line_new.dss'.format(feeder), delimiter=' ', header=None)
        line_data_new = copy.deepcopy(line_data)
        mod_line_idx = 0

        for i in range(len(line_data)):
            
            if '!' not in line_data[0][i]:
                bus1 = line_data[3][i].split('.')[0].upper()
                bus2 = line_data[5][i].split('.')[0].upper()
                
                # if line_data[2][i] !=  'Bus1=' or line_data[4][i] != 'Bus2=':
                #     print(line_data[1][i])
                
                if (bus1 in all_tpx_node) or  (bus2  in all_tpx_node):
                    # line_data_new[0][i] = '!' + line_data[0][i]
                    line_data_new.loc[i,3] = bus1 + '.1.2'
                    line_data_new.loc[i,5]= bus2 + '.1.2'
                    line_data_new.loc[i,11] = '4/0Triplex'
                    mod_line_idx += 1
                    # break
                
        print("{} of the lines modified to Triplex".format(mod_line_idx))
        line_data_new.to_csv('../{}/Line_new_with_triplex.dss'.format(feeder), sep=' ', header=None, index=False)
    
    
    
    print('Populating fake loads in the network')
    model_util_new.populate_loads(model_util_new.transformer)
    # dss.run_command('Redirect ../{}/Transformer_new_v1.dss'.format(feeder))
    # dss.run_command('Redirect ../{}/Loads.dss'.format(feeder))
    
    
    del sys.modules["opendssdirect"]
    dss.Command('Redirect ../{}/Master_with_tpx.dss'.format(feeder))
    dss.Command('Compile ../{}/Master_with_tpx.dss'.format(feeder))
    model_util_with_tpx = ModelUtil(dss)
    # model_util_with_tpx.plot_circuit()
    k=dss.Command("Calcv")
    dss.Solution.Solve() 
    model_util_with_tpx.grid_voltage_profile()