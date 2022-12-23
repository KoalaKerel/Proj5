# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 11:35:22 2022

@author: damon
"""
import streamlit as sl
import numpy as np
import pandas as pd
from PIL import Image

if sl.session_state['noinput'] == True:
    sl.markdown("No schedule has been uploaded. Please return to the frontpage and upload a schedule.")
    noinputimg = Image.open('Geeninput.png')
    sl.image(noinputimg)
    
if sl.session_state['mismatch'] == True and sl.session_state['noinput']==False:
    sl.markdown("The uploaded schedule is not formatted correctly or does not match the uploaded data. Please check if both are correct.")
    badinputimg = Image.open('Fouteinput.png')
    sl.image(badinputimg)
    
if sl.session_state['mismatch'] == False and sl.session_state['noinput'] == False:
    sl.markdown("Here you can find the which route is being analysed. By default this will be routes 400 and 401. You can change the routes by uploading the necessary data below.")
    
    halt1 = False
    halt2 = False
    new_upload = sl.file_uploader('Data uploader', type=['xlsx'])
    
    if new_upload is None:
        usedata = sl.session_state['dienstdata']
        usedienst = sl.session_state['dienstregeling']
    if new_upload is not None:
        if (len(pd.ExcelFile(new_upload).sheet_names)<2) or (len(pd.ExcelFile(new_upload).sheet_names)>2):
            sl.header("The worksheets in the uploaded file are incorrect. Please refer to the instruction video.")
            sl.image(Image.open('Fouteinput.png'))
            halt1 = True
        else:
            usedata = pd.read_excel(new_upload, sheet_name=1)
            if (usedata.columns.values.tolist() == ['startlocatie', 'eindlocatie', 'min reistijd in min', 'max reistijd in min', 'afstand in meters', 'buslijn'])==False:
                sl.header("The uploaded format is incorrect on the Afstand matrix page. Please refer to the instruction video for the correct format.")
                sl.image(Image.open('Fouteinput.png'))
                halt1 = True
            else:
                halt1 = False
                sl.session_state['dienstdata2'] = pd.ExcelFile(new_upload)
            
            dienstlijnen = usedata.buslijn.unique()
            dienstlijnen = dienstlijnen[~np.isnan(dienstlijnen)]
            dienstlijnen = dienstlijnen.astype(int)
            
            
            usedata["activiteit"] = ""
            for i in range(len(usedata)):
                if np.isnan(usedata['buslijn'][i]) == False:
                    usedata.activiteit[i] = usedata.startlocatie[i] + usedata.eindlocatie[i] + str(int(usedata.buslijn[i]))
                if np.isnan(usedata['buslijn'][i]) == True:
                    usedata.activiteit[i] = usedata['startlocatie'][i]+usedata['eindlocatie'][i]+'m'
            usedata = usedata.append({'startlocatie':'', 'eindlocatie': '', 'min reistijd in min': 0, 'max reistijd in min': 0, 'afstand in meters': 0, 'buslijn': np.nan, 'activiteit':'idle'}, ignore_index=True)
            usedata = usedata.append({'startlocatie':'', 'eindlocatie': '', 'min reistijd in min': 0, 'max reistijd in min': 0, 'afstand in meters': 0, 'buslijn': np.nan, 'activiteit':'charge'}, ignore_index=True)
            usedienst = pd.read_excel(new_upload)
            if (usedienst.columns.values.tolist()[:4] == ['startlocatie', 'vertrektijd', 'eindlocatie', 'buslijn'])==False:
                sl.markdown(usedienst.columns.values.tolist()[:4])
                sl.header("The uploaded format is incorrect on the Dienstregeling page. Please refer to the instruction video for the correct format.")
                sl.image(Image.open('Fouteinput.png'))
                halt2 = True
            else:
                halt2 = False
            sl.session_state['dienstdata'] = usedata
            sl.session_state['dienstregeling'] = usedienst
    if halt1 == False and halt2 == False:
        activeroutes = usedata.buslijn.unique()
        activeroutes = activeroutes[~np.isnan(activeroutes)]
        
        if(all(x in sl.session_state['dienstdata'].activiteit.unique() for x in sl.session_state['datainput'].type.unique() ))==False:
            sl.session_state['wrongdata'] = True
            sl.image(Image.open('little error.png'))
            sl.markdown("Currently the data is not compatible with the shedule. The following routes are currently active:")
        else:
            sl.markdown("The following routes are currently active:")
            sl.session_state['wrongdata'] = False
        for i in activeroutes:
            sl.markdown(i)
            
        if len(usedienst.columns) > 4:
            usedienst.drop(columns=usedienst.columns[[4, 5]],  axis=1, inplace=True)
        sl.markdown("These routes are required to make the following trips:")
        sl.dataframe(usedienst)
    
