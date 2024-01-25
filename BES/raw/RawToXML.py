# Copyright (C) 2022-2023 Battelle Memorial Institute
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  10 13:34:29 2023

@author: wang109
"""
# translates raw XML (PSLF/PSSE) to CIM XML
#
# using Python 3 XML module as documented at:
#   https://docs.python.org/3/library/xml.etree.elementtree.html
# CIMHub uses lxml:
#   from lxml import etree
#   from lxml.etree import Element, ElementTree, QName

import uuid
import os
import re
import numpy as np
import pandas as pd
from lxml import etree as et
import scipy.constants
import math
import sys

#%% 
def getStartEndLinesNo(fileName, stringbegin, stringend):   
  startLine = 0
  endLine = 0
  f = open(fileName,'r')
  lines = f.readlines()
  f.close()  
  for i in range(len(lines)):
    line = lines[i]
    linesplit = [x.strip() for x in line.strip().split(',')]
    if len(linesplit) > 1 :
      if linesplit[1] == stringbegin:
        startLine = i
      if linesplit[0] == stringend:
        endLine = i
    else:
      if linesplit[0] == stringend:
        endLine = i
  if startLine != 0:
    for j in range(10):
      line = lines[startLine+j+1]
      if line[0] !='@':
        startLine = startLine+j
        break
      else:
        print('skip: ', line)
  return [startLine , endLine]

def loadRaw(rawpath, rawname, savetocsv=False): 
  dflist = []
  filename = rawpath+rawname
  if sys.platform == 'win32':
    df_0 = pd.read_csv(filename, header=None, sep='\r\n') 
  else:
    df_0 = pd.read_csv(filename, header=None, sep='\n') 
  lineskip = 0
  
  #%%
  stringbegin = 'BEGIN BUS DATA'
  stringend = '0 / END OF BUS DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['BusNo', "\'BusName\'", 'NormKV', 
            'Unknown_1', 'AreaNum', 'ZoneNum', 
            'Unknown_2', 'PUVolt', 'Angle', 
            'Uplimit_1', 'Lowlimit_1', 'Uplimit_2', 'Lowlimit_2']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                  6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                  9: list_keys[9], 10: list_keys[10], 
                  11: list_keys[11], 12: list_keys[12]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'BusName\'"] = df_tmp2["\'BusName\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('BUS DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%%
  stringbegin = 'BEGIN LOAD DATA'
  stringend = '0 / END OF LOAD DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', "\'ID\'", 'STAT', 
            'AreaNum', 'ZoneNum', 'PL', 
            'QL', 'IP', 'IQ', 
            'YP', 'YQ', 'OWNER', 
            'SCALE', 'INTRPT', 'DGENP',
            'DGENQ', 'DGENF']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                  6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                  9: list_keys[9], 10: list_keys[10], 11: list_keys[11], 
                  12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                  15: list_keys[15], 16: list_keys[16]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'ID\'"] = df_tmp2["\'ID\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('LOAD DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
    
  #%%
  stringbegin = 'BEGIN FIXED SHUNT DATA'
  stringend = '0 / END OF FIXED SHUNT DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', "\'ID\'", 'STATUS', 'GL', 'BL']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'ID\'"] = df_tmp2["\'ID\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('FIXED SHUNT DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
    
  #%%
  stringbegin = 'BEGIN GENERATOR DATA'
  stringend = '0 / END OF GENERATOR DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', "\'ID\'", 'PG', 
            'QG', 'QT', 'QB', 
            'VS', 'IREG', 'MBASE', 
            'ZR', 'ZX', 'RT', 
            'XT', 'GTAP', 'STAT',
            'RMPCT', 'PT', 'PB',
            'O1', 'F1', 'O2', 
            'F2', 'O3', 'F3',
            'O4', 'F4', 'WMOD',
            'WPF']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                  6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                  9: list_keys[9], 10: list_keys[10], 11: list_keys[11], 
                  12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                  15: list_keys[15], 16: list_keys[16], 17: list_keys[17],
                  18: list_keys[18], 19: list_keys[19], 20: list_keys[20],
                  21: list_keys[21], 22: list_keys[22], 23: list_keys[23],
                  24: list_keys[24], 25: list_keys[25], 26: list_keys[26],
                  27: list_keys[27]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'ID\'"] = df_tmp2["\'ID\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('GENERATOR DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
    
  #%%
  stringbegin = 'BEGIN BRANCH DATA'
  stringend = '0 / END OF BRANCH DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'J', "\'CKT\'", 'R', 'X', 'B', 
             'Unknown_1', 'Unknown_2', 'Unknown_3', 'Unknown_4', 
             'Unknown_5', 'Unknown_6', 'Unknown_7', 'Unknown_8', 
             'Unknown_9', 'Unknown_10', 'Unknown_11', 'Unknown_12', 
             'Unknown_13', 'Unknown_14', 'Unknown_15', 'Unknown_16', 
             'Unknown_17', 'Unknown_18', 'Unknown_19', 'Unknown_20', 
             'Unknown_21', 'Unknown_22', 'Unknown_23', 'Unknown_24', 
             'Unknown_25', 'Unknown_26', 'Unknown_27', 'Unknown_28']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4], 5: list_keys[5],
                  6: list_keys[6], 7: list_keys[7], 8: list_keys[8],
                  9: list_keys[9], 10: list_keys[10], 11: list_keys[11],
                  12: list_keys[12], 13: list_keys[13], 14: list_keys[14],
                  15: list_keys[15], 16: list_keys[16], 17: list_keys[17],
                  18: list_keys[18], 19: list_keys[19], 20: list_keys[20],
                  21: list_keys[21], 22: list_keys[22], 23: list_keys[23],
                  24: list_keys[24], 25: list_keys[25], 26: list_keys[26],
                  27: list_keys[27], 28: list_keys[28], 29: list_keys[29],
                  30: list_keys[30], 31: list_keys[31], 32: list_keys[32], 
                  33: list_keys[33]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'CKT\'"] = df_tmp2["\'CKT\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('BRANCH DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%% 
  stringbegin = 'BEGIN TRANSFORMER DATA'
  stringend = '0 / END OF TRANSFORMER DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    
    list_keys_1 = ['I', 'J', 'K', "\'CKT\'", 'CW', 'CZ', 
             'CM', 'MAG1', 'MAG2', 'NMETR', "\'NAME\'", 'STAT',
             'O1', 'F1', 'O2', 'F2', 'O3', 'F3', 'O4', 'F4']
    list_keys_2 = ['R1-2', 'X1-2', 'SBASE1-2']
    list_keys_3 = ['WINDV1', 'NOMV1', 'WINDV2', 'NOMV2']
    
    len_tmp = int((endLine-startLine-1-lineskip)/4)
    df_tmp3 = pd.DataFrame(0, index=np.arange(len_tmp, dtype=object), columns=(list_keys_1+list_keys_2+list_keys_3))
    for i in range(len_tmp):
      for j in range(len(list_keys_1)):
        df_tmp3.iloc[i, j] = df_tmp2.iloc[4*i, j].strip()
      for j in range(len(list_keys_2)):
        df_tmp3.iloc[i, len(list_keys_1)+j] = df_tmp2.iloc[4*i+1, j].strip()
      df_tmp3.loc[i, 'WINDV1'] = df_tmp2.iloc[4*i+2, 0].strip()
      df_tmp3.loc[i, 'NOMV1'] = df_tmp2.iloc[4*i+2, 1].strip()
      df_tmp3.loc[i, 'WINDV2'] = df_tmp2.iloc[4*i+3, 0].strip()
      df_tmp3.loc[i, 'NOMV2'] = df_tmp2.iloc[4*i+3, 1].strip()

    df_tmp3["\'CKT\'"] = df_tmp3["\'CKT\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
    df_tmp3["\'NAME\'"] = df_tmp3["\'NAME\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
    
    print('TRANSFORMER DATA LOADED')
    if len(df_tmp3)>0:
      print(df_tmp3)
      dflist.append(df_tmp3)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%%
  stringbegin = 'BEGIN AREA DATA'
  stringend = '0 / END OF AREA DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'ISW', 'PDES', 'PTOL', "\'ARNAME\'"]
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'ARNAME\'"] = df_tmp2["\'ARNAME\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('AREA DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%%
  stringbegin = 'BEGIN ZONE DATA'
  stringend = '0 / END OF ZONE DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', "\'ZONAME\'"]
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'ZONAME\'"] = df_tmp2["\'ZONAME\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('ZONE DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')

  #%%
  stringbegin = 'BEGIN OWNER DATA'
  stringend = '0 / END OF OWNER DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', "\'OWNAME\'"]
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'OWNAME\'"] = df_tmp2["\'OWNAME\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('OWNER DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')

  #%%
  stringbegin = 'BEGIN SWITCHED SHUNT DATA'
  stringend = '0 / END OF SWITCHED SHUNT DATA'
  [startLine, endLine] = getStartEndLinesNo(filename, stringbegin, stringend)
  if startLine!=0 and endLine !=0:
    df_tmp = df_0.loc[startLine+1+lineskip : endLine-1].reset_index()
    df_tmp2 = df_tmp[0].str.split(r",", expand=True)
    if len(df_tmp2)>0:
      list_keys = ['I', 'MODSW', 'ADJM', 'ST', 'VSWHI', 'VSWLO', 
            'SWREG', 'RMPCT', "\'RMIDNT\'", 'BINIT', 'N1', 'B1']
      df_tmp2.rename(columns={0: list_keys[0], 1: list_keys[1], 2: list_keys[2], 
                  3: list_keys[3], 4: list_keys[4], 5: list_keys[5], 
                  6: list_keys[6], 7: list_keys[7], 8: list_keys[8], 
                  9: list_keys[9], 10: list_keys[10], 11: list_keys[11]}, inplace=True)
      df_tmp2 = df_tmp2.applymap(lambda x: x.strip() if isinstance(x, str) else x)
      df_tmp2["\'RMIDNT\'"] = df_tmp2["\'RMIDNT\'"].apply(lambda x: x.replace("\'", "").strip() if isinstance(x, str) else x)
      print('SWITCHED SHUNT DATA LOADED')
      print(df_tmp2)
      dflist.append(df_tmp2)
    else:
      dflist.append(df_tmp2)
      print('EMPTY section')
  
  #%%
  if savetocsv:
    for i in range(len(dflist)):
      if not dflist[i].empty:
        dflist[i].to_csv(rawpath+'Section'+str(i)+'Data.csv')
    
  return dflist

def convertXML(dflist):
  root = et.Element('root')
  list_subelement = ['BUSDATA', 'LOADDATA', 'FIXEDSHUNTDATA', 
             'GENERATORDATA', 'BRANCHDATA', 'TRANSFORMERDATA', 
             'AREADATA', 'ZONEDATA', 'OWNERDATA', 'SWITCHEDSHUNTDATA']
  
  for i in range(len(list_subelement)):
    df = dflist[i]
    if not df.empty:
      list_keys = df.columns.to_list()
      list_keys_clean = [x.replace("\'", "") for x in list_keys]
      list_keys_clean = [x.replace("-", "") for x in list_keys_clean]
      for row in df.iterrows():
        expression = list_subelement[i]+" = et.SubElement(root, '"+list_subelement[i]+"')"
        # print(expression)
        exec(expression)
        for j in range(len(list_keys)):
          key = list_keys[j]
          key_clean = list_keys_clean[j]
          expression = key_clean+" = et.SubElement("+list_subelement[i]+", '"+key_clean+"')"
          # print(expression)
          exec(expression)
        for j in range(len(list_keys)):
          key = list_keys[j]
          key_clean = list_keys_clean[j]
          expression = key_clean+".text = str(row[1][\""+key+"\"])"
          # print(expression)
          exec(expression)
  return root

#%%
if __name__ == "__main__":
  
  # user selected model
  for model in ["IEEE118", "WECC240"]:
  
    if model == "IEEE118": 
      rawpath = 'ieee118/'
      rawname = 'ieee-118-bus-v4.raw'
      xmlname = 'IEEE118.xml'
    elif model == "WECC240":
      rawpath = 'wecc240/'
      rawname = '240busWECC_2018_PSS.raw'
      xmlname = 'WECC240.xml'
    else:
      sys.exit("this model is not supported")
    
    #%% load raw file as DataFrame
    dflist = loadRaw(rawpath, rawname, savetocsv=False)
    
    #%% find unique id for load and generator
    tmp = [dflist[1].iloc[:, [1, 2]], dflist[3].iloc[:, [1, 2]]]
    tmp2 = pd.concat(tmp).reset_index()
    list_uni_id = []
    for i in range(len(tmp2)):
      id_tmp = str(tmp2.iloc[i, 1])+str(tmp2.iloc[i, 2])
      if id_tmp not in list_uni_id:
        list_uni_id.append(id_tmp)
    print('unique id length: ', len(list_uni_id), ' vs. length of load & generator data: ', len(tmp2))

    #%% write DataFrame as xml file
    root = convertXML(dflist)
    print(et.tostring(root, pretty_print=True).decode('utf-8'))
    tree = et.ElementTree(root)
    tree.write(rawpath+xmlname, pretty_print=True)
    
  