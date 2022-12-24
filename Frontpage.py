# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 11:47:56 2022

@author: damon
"""

import pandas as pd
import streamlit as sl
import numpy as np
from PIL import Image

sl.set_page_config(
    page_title="Startpagina Tool",
    page_icon="🚌",
)

sl.write("Welcome to this tool for checking bus schedules. Below you will find a video instructing you on how to use this application.")


sl.video('https://youtu.be/SVFKbhT3If8') #PLACEHOLDER VIDEO!

planningdf = pd.DataFrame(columns=['buslijn']) #Om no input error te vermijden
if 'noinput' not in sl.session_state: 
    sl.session_state['noinput'] = True #Hiermee weet het om aan te geven op andere paginas als er geen input is
if 'mismatch' not in sl.session_state:
    sl.session_state['mismatch'] = False
if 'wrongdata' not in sl.session_state:
    sl.session_state['wrongdata']= False
if 'datainput' not in sl.session_state:
    sl.session_state['datainput'] = pd.read_excel('Empty Schedule.xlsx')
    sl.session_state['dienstdata2'] = pd.ExcelFile("Connexxion data - 2022-2023.xlsx")
#Het uploaden van een planning
sl.write("Please upload the excel file containing the bus schedule:")
planning = sl.file_uploader('Schedule uploader', type=['xlsx'])
#Hiermee weten de andere paginas dat er een upload is, het update ook alleen de data wanneer er iets upload dus geen reset.
if planning is not None: 
    planningdf = pd.read_excel(planning)
    sl.session_state['datainput'] = planningdf
    sl.session_state['noinput'] = False
    if planningdf.columns.values.tolist() == ['startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 'buslijn', 'omloop nummer']:
        mismatch = False #De layout komt overeen
    else:
        mismatch = True #De layout komt niet overeen
        sl.markdown("The format of the uploaded file does not match the requirements. Please watch the video above to learn more.")
        sl.image(Image.open('Fouteinput.png'))
    sl.session_state['mismatch'] =mismatch
    

dienstdata = pd.read_excel("Connexxion data - 2022-2023.xlsx", sheet_name=1)
dienstdata['activiteit'] = ''
for i in range(len(dienstdata)):
    if np.isnan(dienstdata['buslijn'][i])==False:
        dienstdata['activiteit'][i] = dienstdata['startlocatie'][i]+dienstdata['eindlocatie'][i]+str(dienstdata['buslijn'][i])[:-2]
    else:
        dienstdata['activiteit'][i] = dienstdata['startlocatie'][i]+dienstdata['eindlocatie'][i]+'m'
dienstdata = dienstdata.append({'startlocatie':'', 'eindlocatie': '', 'min reistijd in min': 0, 'max reistijd in min': 0, 'afstand in meters': 0, 'buslijn': np.nan, 'activiteit':'idle'}, ignore_index=True)
dienstdata = dienstdata.append({'startlocatie':'', 'eindlocatie': '', 'min reistijd in min': 0, 'max reistijd in min': 0, 'afstand in meters': 0, 'buslijn': np.nan, 'activiteit':'charge'}, ignore_index=True)
dienstregeling = pd.read_excel("Connexxion data - 2022-2023.xlsx")
if 'dienstregeling' not in sl.session_state:
    sl.session_state['dienstdata'] =  dienstdata
    sl.session_state['dienstregeling'] = dienstregeling
    sl.session_state['dienstdata2'] = pd.ExcelFile("Connexxion data - 2022-2023.xlsx")


    
#Hier kan de state of health door de gebruiker bepaald worden. Uit zichzelf staat er altijd al 90%
sl.write("Please input a percentage for the state of health:")
soc = sl.number_input('State of Health')


if 'soc' not in sl.session_state or soc == 0:
    sl.session_state['soc'] = 90
    soc = 90
elif int(soc) > 0:
    sl.session_state['soc'] = float(soc)
    
sl.write('The current state of health is ', str(sl.session_state['soc']), " %")
if float(soc) < 85:
    sl.markdown("Beware! This is a very low value. Recommended: 85% - 95%.")
if float(soc) > 95:
    sl.markdown("Beware! This is a very high value. Recommended:  85% - 95%.")

sl.write("Please enter how many kwh the bus uses per meter:")
verbruik = sl.number_input('Usage', format='%.4f')
if 'stroomverbruik' not in sl.session_state:
    sl.session_state['stroomverbruik'] = 0.00100
elif verbruik > 0:
    sl.session_state['stroomverbruik']=verbruik
sl.markdown("The current usage is " + str(sl.session_state['stroomverbruik']) + ' kwh per meter.')
    

if planning is not None and mismatch==False: 
    #Welke verschillende lijnen zitten er in de omloopplanning
    lijnen = planningdf.buslijn.unique()
    lijnen = lijnen[~np.isnan(lijnen)]
    if 'lijnen' not in sl.session_state:
        sl.session_state['lijnen'] = lijnen
    
    #Dataframe voorbereiden voor de andere paginas
    data = sl.session_state['datainput']
    #lijnen
    lijnen = sl.session_state['lijnen']
    #Het aanmaken van typen rit
    data["type"] = np.nan
    #Alle soorten ritten in kaart brengen
    for i in range(len(data)):
        if data.activiteit[i] == "idle":
            data.type[i] = "idle"
        if data.activiteit[i] == "opladen":
            data.type[i] = "charge"
        if data.activiteit[i] == "dienst rit":
            data.type[i] = data.startlocatie[i] + data.eindlocatie[i] + str(data.buslijn[i])[:-2]
        if data.activiteit[i] == "materiaal rit":
            data.type[i] = data.startlocatie[i] + data.eindlocatie[i] + "m"
    
    for i in range(len(data)):
        data['starttijd'][i] = str(data['starttijd'][i])
        data['eindtijd'][i] = str(data['eindtijd'][i])
    
    data['start_time'] = pd.to_datetime(data.starttijd)
    data['end_time'] = pd.to_datetime(data.eindtijd)
    for i in range(len(data)):
        data['start_time'][i] = data['start_time'][i].minute + 60 * data['start_time'][i].hour
        data['end_time'][i] = data['end_time'][i].minute + 60 * data['end_time'][i].hour
    data['tte'] = data.end_time - data.start_time
    for i in range(len(data)):
        if data['tte'][i]<0:
            data['tte'][i] = data['tte'][i] + 1440
        if data['start_time'][i]<300:
            data['start_time'][i] = data['start_time'][i] + 1440
        if data['end_time'][i]<300:
            data['end_time'][i] = data['end_time'][i] + 1440
        if data['buslijn'][i] not in lijnen:
            data['buslijn'][i] = ""
    

if (planning is not None) and (sl.session_state['mismatch'] == False):            
    if(all(x in sl.session_state['dienstdata'].activiteit.unique() for x in sl.session_state['datainput'].type.unique() ))==False:
        sl.session_state['wrongdata'] = True
    else:
        sl.session_state['wrongdata'] = False
