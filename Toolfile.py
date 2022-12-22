# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 11:47:56 2022

@author: damon
"""

import pandas as pd
import streamlit as sl
import numpy as np

sl.set_page_config(
    page_title="Startpagina Tool",
    page_icon="🚌",
)

sl.write("Welkom bij in de tool. Hier kunt u de planning controleren en diepere informatie krijgen. Hieronder vindt u een instructievideo die laat zien hoe de tool gebruikt kan worden.")


sl.video('https://youtu.be/dQw4w9WgXcQ') #PLACEHOLDER VIDEO!

planningdf = pd.DataFrame(columns=['buslijn']) #Om no input error te vermijden
if 'noinput' not in sl.session_state: 
    sl.session_state['noinput'] = True #Hiermee weet het om aan te geven op andere paginas als er geen input is
#Het uploaden van een planning
sl.write("Upload in dit vak de planning in de als een excelfile:")
planning = sl.file_uploader('', type=['xlsx'])
#Hiermee weten de andere paginas dat er een upload is, het update ook alleen de data wanneer er iets upload dus geen reset.

mismatch = True 
if planning is not None: 
    planningdf = pd.read_excel(planning)
    sl.session_state['datainput'] = planningdf
    sl.session_state['noinput'] = False
    if planningdf.columns.values.tolist() == ['startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 'buslijn', 'omloop nummer']:
        mismatch = False #De layout komt overeen
    else:
        mismatch = True #De layout komt niet overeen
    sl.session_state['mismatch'] =mismatch

if 'dienstregeling' not in sl.session_state:
    sl.session_state['dienstdata'] = pd.read_excel("Connexxion data - 2022-2023.xlsx", sheet_name=1) 
    sl.session_state['dienstregeling'] = pd.read_excel("Connexxion data - 2022-2023.xlsx")

    
#Hier kan de state of health door de gebruiker bepaald worden. Uit zichzelf staat er altijd al 90%
sl.write("Voer hieronder een percentage voor de state of health in:")
soc = sl.text_input('State of Health', '90')
sl.write('De huidige state of health is', soc, "%")
if float(soc) < 85:
    sl.markdown("Let op! Dit is een bijzonder lage waarde. Geadviseerd is 85% - 95%.")
if float(soc) > 95:
    sl.markdown("Let op! Dit is een bijzonder hoge waarde. Geadviseerd is 85% - 95%.")
sl.session_state['soc'] = float(soc)

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
            data.type[i] = "opladen"
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
