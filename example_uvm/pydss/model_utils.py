import copy
import random
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

class ModelUtil:

    def __init__(self, dss):
        self.bus_info = {}
        self.dss = dss
        self.dss.Topology.First()
        self.sourcebus = self.dss.CktElement.BusNames()[0].split('.')[0].upper()
        coor_df = pd.read_csv('nodecoords.csv', header=None)
        bus_coor = {}
        for i in range(len(coor_df)):
            bus_name = coor_df.iloc[i, 0].upper()
            x_coor = coor_df.iloc[i, 1]
            y_coor = coor_df.iloc[i, 2]
            bus_coor[bus_name] = {'x': x_coor, 'y': y_coor}
        print('Total buses: {}'.format(len(dss.Circuit.AllBusNames())))
        count = 0
        for bus in dss.Circuit.AllBusNames():
            self.dss.Circuit.SetActiveBus(bus)
            count += len(self.dss.Bus.Nodes())
            self.bus_info[bus.upper()] = {'nodes': self.dss.Bus.Nodes(), 'basekV': self.dss.Bus.kVBase(), 'loc': []}
            if bus.upper() in bus_coor:
                loc = [bus_coor[bus.upper()]['x'], bus_coor[bus.upper()]['y']]
                self.bus_info[bus.upper()]['loc'] = loc

        self.lines_df = self.dss.utils.lines_to_dataframe()
        self.branch_info = {}
        for ind in self.lines_df.index:
            bus1 = self.lines_df['Bus1'][ind].split('.')[0].upper()
            bus2 = self.lines_df['Bus2'][ind].split('.')[0].upper()
            self.branch_info[ind] = {'bus1': bus1, 'bus2': bus2}
        self.xfmrs_df = self.dss.utils.transformers_to_dataframe()
        self.transformer = {}
        
        with open('bus_info_temp.json', 'w') as f:
            json.dump(self.bus_info, f)
            
            
    def find_network_graph(self):
        flag = self.dss.Topology.First()
        G = nx.Graph()
        count = 0
        power_delivery_elements = []
        while flag > 0:
            # print(self.dss.Topology.BranchName())
            # print(self.dss.CktElement.BusNames())
            power_delivery_elements.append(self.dss.Topology.BranchName().split('.')[0])
            bus1 = self.dss.CktElement.BusNames()[0].split('.')[0].upper()
            bus2 = self.dss.CktElement.BusNames()[1].split('.')[0].upper()
            # if bus1 != self.sourcebus:
            
            G.add_edge(bus1, bus2)
            if 'Transformer' in self.dss.Topology.BranchName():
                self.branch_info[self.dss.Topology.BranchName()] = {'bus1': bus1, 'bus2': bus2}
                self.transformer[self.dss.Topology.BranchName()] = {}
                self.transformer[self.dss.Topology.BranchName()]['bus1'] = bus1
                self.transformer[self.dss.Topology.BranchName()]['bus2'] = bus2
                self.transformer[self.dss.Topology.BranchName()]['sec_voltage'] = self.bus_info[bus2]['basekV']
                self.transformer[self.dss.Topology.BranchName()]['phases'] = self.bus_info[bus2]['nodes']
            if 'Reactor' in self.dss.Topology.BranchName():
                self.branch_info[self.dss.Topology.BranchName()] = {'bus1': bus1, 'bus2': bus2}
            # if 'Line' in self.dss.Topology.BranchName():
            #     self.branch_info[self.dss.Topology.BranchName()] = {'bus1': bus1, 'bus2': bus2}
            count += 1
            # print(self.dss.Topology.BranchName())
            flag = self.dss.Topology.Next()
        print('Edges: {} and Nodes: {}'.format(G.number_of_edges(), G.number_of_nodes()))
        print('Total PDEs: {}'.format(count))
        print('Types of Elements: ', set(power_delivery_elements))
        return G

    def find_triplex_nodes(self):
        G = self.find_network_graph()
        idx = 0
        for xfmr in self.transformer:
            # Check only for service transformers
            G_new = copy.deepcopy(G)
            if self.transformer[xfmr]['sec_voltage'] < 0.2:
                # G_new = copy.deepcopy(G)
                G_new.remove_edge(self.transformer[xfmr]['bus1'], self.transformer[xfmr]['bus2'])
                ancestor_nodes = nx.ancestors(G_new, self.transformer[xfmr]['bus2'])
                self.transformer[xfmr]['triplex_nodes'] = [self.transformer[xfmr]['bus2']] + list(ancestor_nodes)
                idx += 1
                # sp_graph = list(nx.connected_components(G_new))
                # for k in sp_graph:
                #     if self.sourcebus not in k:
                #         area = k
                #         break
                # self.transformer[xfmr]['triplex_nodes'] = list(area)
                # for bus in area:
                #     # print(len(area))
                #     self.transformer[xfmr]['triplex_nodes'] += bus

        with open('xfmrs_info_temp.json', 'w') as f:
            json.dump(self.transformer, f)
        
        
    def populate_loads(self, xfmrs):
        load_f = open('Loads.dss', 'w')
        idx = 1
        phase = {'a': '.1', 'b': '.2', 'c': '.3'}
        for xfmr in xfmrs:
            try:
                name = xfmr.split('.')[1]
                # Add loads only in the secondary of transformer with service-level voltage
                kV = self.xfmrs_df.loc[name]['kV']
                bus = xfmrs[xfmr]['bus2']  #phase[name[-1]]
                phases = xfmrs[xfmr]['phases']
                if kV < 0.2:
                    bus_with_ph = bus + '.1.2'
                    kW = random.random() * 5
                    load_f.write('New Load.ldtpx_' + str(idx) + ' bus1=' + bus_with_ph + ' Phases=2 kV=' +
                                 str(0.208) + ' kW=' + str(kW) + ' pf=0.88 Vmin=0.75 Vmax=1.075' + '\n')
                    idx += 1
                elif kV > 0.2 and kV < 0.5:
                    ph_len = len(phases)
                    bus_with_ph = bus + '.' + ('.'.join(str(x) for x in phases))
                    kW = random.random() * 10
                    load_f.write('New Load.ldpri_' + str(idx) + ' bus1=' + bus_with_ph + ' Phases=' + str(ph_len) +' kV=' +
                                 str(round(kV*1.732, 3)) + ' kW=' + str(kW) + ' pf=0.90 Vmin=0.75 Vmax=1.075' + '\n')
                    idx += 1
            except:
                pass
        load_f.close()

    def grid_voltage_profile(self):
        node_names = self.dss.Circuit.AllNodeNames()
        nodeA_names = []
        nodeB_names = []
        nodeC_names = []
        for node in node_names:
            if ".1" in node:
                nodeA_names.append(node)
            elif ".2" in node:
                nodeB_names.append(node)
            elif ".3" in node:
                nodeC_names.append(node)

        bus_voltages = {}
        bus_A = []
        bus_B = []
        bus_C = []
        phases = [1, 2, 3]
        for p in phases:
            for idx, voltage in enumerate(self.dss.Circuit.AllNodeVmagPUByPhase(p)):
                if p == 1:
                    bus_A.append(voltage)
                    bus_voltages[nodeA_names[idx]] = voltage
                elif p == 2:
                    bus_B.append(voltage)
                    bus_voltages[nodeB_names[idx]] = voltage
                elif p == 3:
                    bus_C.append(voltage)
                    bus_voltages[nodeC_names[idx]] = voltage

        # Min, Max voltage and profile plot
        print('\n..........Voltage Min-Max.............')
        print(max(bus_A), max(bus_B), max(bus_C))
        print(min(bus_A), min(bus_B), min(bus_C))
        plt.scatter(range(len(bus_A)), bus_A)
        plt.scatter(range(len(bus_B)), bus_B)
        plt.scatter(range(len(bus_C)), bus_C)
        nodes = max(len(bus_B), len(bus_A), len(bus_C))

        # plt.ylim([0.8, 1.1])
        plt.xlabel('Bus Index')
        plt.ylabel('Voltage (p.u.)')
        plt.legend(['Phase-A', 'Phase-B', 'Phase-C'])
        plt.plot(np.ones(nodes) * 1.05, 'r--')
        plt.plot(np.ones(nodes) * 0.95, 'r--')
        plt.show()

        # Extract line flows/cuurents. Example is shown for a line connected to source bus
        self.dss.Topology.First()
        self.dss.Topology.Next()
        line_flow_sensors = [self.dss.Topology.BranchName().split('.')[1]]
        for line in line_flow_sensors:
            print('\n..........Substation flow from {}.............'.format(line))
            element = 'Line.' + line
            self.dss.Circuit.SetActiveElement(element)
            print(complex(self.dss.CktElement.Powers()[0], self.dss.CktElement.Powers()[1]))
            print(complex(self.dss.CktElement.Powers()[2], self.dss.CktElement.Powers()[3]))
            print(complex(self.dss.CktElement.Powers()[4], self.dss.CktElement.Powers()[5]))

    def voltage_violations_check(self):
        nodeA_voltages = self.dss.Circuit.AllNodeVmagPUByPhase(1)
        nodeB_voltages = self.dss.Circuit.AllNodeVmagPUByPhase(2)
        nodeC_voltages = self.dss.Circuit.AllNodeVmagPUByPhase(3)
        vmax = [max(nodeA_voltages), max(nodeB_voltages), max(nodeC_voltages)]
        violation = 0
        if max(vmax) > 1.05:
            violation = 1

        return violation

    def plot_circuit(self):
        G = self.find_network_graph()
        for branch in self.branch_info:
            try:
                point1 = self.bus_info[self.branch_info[branch]['bus1']]['loc']
                point2 = self.bus_info[self.branch_info[branch]['bus2']]['loc']
                bus1 = self.branch_info[branch]['bus1']
                bus2 = self.branch_info[branch]['bus2']
                x_values = [point1[0], point2[0]]
                y_values = [point1[1], point2[1]]
                e = (bus1, bus2)
                if G.has_edge(*e):
                    if 'Transformer' not in branch:
                        plt.plot(x_values, y_values, 'k-')
                    else:
                        plt.plot(x_values, y_values, 'g-')
                else:
                    # print(branch)
                    plt.plot(x_values, y_values, 'r-')
            except:
                pass
        plt.plot(self.bus_info[self.sourcebus]['loc'][0], self.bus_info[self.sourcebus]['loc'][1], 'bs')
        plt.axis('off')
        plt.show()

    def remove_isolated_circuits(self, feeder):
        import os
        print(os.getcwd())
        # f = open("../South_D1_Alburgh/South_D1_Alburgh_Isolated.txt", "r")
        isolated_elements = {'Line': [], 'Transformer': [], 'Reactor': []}
        isolated_txt = '../{}/{}_Isolated.txt'.format(feeder, feeder)
        with open(isolated_txt, mode='r') as infile:
            # change this number based on txt file. This shows how many lines to skip before acting on the file
            for i in range(70):
                next(infile)

            for i in range(152):
                line = infile.readline()
                row = line.split()
                if 3 > len(row) > 0:
                    element = row[1].split('.')
                    isolated_elements[element[0]].append(element[1].upper())
                if '(Lexical' in row:
                    break

        lines_to_write = []
        with open('../{}/Line.dss'.format(feeder), mode='r') as infile:
            lines = infile.readlines()
            index = 0
            while index < len(lines):
                line = lines[index]
                row = line.split()
                if 'New' in row[0]:
                    if row[1].split('.')[1].upper() in isolated_elements['Line']:
                        lines_to_write.append('!' + line)
                        line = lines[index + 1]
                        lines_to_write.append('!' + line)
                    else:
                        lines_to_write.append(line)
                        line = lines[index + 1]
                        lines_to_write.append(line)
                index += 2

        with open('../{}/Line_new.dss'.format(feeder), 'w') as new_file:
            # Write each line to the new file
            for line in lines_to_write:
                new_file.write(line)

        xfmrs_to_write = []
        with open('../{}/Transformer.dss'.format(feeder), mode='r') as infile:
            lines = infile.readlines()
            index = 0
            while index < len(lines):
                line = lines[index]
                row = line.split()
                if 'New' in row[0]:
                    if row[1].split('.')[1].upper() in isolated_elements['Transformer']:
                        xfmrs_to_write.append('!' + line)
                        line = lines[index + 1]
                        xfmrs_to_write.append('!' + line)
                        line = lines[index + 2]
                        xfmrs_to_write.append('!' + line)
                    else:
                        xfmrs_to_write.append(line)
                        line = lines[index + 1]
                        xfmrs_to_write.append(line)
                        line = lines[index + 2]
                        xfmrs_to_write.append(line)
                index += 3

        with open('../{}/Transformer_new.dss'.format(feeder), 'w') as new_file:
            # Write each line to the new file
            for line in xfmrs_to_write:
                new_file.write(line)
